import arcpy
import arcpy.ddd
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
from dic_plot_all_profiles_global_variables import *


def get_topo_profiles(i):
    """ Create csv tables containing elevation data """
    profile_preEQ_topo = OUTPUT[i] + '/temp/profile_preEQ_topo.csv'
    profile_postEQ_topo = OUTPUT[i] + '/temp/profile_postEQ_topo.csv'
    if CREATE_PROFILE_TOPODATA == 1:
        arcpy.ddd.StackProfile(in_line_features=PROFILE_LINE[i], profile_targets=PRE_EQ_DSM[i], out_table=profile_preEQ_topo)
        arcpy.ddd.StackProfile(PROFILE_LINE[i], [POST_EQ_DSM[i]], profile_postEQ_topo)
        print('Profile data saved as csv files.')
    else:
        print('No new profile data created.')
    return profile_preEQ_topo, profile_postEQ_topo


def get_gis_point_layers(i):
    """ Creates point feature classes displ_field_coords (i.e. preEQ pixel coordinates) and displ_field_coords_postEQ
    (i.e. postEQ pixel coordinates and calculates the 3D displacement field.
    All attributes are re-attributed to the feature class displ_field_coords. """
    displ_field_coords = OUTPUT_GDB[i] + '/displ_field_coords'
    displ_field_coords_postEQ = OUTPUT_GDB[i] + '/displ_field_coords_postEQ'

    if arcpy.Exists(displ_field_coords):
        arcpy.Delete_management(displ_field_coords)
    if arcpy.Exists(displ_field_coords_postEQ):
        arcpy.Delete_management(displ_field_coords_postEQ)
    arcpy.MakeXYEventLayer_management(DISPL_INPUT_TXT[i], 'Field1', 'Field2', 'displ_field_layer', EPSG)
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
    arcpy.sa.ExtractMultiValuesToPoints(displ_field_coords, [[PRE_EQ_DSM[i], 'z_2015']], 'NONE')
    displ_field_coords_postEQ_temp = OUTPUT_GDB[i] + '/displ_field_coords_postEQ_temp'
    arcpy.MakeXYEventLayer_management(displ_field_coords, 'x_postEQ', 'y_postEQ', 'displ_field_postEQ_layer', EPSG)
    arcpy.CopyFeatures_management('displ_field_postEQ_layer', displ_field_coords_postEQ_temp, '', '0', '0', '0')
    arcpy.sa.ExtractValuesToPoints(displ_field_coords_postEQ_temp, POST_EQ_DSM[i], displ_field_coords_postEQ, 'NONE', 'ALL')
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
    return displ_field_coords, displ_field_coords_postEQ


def filter_point_layer(displ_field_coords, i):
    """ Applies filters and creates two new point feature classes when filters are applied"""
    displ_field_coords_filter_RMSE = OUTPUT_GDB[i] + '/displ_field_coords_filter_RMSE'
    displ_field_coords_filter_RMSE_mask = OUTPUT_GDB[i] + '/displ_field_coords_filter_RMSE_mask'
    if arcpy.Exists(displ_field_coords_filter_RMSE):
        arcpy.Delete_management(displ_field_coords_filter_RMSE)
    if arcpy.Exists(displ_field_coords_filter_RMSE_mask):
        arcpy.Delete_management(displ_field_coords_filter_RMSE_mask)
    where_clause = '\"RMSE\" < {}'.format(RMSE_THR[i])
    arcpy.Select_analysis(displ_field_coords, displ_field_coords_filter_RMSE, where_clause)
    print('RMSE point filter applied.')
    arcpy.CopyFeatures_management(displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask)
    arcpy.MakeFeatureLayer_management(displ_field_coords_filter_RMSE_mask, 'displ_field_coords_filter_RMSE_mask')
    displ_field_coords_filter_RMSE_mask_select = arcpy.SelectLayerByLocation_management\
            ('displ_field_coords_filter_RMSE_mask', "INTERSECT", MASK[i])
    arcpy.DeleteFeatures_management(displ_field_coords_filter_RMSE_mask_select)
    print('Spatial point filter based on mask shapefile applied.')
    return displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask


def select_features_to_project(displ_field_coords, displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask):
    """ Selects feature class to project based on applied filters"""
    displ_field_selected = displ_field_coords
    if RMSE_FILTER == 1 and USE_MASK == 0:
        displ_field_selected = displ_field_coords_filter_RMSE
    elif RMSE_FILTER == 1 and USE_MASK == 1:
        displ_field_selected = displ_field_coords_filter_RMSE_mask
    return displ_field_selected


def get_pixel_locations(displ_field_selected, i):
    """Creates gdb tables with location of pre-EQ pixel coordinates projected to profile line"""
    profile_route = OUTPUT_GDB[i] + '/profile_route'
    preEQ_coord_proj = OUTPUT_GDB[i] + '/preEQ_coord_proj'
    postEQ_coord_proj = OUTPUT_GDB[i] + '/postEQ_coord_proj'
    displ_vectors_proj = OUTPUT_GDB[i] + '/displ_vectors_proj'
    postEQ_coord_selected = OUTPUT_GDB[i] + '/postEQ_coord_selected'
    preEQ_coord_proj_table = OUTPUT_GDB[i] + '/preEQ_coord_proj_table'
    postEQ_coord_proj_table = OUTPUT_GDB[i] + '/postEQ_coord_proj_table'
    preEQ_coord_proj_csv = PATH_DIC[i] + '/Output/temp/preEQ_coord_proj.csv'
    postEQ_coord_proj_csv = PATH_DIC[i] + '/Output/temp/postEQ_coord_proj.csv'
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
    arcpy.CreateRoutes_lr(PROFILE_LINE[i], "Profile", profile_route, "LENGTH")

    if PROJECT_TO_PROFILE == 1:
        arcpy.Near_analysis(displ_field_selected, PROFILE_LINE[i], BUFFER_DISTANCE[i], 'LOCATION', 'NO_ANGLE', 'PLANAR')
        arcpy.MakeXYEventLayer_management(displ_field_selected, 'NEAR_X', 'NEAR_Y', 'preEQ_coord_proj', EPSG)
        arcpy.CopyFeatures_management('preEQ_coord_proj', preEQ_coord_proj)
        arcpy.AlterField_management(preEQ_coord_proj, 'NEAR_X', 'x_preEQ_proj', 'x_preEQ_proj')
        arcpy.AlterField_management(preEQ_coord_proj, 'NEAR_Y', 'y_preEQ_proj', 'y_preEQ_proj')
        arcpy.MakeXYEventLayer_management(preEQ_coord_proj, 'x_postEQ', 'y_postEQ', 'postEQ_coord_selected', EPSG)
        arcpy.CopyFeatures_management('postEQ_coord_selected', postEQ_coord_selected)
        arcpy.Near_analysis(postEQ_coord_selected, PROFILE_LINE[i], '100 METERS', 'LOCATION', 'NO_ANGLE', 'PLANAR')
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
        print('Line feature class "displ_vectors_proj" containing projected displacement vectors created.')
        arcpy.LocateFeaturesAlongRoutes_lr(preEQ_coord_proj, profile_route, "Profile", "1 METER",
                                           preEQ_coord_proj_table)
        print('Point feature class "preEQ_coord_proj" containing pre-EQ pixel locations projected to profile '
              'line created. Geodatabase table "preEQ_coord_proj_table" created.')
        arcpy.TableToTable_conversion(preEQ_coord_proj_table, PATH_DIC[i] + '/Output/temp', 'preEQ_coord_proj.csv')
        arcpy.TableToTable_conversion(postEQ_coord_proj_table, PATH_DIC[i] + '/Output/temp', 'postEQ_coord_proj.csv')
        print('Geodatabase tables exported to csv files.')
    else:
        print('Projection of pixel locations to profile line not carried out.')
    return profile_route, preEQ_coord_proj_csv, postEQ_coord_proj_csv


def create_dataframes(profile_preEQ_topo, profile_postEQ_topo, preEQ_coord_proj_csv, postEQ_coord_proj_csv, i):
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
    if PROFILE_DIR[i] == 'left-right':
        for i in range(0, len(displ_proj_df)):
            if displ_proj_df.meas_x_preEQ[i] > displ_proj_df.meas_x_postEQ[i]:
                proj_offset.append(displ_proj_df.vector_length2D_proj[i] * -1)
            else:
                proj_offset.append(displ_proj_df.vector_length2D_proj[i])
        displ_proj_df['proj_offset'] = proj_offset
    elif PROFILE_DIR[i] == 'right-left':
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


def get_deformation_data(profile_route, topo_df, i):
    """ Extracts locations of mapped ground cracks and the onset of catastrophic failure along the profile line"""
    crack_x_locations = []
    failure_location = ()
    if GROUND_CRACKS[i] != '':
        ground_cracks_proj = OUTPUT_GDB[i] + '/ground_cracks_proj'
        intersection_points = OUTPUT_GDB[i] + '/intersection_points'
        if arcpy.Exists(ground_cracks_proj):
            arcpy.Delete_management(ground_cracks_proj)
        if arcpy.Exists(ground_cracks_proj):
            arcpy.Delete_management(ground_cracks_proj)
        arcpy.Intersect_analysis([GROUND_CRACKS[i], PROFILE_LINE[i]], intersection_points, output_type='POINT')
        arcpy.LocateFeaturesAlongRoutes_lr(intersection_points, profile_route, 'Profile', '1 Meters',
                                           out_table=ground_cracks_proj, out_event_properties='Profile POINT MEAS')
        mapped_cracks = arcpy.da.SearchCursor(ground_cracks_proj, field_names='MEAS')
        for row in mapped_cracks:
            crack_x_locations.append(row[0])
    if CATASTROPHIC_FAILURE[i] != '':
        failure_proj = OUTPUT_GDB[i] + '/failure_proj'
        intersection = OUTPUT_GDB[i] + '/intersection'
        if arcpy.Exists(failure_proj):
            arcpy.Delete_management(failure_proj)
        if arcpy.Exists(intersection):
            arcpy.Delete_management(intersection)
        arcpy.Intersect_analysis([CATASTROPHIC_FAILURE[i], PROFILE_LINE[i]], intersection, output_type='POINT')
        arcpy.LocateFeaturesAlongRoutes_lr(intersection, profile_route, 'Profile', '1 Meter',
                                           out_table=failure_proj, out_event_properties='Profile POINT MEAS')
        failure = arcpy.da.SearchCursor(failure_proj, field_names=['MEAS'])
        failure_x_list = []
        for row in failure:
            failure_x = row[0]
            failure_x_list.append(failure_x)
        failure_x = failure_x_list[0]
        meas_x = topo_df['meas_x'].tolist()
        z_2015 = topo_df['z_2017'].tolist()
        n_list = []
        for i in meas_x:
            n = abs(i - failure_x)
            n_list.append(n)
        idx = n_list.index(min(n_list))
        failure_x1 = meas_x[idx]
        failure_z = z_2015[idx]
        failure_location = (failure_x1, failure_z)
    return crack_x_locations, failure_location


def get_toe_location(topo_df, i):
    """ Returns toe x and z value and gdb table toe_location"""
    x_value = TOE[i]
    meas_x = topo_df['meas_x'].tolist()
    z_2015 = topo_df['z_2015'].tolist()
    n = [abs(i - x_value) for i in meas_x]
    idx = n.index(min(n))
    toe_x_value = meas_x[idx]
    toe_z_value = z_2015[idx]
    print('Toe location selected at {:.1f} m along profile at {:.1f} m elevation.'.format(toe_x_value,
                                                                                          toe_z_value))
    return toe_x_value, toe_z_value


def get_strain_dic(displ_proj_df, toe_x_value, toe_z_value, i):
    """ Calculate 1D strain from DIC displacements along profile """
    displ_proj_strain_df = displ_proj_df.copy()
    angle_to_toe_list = []
    angle_to_toe_list_deg = []
    strain_list_dic = []
    for row in range(0, len(displ_proj_strain_df)):
        if PROFILE_DIR[i] == 'left-right' and displ_proj_strain_df.meas_x_preEQ[row] < toe_x_value:
            x_dist_to_toe = abs(toe_x_value - displ_proj_strain_df.meas_x_preEQ[row])
            z_dist_to_toe = abs(toe_z_value - displ_proj_strain_df.z_2015[row])
            dist_to_toe = math.sqrt(x_dist_to_toe ** 2 + z_dist_to_toe ** 2)
            angle_to_toe = math.atan(-1 * z_dist_to_toe / x_dist_to_toe)
            angle_to_toe_list.append(angle_to_toe)
            angle_to_toe_list_deg.append(angle_to_toe * 180 / math.pi)
            if displ_proj_strain_df.proj_offset[row] >= 0:
                vector_proj_length = math.sqrt(displ_proj_strain_df.proj_offset[row] ** 2 +
                                               displ_proj_strain_df.z_offset[row] ** 2)
            else:
                vector_proj_length = - (math.sqrt(displ_proj_strain_df.proj_offset[row] ** 2 +
                                                  displ_proj_strain_df.z_offset[row] ** 2))
            if displ_proj_strain_df.proj_offset[row] != 0:
                angle_displ = math.atan(displ_proj_strain_df.z_offset[row] / displ_proj_strain_df.proj_offset[row])
            else:
                angle_displ = 0
            angle_diff = abs(angle_displ - angle_to_toe)
            strain = (vector_proj_length * math.cos(angle_diff)) / (dist_to_toe)
            strain_list_dic.append(strain)
        elif PROFILE_DIR[i] == 'left-right' and displ_proj_strain_df.meas_x_preEQ[row] > toe_x_value:
            strain = 0
            strain_list_dic.append(strain)
            angle_to_toe = 0
            angle_to_toe_list_deg.append(angle_to_toe)
        elif PROFILE_DIR[i] == 'right-left' and displ_proj_strain_df.meas_x_preEQ[row] > toe_x_value:
            x_dist_to_toe = abs(toe_x_value - displ_proj_strain_df.meas_x_preEQ[row])
            z_dist_to_toe = abs(toe_z_value - displ_proj_strain_df.z_2015[row])
            dist_to_toe = math.sqrt(x_dist_to_toe ** 2 + z_dist_to_toe ** 2)
            angle_to_toe = math.atan(-1 * z_dist_to_toe / x_dist_to_toe)
            angle_to_toe_list.append(angle_to_toe)
            angle_to_toe_list_deg.append(angle_to_toe * 180 / math.pi)
            if displ_proj_strain_df.proj_offset[row] >= 0:
                vector_proj_length = math.sqrt(displ_proj_strain_df.proj_offset[row] ** 2 +
                                               displ_proj_strain_df.z_offset[row] ** 2)
            else:
                vector_proj_length = - (math.sqrt(displ_proj_strain_df.proj_offset[row] ** 2 +
                                                  displ_proj_strain_df.z_offset[row] ** 2))
            if displ_proj_strain_df.proj_offset[i] != 0:
                angle_displ = math.atan(displ_proj_strain_df.z_offset[row] / displ_proj_strain_df.proj_offset[row])
            else:
                angle_displ = 0
            angle_diff = abs(angle_displ - angle_to_toe)
            strain = (vector_proj_length * math.cos(angle_diff)) / (dist_to_toe)
            strain_list_dic.append(strain)
        elif PROFILE_DIR[i] == 'right-left' and displ_proj_strain_df.meas_x_preEQ[row] < toe_x_value:
            strain = 0
            strain_list_dic.append(strain)
            angle_to_toe = 0
            angle_to_toe_list_deg.append(angle_to_toe)
    max_strain_dic = max(strain_list_dic)
    print('Strain from DIC measurements calculated. Maximum strain, method 1 = {:.3f}'.format(max_strain_dic))
    displ_proj_strain_df['strain_dic'] = strain_list_dic
    displ_proj_strain_df['angle_to_toe'] = angle_to_toe_list_deg
    return displ_proj_strain_df


def filter_outliers(displ_proj_strain_df):
    outlier_list = [False] * len(displ_proj_strain_df)
    proj_offset_ind =displ_proj_strain_df.columns.get_loc('proj_offset')
    for i in range(0, len(displ_proj_strain_df)):
        if displ_proj_strain_df.iloc[i, proj_offset_ind] < -0:
            outlier_list[i] = True
    displ_proj_strain_df['outlier'] = outlier_list
    displ_proj_strain_filt_df = displ_proj_strain_df[displ_proj_strain_df['outlier'] == False]
    return displ_proj_strain_filt_df


def get_field_displ_df(profile_route, i):
    field_displ_df = pd.DataFrame()
    if SITE_FIELD_DISPL[i] != '':
        field_points_proj = OUTPUT_GDB[i] + '/field_points_proj'
        arcpy.sa.ExtractMultiValuesToPoints(SITE_FIELD_DISPL[i], [[POST_EQ_DSM[i], 'z_2017']], 'NONE')
        arcpy.LocateFeaturesAlongRoutes_lr(in_features=SITE_FIELD_DISPL[i], in_routes=profile_route,
                                           route_id_field='Profile',
                                           radius_or_tolerance='20 Meters', in_fields='FIELDS',
                                           out_table=field_points_proj)
        cursor = arcpy.da.SearchCursor(field_points_proj,
                                       field_names=['MEAS', 'z_2017', 'cum_V_disp', 'cum_H_disp', 'OBJECTID'])
        object_id = []
        field_x_list = []
        field_z_list = []
        cum_V_disp_list = []
        cum_H_disp_list = []
        for row in cursor:
            field_x_list.append(row[0])
            field_z_list.append(row[1])
            cum_V_disp_list.append(row[2])
            cum_H_disp_list.append(row[3])
            object_id.append(row[4])
        field_displ_data = {'object_id': object_id, 'meas_x_field': field_x_list, 'z_field': field_z_list,
                             'cum_V_disp': cum_V_disp_list, 'cum_H_disp': cum_H_disp_list}
        field_displ_df = pd.DataFrame(field_displ_data)
        cum_3D_mag = []
        for i in range(0, len(field_displ_df)):
            mag_3D = math.sqrt(field_displ_df.cum_V_disp[i]**2 + field_displ_df.cum_H_disp[i]**2)
            cum_3D_mag.append(mag_3D)
        field_displ_df['cum_3D_mag'] = cum_3D_mag
    return field_displ_df


def get_strain_field(field_displ_df, toe_x_value, toe_z_value, i):
    """ Calculates 1D strain along profile for field measurements """
    field_strain_df = field_displ_df
    if SITE_FIELD_DISPL[i] != '':
        strain_list_field = []
        for i in range(0, len(field_displ_df)):
            x_dist_to_toe = abs(toe_x_value - (field_displ_df.meas_x_field[i] - field_displ_df.cum_H_disp[i]))
            z_dist_to_toe = abs(toe_z_value - (field_displ_df.z_field[i] - field_displ_df.cum_V_disp[i]))
            dist_to_toe = math.sqrt(x_dist_to_toe ** 2 + z_dist_to_toe ** 2)
            angle_to_toe = math.atan(z_dist_to_toe / x_dist_to_toe)
            vector_proj_length = math.sqrt(field_displ_df.cum_H_disp[i] ** 2 + field_displ_df.cum_V_disp[i] ** 2)
            if field_displ_df.cum_H_disp[i] != 0:
                angle_displ = math.atan(-1 * field_displ_df.cum_V_disp[i] / field_displ_df.cum_H_disp[i])
            else:
                angle_displ = 0
            angle_diff = abs(angle_displ - angle_to_toe)
            strain = (vector_proj_length * math.cos(angle_diff)) / (dist_to_toe)
            strain_list_field.append(strain)
        field_strain_df['strain_field'] = strain_list_field
        max_strain_field = max(strain_list_field)
        print('Strain from field measurements calculated. Maximum strain = {:.3f}'.format(max_strain_field))
    else:
        print('No field measurements available.')
    return field_strain_df


def get_norm_dist(displ_proj_strain_filt_df, field_strain_df, toe_x_value, crack_x_locations, failure_location, i):
    crack_x_locations_norm = []
    profile_len = [f[0] for f in arcpy.da.SearchCursor(PROFILE_LINE[i], 'SHAPE@LENGTH')][0]
    if PROFILE_DIR[i] == 'right-left':
        for x in crack_x_locations:
            x_norm = (profile_len - x) / (profile_len - toe_x_value)
            crack_x_locations_norm.append(x_norm)
        if CATASTROPHIC_FAILURE[i] != '':
            failure_x_norm = (profile_len - failure_location[0]) / (profile_len - toe_x_value)
        else:
            failure_x_norm = 'None'
    else:
        for x in crack_x_locations:
            x_norm = x / toe_x_value
            crack_x_locations_norm.append(x_norm)
        if CATASTROPHIC_FAILURE[i] != '':
            failure_x_norm = failure_location[0] / toe_x_value
        else:
            failure_x_norm = 'None'
    meas_x_preEQ_norm_list = []
    x_ind = displ_proj_strain_filt_df.columns.get_loc('meas_x_preEQ')
    if PROFILE_DIR[i] == 'right-left':
        for row in range(0, len(displ_proj_strain_filt_df)):
            meas_x_norm = (profile_len - displ_proj_strain_filt_df.iloc[row,x_ind])/(profile_len - toe_x_value)
            meas_x_preEQ_norm_list.append(meas_x_norm)
    else:
        for row in range(0, len(displ_proj_strain_filt_df)):
            meas_x_norm = displ_proj_strain_filt_df.iloc[row, x_ind]/toe_x_value
            meas_x_preEQ_norm_list.append(meas_x_norm)

    column_values = pd.Series(meas_x_preEQ_norm_list)
    column_values.index = displ_proj_strain_filt_df.index
    displ_proj_strain_filt_df.insert(loc=0, column='meas_x_preEQ_norm', value=column_values)
    if SITE_FIELD_DISPL[i] != '':
        meas_x_field_norm = []
        x_ind_field = field_strain_df.columns.get_loc('meas_x_field')
        if PROFILE_DIR[i] == 'right-left':
            for i in range(0, len(field_strain_df)):
                meas_x_norm = (profile_len - field_strain_df.iloc[i, x_ind_field])/(profile_len - toe_x_value)
                meas_x_field_norm.append(meas_x_norm)
        else:
            for i in range(0, len(field_strain_df)):
                meas_x_norm = field_strain_df.iloc[i, x_ind_field]/toe_x_value
                meas_x_field_norm.append(meas_x_norm)
        field_strain_df['meas_x_field_norm'] = meas_x_field_norm
    return displ_proj_strain_filt_df, field_strain_df, crack_x_locations_norm, failure_x_norm


def plot_strain_overview(displ_proj_strain_filt_df, field_strain_df, crack_x_locations_norm, failure_x_norm, i):
    """ Plots 2 subplots showing projected displacement magnitudes and strain """
    fig1, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))
    max_x_graph = 1
    # Create displacement subplot
    max_displ = max(displ_proj_strain_filt_df['proj_offset'])+1
    ax[0].scatter(displ_proj_strain_filt_df['meas_x_preEQ_norm'], displ_proj_strain_filt_df['proj_offset'],
                s=8, color='red', label='Projected displacement vector magnitudes in profile plane (from DIC)')
    for x in crack_x_locations_norm:
        ax[0].plot([x, x], [0, max_displ], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE[i] != '':
        ax[0].plot([failure_x_norm, failure_x_norm], [0, max_displ], color='black',
                linestyle='--', linewidth='1', label='catastrophic failure')
    if SITE_FIELD_DISPL[i] != '':
        ax[0].scatter(field_strain_df['meas_x_field_norm'], field_strain_df['cum_3D_mag'],
                    color='black', s=8, label='Displacement magnitude 3D (from field measurements)')
    ax[0].set_ylabel('displacement in m', fontsize=8)
    ax[0].set_xlim(0, max_x_graph)
    ax[0].tick_params(labelsize=8)
    ax[0].legend(loc='best', fontsize=8)
    # Create strain subplot
    max_strain = max(displ_proj_strain_filt_df['strain_dic'])
    ax[1].scatter(displ_proj_strain_filt_df['meas_x_preEQ_norm'], displ_proj_strain_filt_df['strain_dic'],
                  s=8, color='teal', label='Strain (from DIC)')
    for x in crack_x_locations_norm:
        ax[1].plot([x, x], [0, max_strain], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE[i] != '':
        ax[1].plot([failure_x_norm, failure_x_norm], [0, max_strain], color='black',
                   linestyle='--', linewidth='1', label='catastrophic failure')
    if SITE_FIELD_DISPL[i] != '':
        ax[1].scatter(field_strain_df['meas_x_field_norm'], field_strain_df['strain_field'], color='black', s=8,
                      label='Strain (from field measurements)')
    ax[1].set_ylabel('strain', fontsize=8)
    ax[1].set_xlim(0, max_x_graph)
    ax[1].set_ylim(-0.001, max_strain + 0.1 * max_strain)
    ax[1].tick_params(labelsize=8)
    ax[1].legend(loc='best', fontsize=8)
    plt.show()


def plot_profiles(results_df, failure_df):
    fig2, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))
    # Create displacement subplot
    failure_x_norm_str = failure_df['failure_x_norm'].tolist()
    failure_x_norm = []
    for num in failure_x_norm_str:
        if num != 'None':
            failure_x = float(num)
        else:
            failure_x = -1
        failure_x_norm.append(failure_x)
    max_displ = 20
    colors0 = iter(cm.jet(np.linspace(0, 1, len(PROFILE_LIST))))
    colors2 = iter(cm.jet(np.linspace(0, 1, len(PROFILE_LIST))))
    for i in range(0, len(PROFILE_LIST)):
        x_values = results_df['meas_x_preEQ_norm_{}'.format(PROFILE_LIST[i])]
        displ_values = results_df['proj_offset_{}'.format(PROFILE_LIST[i])]
        ax[0].scatter(x_values, displ_values, s=10, marker='x', color=next(colors0), label='{}'.format(PROFILE_LIST[i]))
        ax[0].plot([failure_x_norm[i], failure_x_norm[i]], [0, max_displ], color=next(colors2),
                    linestyle='solid', linewidth='0.5')
    ax[0].set_ylabel('displacement [m]', fontsize=10)
    ax[0].set_xlim(0, 1)
    ax[0].tick_params(labelsize=10)
    #ax[0].legend(loc='best', fontsize=8, bbox_to_anchor=(1, 1))
    # Create strain subplot
    max_strain = 0.15
    colors1 = iter(cm.jet(np.linspace(0, 1, len(PROFILE_LIST))))
    colors3 = iter(cm.jet(np.linspace(0, 1, len(PROFILE_LIST))))
    for i in range(0, len(PROFILE_LIST)):
        ax[1].scatter(results_df['meas_x_preEQ_norm_{}'.format(PROFILE_LIST[i])],
                      results_df['strain_dic_{}'.format(PROFILE_LIST[i])],
                      s=10, marker='x', color=next(colors1), label='{}'.format(PROFILE_LIST[i]))
        ax[1].plot([failure_x_norm[i], failure_x_norm[i]], [0, max_strain-0.01], color=next(colors3),
                    linestyle='solid', linewidth='0.5')
    ax[1].set_ylabel('strain [-]', fontsize=10)
    ax[1].set_xlabel('normalised distance along profile', fontsize=10)
    ax[1].set_xlim(0, 1)
    ax[1].set_ylim(-0.001, max_strain)
    ax[1].tick_params(labelsize=10)
    ax[1].legend(title='Analysed Profiles', loc='upper left', fontsize=10, bbox_to_anchor=(1.01, 1.3), frameon=False)
    plt.show()


