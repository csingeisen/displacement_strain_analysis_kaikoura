import arcpy
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import *
from dic_global_constants import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'E:/02_GIS_lokal/06_MtPeter_MtStewart.gdb'


def correct_dsm():
    """ DSM correction for tectonic displacement in pre-event DSM based on mean ICP measurements in study area
    """
    if DSM_CORRECTION == 1:
        north_offset_calc = arcpy.GetRasterProperties_management(ALL_NORTH_MASK, "MEAN")
        north_offset = north_offset_calc.getOutput(0)
        print("Mean offset towards North = {}".format(north_offset))
        east_offset_calc = arcpy.GetRasterProperties_management(ALL_EAST_MASK, "MEAN")
        east_offset = east_offset_calc.getOutput(0)
        print("Mean offset towards East = {}".format(east_offset))
        vertical_offset_calc = arcpy.GetRasterProperties_management(ALL_VERTICAL_MASK, "MEAN")
        vertical_offset = vertical_offset_calc.getOutput(0)
        print("Mean vertical offset = {}".format(vertical_offset))
        dsm_corr_temp = arcpy.Shift_management(DSM, "DSM_corr_temp", east_offset, north_offset)
        dsm_corr_output = (Raster(dsm_corr_temp) + float(vertical_offset))
        dsm_corr_output.save(DSM_CORR)
        arcpy.Delete_management(dsm_corr_temp)
        print('DSM correction applied. Copy DSM_corrICP from GIS into DIC folder')
    else:
        print('DSM correction not applied.')


correct_dsm()