import os
import pandas as pd
import math
import arcpy.ddd
from dic_global_constants import *


def get_gis_point_layers():
    """ Creates point feature classes displ_field_coords (i.e. preEQ pixel coordinates) and displ_field_coords_postEQ
    (i.e. postEQ pixel coordinates and calculates the 3D displacement field.
    All attributes are re-attributed to the feature class displ_field_coords. """
    displ_field_coords = OUTPUT_GDB + '/displ_field_coords'
    displ_field_coords_postEQ = OUTPUT_GDB + '/displ_field_coords_postEQ'

    if CREATE_GIS_POINT_LAYERS == 1:
        if arcpy.Exists(displ_field_coords):
            arcpy.Delete_management(displ_field_coords)
        if arcpy.Exists(displ_field_coords_postEQ):
            arcpy.Delete_management(displ_field_coords_postEQ)
        arcpy.MakeXYEventLayer_management(DISPL_INPUT_TXT, 'Field1', 'Field2', 'displ_field_layer', EPSG)
        arcpy.CopyFeatures_management('displ_field_layer', displ_field_coords)
        arcpy.AlterField_management(displ_field_coords, 'Field1', 'x_coord', 'x_coord')
        arcpy.AlterField_management(displ_field_coords, 'Field2', 'y_coord', 'y_coord')
        arcpy.AlterField_management(displ_field_coords, 'Field3', 'x_offset', 'x_offset')
        arcpy.AlterField_management(displ_field_coords, 'Field4', 'y_offset', 'y_offset')
        arcpy.AlterField_management(displ_field_coords, 'Field5', 'magnitude', 'magnitude')
        arcpy.AlterField_management(displ_field_coords, 'Field6', 'RMSE', 'RMSE')
        arcpy.AddField_management(displ_field_coords, 'Point_ID', 'DOUBLE')
        codeblock = """
rec=0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if (rec == 0):
        rec = pStart
    else:
        rec += pInterval
    return rec """
        arcpy.CalculateField_management(in_table=displ_field_coords, field='Point_ID', expression='autoIncrement()',
                                        expression_type="PYTHON3", code_block=codeblock)
        arcpy.AddField_management(displ_field_coords, 'x_postEQ', 'DOUBLE')
        arcpy.AddField_management(displ_field_coords, 'y_postEQ', 'DOUBLE')
        arcpy.CalculateField_management(displ_field_coords, 'x_postEQ', '!x_coord! + !x_offset!')
        arcpy.CalculateField_management(displ_field_coords, 'y_postEQ', '!y_coord! - !y_offset!')
        print('Point feature class "displ_field_coords" created.')
        arcpy.sa.ExtractMultiValuesToPoints(displ_field_coords, [[PRE_EQ_DSM, 'z_2015']], 'NONE')
        displ_field_coords_postEQ_temp = OUTPUT_GDB + '/displ_field_coords_postEQ_temp'
        arcpy.MakeXYEventLayer_management(displ_field_coords, 'x_postEQ', 'y_postEQ', 'displ_field_postEQ_layer', EPSG)
        arcpy.CopyFeatures_management('displ_field_postEQ_layer', displ_field_coords_postEQ_temp, '', '0', '0', '0')
        arcpy.sa.ExtractValuesToPoints(displ_field_coords_postEQ_temp, POST_EQ_DSM, displ_field_coords_postEQ, 'NONE', 'ALL')
        arcpy.Delete_management(displ_field_coords_postEQ_temp)
        arcpy.AlterField_management(displ_field_coords_postEQ, 'RASTERVALU', 'z_2017', 'z_2017')
        arcpy.JoinField_management(displ_field_coords, 'Point_ID', displ_field_coords_postEQ, 'Point_ID', 'z_2017')
        arcpy.AddField_management(displ_field_coords, 'z_offset', 'DOUBLE')
        arcpy.CalculateField_management(displ_field_coords, 'z_offset', '!z_2017! - !z_2015!')
        arcpy.AddField_management(displ_field_coords, 'mag_3D', 'DOUBLE')
        arcpy.CalculateField_management(displ_field_coords, 'mag_3D', 'math.sqrt( (!x_offset!) **2 + (!y_offset!) **2 '
                                        '+ (!z_offset!) **2)')
        print('3D displacement calculated in feature class "displ_field_coords". '
            'Point feature class "displ_field_coords_postEQ created.')
    else:
        print('No point feature classes created.')

    return displ_field_coords, displ_field_coords_postEQ


def filter_point_layer(displ_field_coords):
    """ Applies filters and creates two new point feature classes when filters are applied"""
    displ_field_coords_filter_RMSE = OUTPUT_GDB + '/displ_field_coords_filter_RMSE'
    displ_field_coords_filter_RMSE_mask = OUTPUT_GDB + '/displ_field_coords_filter_RMSE_mask'
    if arcpy.Exists(displ_field_coords_filter_RMSE):
        arcpy.Delete_management(displ_field_coords_filter_RMSE)
    if arcpy.Exists(displ_field_coords_filter_RMSE_mask):
        arcpy.Delete_management(displ_field_coords_filter_RMSE_mask)
    if RMSE_FILTER == 1:
        where_clause = '\"RMSE\" < {}'.format(RMSE_THR)
        arcpy.Select_analysis(displ_field_coords, displ_field_coords_filter_RMSE, where_clause)
        print('RMSE point filter applied.')
    else:
        print('RMSE point filter not applied.')
    if USE_MASK == 1:
        arcpy.CopyFeatures_management(displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask)
        arcpy.MakeFeatureLayer_management(displ_field_coords_filter_RMSE_mask, 'displ_field_coords_filter_RMSE_mask')
        displ_field_coords_filter_RMSE_mask_select = arcpy.SelectLayerByLocation_management\
            ('displ_field_coords_filter_RMSE_mask', "INTERSECT", MASK)
        arcpy.DeleteFeatures_management(displ_field_coords_filter_RMSE_mask_select)
        print('Spatial point filter based on mask shapefile applied.')
    else:
        print('Spatial point filter based on mask shapefile was not applied.')
    return displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask


def get_pixel_locations(displ_field_selected):
    """Creates gdb tables with location of pre-EQ pixel coordinates projected to profile line"""
    profile_route = OUTPUT_GDB + '/profile_route'
    preEQ_coord_proj = OUTPUT_GDB + '/preEQ_coord_proj'
    postEQ_coord_proj = OUTPUT_GDB + '/postEQ_coord_proj'
    displ_vectors_proj = OUTPUT_GDB + '/displ_vectors_proj'
    postEQ_coord_selected = OUTPUT_GDB + '/postEQ_coord_selected'
    preEQ_coord_proj_table = OUTPUT_GDB + '/preEQ_coord_proj_table'
    postEQ_coord_proj_table = OUTPUT_GDB + '/postEQ_coord_proj_table'
    preEQ_coord_proj_csv = 'Output/temp/preEQ_coord_proj.csv'
    postEQ_coord_proj_csv = 'Output/temp/postEQ_coord_proj.csv'
    if arcpy.Exists(profile_route):
        arcpy.Delete_management(profile_route)
    if arcpy.Exists(preEQ_coord_proj):
        arcpy.Delete_management(preEQ_coord_proj)
    if arcpy.Exists(postEQ_coord_proj):
        arcpy.Delete_management(postEQ_coord_proj)
    if arcpy.Exists(displ_vectors_proj):
        arcpy.Delete_management(displ_vectors_proj)
    if arcpy.Exists(postEQ_coord_selected):
        arcpy.Delete_management(postEQ_coord_selected)
    if arcpy.Exists(preEQ_coord_proj_table):
        arcpy.Delete_management(preEQ_coord_proj_table)
    if arcpy.Exists(postEQ_coord_proj_table):
        arcpy.Delete_management(postEQ_coord_proj_table)
    arcpy.CreateRoutes_lr(PROFILE_LINE, "Profile", profile_route, "LENGTH")

    if PROJECT_TO_PROFILE == 1:
        arcpy.Near_analysis(displ_field_selected, PROFILE_LINE, BUFFER_DISTANCE, 'LOCATION', 'NO_ANGLE', 'PLANAR')
        arcpy.MakeXYEventLayer_management(displ_field_selected, 'NEAR_X', 'NEAR_Y', 'preEQ_coord_proj', EPSG)
        arcpy.CopyFeatures_management('preEQ_coord_proj', preEQ_coord_proj)
        arcpy.AlterField_management(preEQ_coord_proj, 'NEAR_X', 'x_preEQ_proj', 'x_preEQ_proj')
        arcpy.AlterField_management(preEQ_coord_proj, 'NEAR_Y', 'y_preEQ_proj', 'y_preEQ_proj')
        arcpy.MakeXYEventLayer_management(preEQ_coord_proj, 'x_postEQ', 'y_postEQ', 'postEQ_coord_selected', EPSG)
        arcpy.CopyFeatures_management('postEQ_coord_selected', postEQ_coord_selected)
        arcpy.Near_analysis(postEQ_coord_selected, PROFILE_LINE, '100 METERS', 'LOCATION', 'NO_ANGLE', 'PLANAR')
        arcpy.MakeXYEventLayer_management(postEQ_coord_selected, 'NEAR_X', 'NEAR_Y', 'postEQ_coord_proj', EPSG)
        arcpy.CopyFeatures_management('postEQ_coord_proj', postEQ_coord_proj)
        arcpy.AlterField_management(postEQ_coord_proj, 'NEAR_X', 'x_postEQ_proj', 'x_postEQ_proj')
        arcpy.AlterField_management(postEQ_coord_proj, 'NEAR_Y', 'y_postEQ_proj', 'y_postEQ_proj')
        arcpy.JoinField_management(preEQ_coord_proj, 'Point_ID', postEQ_coord_proj, 'Point_ID',
                                   'x_postEQ_proj;y_postEQ_proj')
        arcpy.LocateFeaturesAlongRoutes_lr(postEQ_coord_proj, profile_route, "Profile", "1 METER",
                                           postEQ_coord_proj_table)
        print('Point feature class "postEQ_coord_proj" containing post-EQ pixel locations projected to profile '
              'line created. Geodatabase table "postEQ_coord_proj_table" created.')
        arcpy.XYToLine_management(in_table=preEQ_coord_proj, out_featureclass=displ_vectors_proj,
                                  startx_field='x_preEQ_proj', starty_field='y_preEQ_proj', endx_field='x_postEQ_proj',
                                  endy_field='y_postEQ_proj', id_field='Point_ID', line_type='Geodesic',
                                  spatial_reference=EPSG)
        arcpy.JoinField_management(preEQ_coord_proj, 'Point_ID', displ_vectors_proj, 'Point_ID', 'Shape_Length')
        arcpy.AddField_management(preEQ_coord_proj, 'vector_length2D_proj', 'DOUBLE')
        arcpy.CalculateField_management(preEQ_coord_proj, 'vector_length2D_proj', '!Shape_Length!', 'PYTHON', '')
        arcpy.CalculateField_management(in_table=preEQ_coord_proj, field='vector_length2D_proj',
                                        expression='X(!vector_length2D_proj!)',
                                        code_block='def X(param):\n'
                                        '   if param is None:\n'
                                        '       return 0\n'
                                        '   else:\n'
                                        '       return param',expression_type='PYTHON3')
        print('Line feature class "displ_vectors_proj" containing projected displacement vectors created.')
        arcpy.LocateFeaturesAlongRoutes_lr(preEQ_coord_proj, profile_route, "Profile", "1 METER",
                                           preEQ_coord_proj_table)
        print('Point feature class "preEQ_coord_proj" containing pre-EQ pixel locations projected to profile '
              'line created. Geodatabase table "preEQ_coord_proj_table" created.')
        arcpy.TableToTable_conversion(preEQ_coord_proj_table, OUTPUT + '/temp', 'preEQ_coord_proj.csv')
        arcpy.TableToTable_conversion(postEQ_coord_proj_table, OUTPUT+ '/temp', 'postEQ_coord_proj.csv')
        print('Geodatabase tables exported to csv files.')
    else:
        print('Projection of pixel locations to profile line not carried out.')
    return profile_route, preEQ_coord_proj_csv, postEQ_coord_proj_csv


def select_features_to_project(displ_field_coords, displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask):
    """ Selects feature class to project based on applied filters"""
    displ_field_selected = displ_field_coords
    if RMSE_FILTER == 1 and USE_MASK == 0:
        displ_field_selected = displ_field_coords_filter_RMSE
    elif RMSE_FILTER == 1 and USE_MASK == 1:
        displ_field_selected = displ_field_coords_filter_RMSE_mask
    return displ_field_selected


def get_topo_profiles():
    """ Create csv tables containing elevation data """
    profile_preEQ_topo = PATH_DIC + '/Output/temp/profile_preEQ_topo.csv'
    profile_postEQ_topo = PATH_DIC + '/Output/temp/profile_postEQ_topo.csv'
    if CREATE_PROFILE_TOPODATA == 1:
        arcpy.ddd.StackProfile(in_line_features=PROFILE_LINE, profile_targets=PRE_EQ_DSM, out_table=profile_preEQ_topo)
        arcpy.ddd.StackProfile(PROFILE_LINE, [POST_EQ_DSM], profile_postEQ_topo)
        print('Profile data saved as csv files.')
    else:
        print('No new profile data created.')
    return profile_preEQ_topo, profile_postEQ_topo


def join_field_dic(displ_field_selected):
    """ Joins the displacements of DIC results within specified search distance to field measurement points """
    displ_field_corr = PATH_GIS + '/displ_field_corr'
    displ_field_dic_filtered = PATH_GIS + '/displ_field_dic_filtered'
    if arcpy.Exists(displ_field_corr):
        arcpy.Delete_management(displ_field_corr)
    if arcpy.Exists(displ_field_dic_filtered):
        arcpy.Delete_management(displ_field_dic_filtered)
    if SITE_FIELD_DISPL != '':
        arcpy.CopyFeatures_management(in_features=displ_field_selected,
                                    out_feature_class=displ_field_dic_filtered)
        arcpy.AddField_management(in_table=SITE_FIELD_DISPL, field_name='cum_3D_mag', field_type='DOUBLE')
        arcpy.CalculateField_management(in_table=SITE_FIELD_DISPL, field='cum_3D_mag',
                                        expression='math.sqrt((!cum_V_disp!)**2 + (!cum_H_disp!)**2)')
        arcpy.JoinFeatures_gapro(target_layer=SITE_FIELD_DISPL, join_layer=displ_field_dic_filtered,
                                output=displ_field_corr, join_operation='JOIN_ONE_TO_ONE',
                                spatial_relationship='NEAR', spatial_near_distance=SPATIAL_CORR,
                                temporal_relationship='', temporal_near_distance='',
                                attribute_relationship='', summary_fields='magnitude MEAN;z_offset MEAN;mag_3D MEAN')
        displ_field_corr_table = OUTPUT + '/displ_field_corr.csv'
        arcpy.TableToTable_conversion(in_rows=displ_field_corr, out_path=OUTPUT, out_name='displ_field_corr.csv')
        displ_field_corr_df = pd.read_csv(displ_field_corr_table)
    else:
        displ_field_corr_df = None
    return displ_field_corr_df


def create_dataframes(profile_preEQ_topo, profile_postEQ_topo, preEQ_coord_proj_csv, postEQ_coord_proj_csv):
    """ Imports data from GIS analysis into dataframes amd deletes temporary csv files """
    preEQ_topo_df0 = pd.read_csv(profile_preEQ_topo, usecols=['FIRST_DIST', 'FIRST_Z'])
    preEQ_topo_df1 = preEQ_topo_df0.rename(columns={'FIRST_DIST': 'meas_x', 'FIRST_Z': 'z_2015'})
    postEQ_topo_df0 = pd.read_csv(profile_postEQ_topo, usecols=['FIRST_Z'])
    postEQ_topo_df1 = postEQ_topo_df0.rename(columns={'FIRST_Z': 'z_2017'})
    topo_df = pd.concat([preEQ_topo_df1, postEQ_topo_df1], axis=1)
    preEQ_coord_proj_df0 = pd.read_csv(preEQ_coord_proj_csv, usecols=['MEAS', 'x_coord', 'y_coord', 'x_offset',
                                                                      'y_offset', 'magnitude', 'RMSE', 'x_postEQ',
                                                                      'y_postEQ', 'z_2015', 'z_2017', 'z_offset',
                                                                      'mag_3D', 'x_preEQ_proj', 'y_preEQ_proj',
                                                                      'x_postEQ_proj', 'y_postEQ_proj',
                                                                      'vector_length2D_proj'])
    preEQ_coord_proj_df1 = preEQ_coord_proj_df0.rename(columns={'MEAS':'meas_x_preEQ'})
    postEQ_coord_proj_df0 = pd.read_csv(postEQ_coord_proj_csv, usecols=['MEAS'])
    postEQ_coord_proj_df1 = postEQ_coord_proj_df0.rename(columns={'MEAS':'meas_x_postEQ'})
    displ_proj_df = pd.concat([preEQ_coord_proj_df1, postEQ_coord_proj_df1], axis=1)
    proj_offset = []
    if PROFILE_DIR == 'left-right':
        for i in range(0, len(displ_proj_df)):
            if displ_proj_df.meas_x_preEQ[i] > displ_proj_df.meas_x_postEQ[i]:
                proj_offset.append(displ_proj_df.vector_length2D_proj[i] * -1)
            else:
                proj_offset.append(displ_proj_df.vector_length2D_proj[i])
        displ_proj_df['proj_offset'] = proj_offset
    elif PROFILE_DIR == 'right-left':
        for i in range(0, len(displ_proj_df)):
            if displ_proj_df.meas_x_preEQ[i] < displ_proj_df.meas_x_postEQ[i]:
                proj_offset.append(displ_proj_df.vector_length2D_proj[i] * -1)
            else:
                proj_offset.append(displ_proj_df.vector_length2D_proj[i])
        displ_proj_df['proj_offset'] = proj_offset
    displ_plunge = []
    for i in range(0, len(displ_proj_df)):
        if displ_proj_df.proj_offset[i] != 0:
            plunge_rad = -1 * math.atan(displ_proj_df.z_offset[i] / displ_proj_df.proj_offset[i])
            plunge_deg = (plunge_rad * 180) / math.pi
        else:
            plunge_deg = 0
        displ_plunge.append(plunge_deg)
    displ_proj_df['displ_plunge'] = displ_plunge
    return topo_df, displ_proj_df