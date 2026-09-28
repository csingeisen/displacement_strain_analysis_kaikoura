""" Global variables and file directory """

# Set global variables
EPSG = 2193
RMSE_FILTER = 1
USE_MASK = 1
CREATE_PROFILE_TOPODATA = 1
PROJECT_TO_PROFILE = 1

# Define profiles
PROFILE_LIST = ['MPS_P1', 'MPS_P2', 'OP_P1', 'OP_P2', 'OP_P3', 'OP_P4',
                'UK_P1', 'UK_P2', 'UK_P3', 'UK_P4', 'UK_P7_a', 'UK_P7_b', 'UK_P8', 'UK_P9',
                'LK_P4', 'OB_P1', 'OB_P3']# 20.7.22: profile 2 Okiwi removed
SITE_LIST = ['MtPeter_MtStewart', 'MtPeter_MtStewart', 'OhauPoint', 'OhauPoint', 'OhauPoint', 'OhauPoint',
             'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai',
             'UpperKowhai', 'LowerKowhai', 'Okiwi', 'Okiwi']
SITE_NAME_LIST = ['MtPeterSouth', 'MtPeterSouth', 'OhauPoint', 'OhauPoint', 'OhauPoint', 'OhauPoint', 'UpperKowhai',
                  'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai', 'UpperKowhai',
                  'UpperKowhai', 'LowerKowhai', 'Okiwi', 'Okiwi']
SITE_ID_LIST = ['06', '06', '04', '04', '04', '04', '09', '09', '09', '09', '09', '09', '09', '09',
                '10', '08', '08']
# Set attributes
PROFILE_NR_LIST = [3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 7, 7, 8, 9, 4, 1, 3]
INPUT_FILE_RUN = ['17', '17', '23', '23', '23', '23', '07', '07', '07', '07', '07', '07', '07', '07',
                  '02', '06', '06']
BUFFER_DISTANCE = ['10 METERS', '10 METERS', '20 METERS', '20 METERS', '20 METERS', '20 METERS', '10 METERS',
                        '10 METERS',  '10 METERS', '10 METERS', '10 METERS', '10 METERS', '10 METERS', '10 METERS',
                        '10 METERS', '20 METERS', '20 METERS']
PROFILE_DIR = ['left-right', 'left-right','left-right','left-right','left-right','left-right','left-right',
                    'left-right','right-left','right-left', 'left-right','left-right','left-right','left-right',
                    'right-left', 'left-right','left-right']
RMSE_THR = [0.35, 0.35, 1, 1, 1, 1, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.4, 1, 1]
FIELD_DISPL = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0]
FAILURE = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0]
TOE = [175, 175, 565, 620, 775, 445, 180, 170, 150, 60, 86, 240, 168, 180, 300, 215, 215]
# Set file paths
# initiate lists
PATH_GIS = []
PATH_DIC = []
SITE_FIELD_DISPL = []
OUTPUT_GDB = []
OUTPUT = []
DISPL_INPUT_TXT = []
PRE_EQ_DSM = []
POST_EQ_DSM = []
MASK = []
PROFILE_LINE = []
CATASTROPHIC_FAILURE = []
GROUND_CRACKS = []
# iterate through profiles to get all file paths
for i in range(0, len(PROFILE_LIST)):
    path_gis = 'C:/Users/csi57/02_GIS_lokal/{}_{}.gdb'.format(SITE_ID_LIST[i],SITE_LIST[i])
    PATH_GIS.append(path_gis)
    path_dic = 'C:/Users/csi57/04_Remote_Sensing_lokal/{}_{}/Analysis'.format(SITE_ID_LIST[i],SITE_LIST[i])
    PATH_DIC.append(path_dic)
    input = path_dic + '/Input'
    output = path_dic + '/Output'
    OUTPUT.append(output)
    output_gdb = path_dic + '/Output/DIC_{}.gdb'.format(SITE_NAME_LIST[i])
    OUTPUT_GDB.append(output_gdb)
    displ_input_txt = input + '/DIC_{}_run{}.txt'.format(SITE_NAME_LIST[i], INPUT_FILE_RUN[i])
    DISPL_INPUT_TXT.append(displ_input_txt)
    pre_eq_dsm = input + '/DSM_2015_1m_corrICP_{}.tif'.format(SITE_NAME_LIST[i])
    PRE_EQ_DSM.append(pre_eq_dsm)
    post_eq_dsm = input + '/DSM_2017_1m_{}.tif'.format(SITE_NAME_LIST[i])
    POST_EQ_DSM.append(post_eq_dsm)
    profile_line = input + '/{}_profile_line_{}.shp'.format(SITE_NAME_LIST[i],PROFILE_NR_LIST[i])
    PROFILE_LINE.append(profile_line)
    ground_cracks = input + '/{}_ground_cracks.shp'.format(SITE_NAME_LIST[i])
    GROUND_CRACKS.append(ground_cracks)
    mask = input + '/{}_decorrelation_mask.shp'.format(SITE_NAME_LIST[i])
    MASK.append(mask)
    if FAILURE[i] == 1:
        catastrophic_failure = input + '/{}_catastrophic_failure.shp'.format(SITE_NAME_LIST[i])
    else:
        catastrophic_failure = ''
    CATASTROPHIC_FAILURE.append(catastrophic_failure)
    if FIELD_DISPL[i] == 1:
        field_input = path_gis + '/{}_field_displacements'.format(SITE_LIST[i],SITE_NAME_LIST[i],SITE_NAME_LIST[i])
    else:
        field_input = ''
    SITE_FIELD_DISPL.append(field_input)