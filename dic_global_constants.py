""" Global constants and analysis settings """
from dic_directory_OhauPoint import *


""" Set global constants """
EPSG = 2193     # coordinate system
BUFFER_DISTANCE = '20 METERS'   # Define buffer distance around profiles for vector projection
SPATIAL_CORR = '10 Meters'  # Distance around field measurement points taken into account for displacement comparison

""" Specify analysis to be carried out (perform analysis = 1, skip analysis step = 0) """
DSM_CORRECTION = 1
CREATE_GIS_POINT_LAYERS = 1
RMSE_FILTER = 1
RMSE_THR = 1  # select root mean square error threshold between 0 and 1
USE_MASK = 1
PROJECT_TO_PROFILE = 1
CREATE_PROFILE_TOPODATA = 1
PLOT_PROFILE = 1
PlOT_MAP = 1
PLOT_SCATTER_PLOTS = 1  # only if field measurements are available
TOE_CALC = 'numeric'  # select toe location as shapefile, graphic input or numeric input [shapefile/graphic/numeric]
CALCULATE_STRAIN = 1
PLOT_STRAIN = 1