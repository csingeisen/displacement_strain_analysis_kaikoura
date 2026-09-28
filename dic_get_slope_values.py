from dic_global_constants import *
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True
from arcpy.sa import *

DSM_corr_10m = PATH_GIS + '/DSM_2015_10m_corrICP'
Slope_DSM_corr_10m = PATH_GIS + '/Slope_DSM_2015_10m_corrICP'

Slope_DSM_corr_10m_ground_def = PATH_GIS + '/Slope_DSM_2015_10m_corrICP_ground_def'
sample_points = PATH_GIS + '/sample_points'
Slope_values_ground_def = PATH_GIS + '/Slope_values_ground_def'
Slope_DSM_corr_10m_failure = PATH_GIS + '/Slope_DSM_2015_10m_corrICP_failure'
Slope_values_failure = PATH_GIS + '/Slope_values_failure'


def create_slope_raster():
    arcpy.Resample_management(DSM_CORR, DSM_corr_10m, cell_size= '10', resampling_type='NEAREST')
    slope = arcpy.sa.Slope(DSM_corr_10m, 'DEGREE', '', 'GEODESIC', 'METER')
    slope.save(Slope_DSM_corr_10m)


def get_average_slope_ground_def():
    slope_extracted = arcpy.sa.ExtractByMask(Slope_DSM_corr_10m, GROUND_DEFORMATION)
    slope_extracted.save(Slope_DSM_corr_10m_ground_def)
    arcpy.GeneratePointsAlongLines_management(PROFILE_LINE, sample_points, 'DISTANCE', Distance='10 METERS')
    arcpy.sa.Sample(Slope_DSM_corr_10m_ground_def, sample_points, Slope_values_ground_def)
    slope = arcpy.da.SearchCursor(Slope_values_ground_def, field_names=['Slope_DSM_2015_10m_corrICP_ground_def_Band_1'])
    slope_list = []
    for row in slope:
        if row[0] != None:
            slope_list.append(row[0])
    print(slope_list)
    mean_slope_ground_def = sum(slope_list) / len(slope_list)
    print('Mean slope angle of the defined ground deformation area (10m pre-EQ DSM) = {:.1f} deg'.format(mean_slope_ground_def))


def get_average_slope_failure():
    slope_extracted = arcpy.sa.ExtractByMask(Slope_DSM_corr_10m, SOURCE_EXCAVATED)
    slope_extracted.save(Slope_DSM_corr_10m_failure)
    arcpy.sa.Sample(Slope_DSM_corr_10m_failure, sample_points, Slope_values_failure)
    slope = arcpy.da.SearchCursor(Slope_values_failure, field_names=['Slope_DSM_2015_10m_corrICP_failure_Band_1'])
    slope_list = []
    for row in slope:
        if row[0] != None:
            slope_list.append(row[0])
    print(slope_list)
    mean_slope_failure = sum(slope_list) / len(slope_list)
    print('Mean slope angle of excavated source area area (10m pre-EQ DSM) = {:.1f} deg'.format(mean_slope_failure))




def delete_data():
    arcpy.Delete_management(DSM_corr_10m)
    arcpy.Delete_management(Slope_DSM_corr_10m)
    arcpy.Delete_management(Slope_DSM_corr_10m_ground_def)
    arcpy.Delete_management(sample_points)
    arcpy.Delete_management(Slope_values_ground_def)
    arcpy.Delete_management(Slope_DSM_corr_10m_failure)
    arcpy.Delete_management(Slope_values_failure)


delete_data()
create_slope_raster()
get_average_slope_ground_def()
get_average_slope_failure()

