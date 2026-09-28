import math
import pandas as pd
from dic_global_constants import *
from dic_module_displ_plots import *
import statistics


def get_strain_dic(displ_proj_df, toe_x_value, toe_z_value):
    """ Calculate 1D strain from DIC displacements along profile """
    displ_proj_strain_df = displ_proj_df.copy()
    if CALCULATE_STRAIN == 1:
        angle_to_toe_list = []
        angle_to_toe_list_deg = []
        strain_list_dic = []
        for i in range(0, len(displ_proj_strain_df)):
            if PROFILE_DIR == 'left-right' and displ_proj_strain_df.meas_x_preEQ[i] < toe_x_value:
                x_dist_to_toe = abs(toe_x_value - displ_proj_strain_df.meas_x_preEQ[i])
                z_dist_to_toe = abs(toe_z_value - displ_proj_strain_df.z_2015[i])
                dist_to_toe = math.sqrt(x_dist_to_toe**2 + z_dist_to_toe**2)
                angle_to_toe = math.atan(-1 * z_dist_to_toe/x_dist_to_toe)
                angle_to_toe_list.append(angle_to_toe)
                angle_to_toe_list_deg.append(angle_to_toe *180/math.pi)
                if displ_proj_strain_df.proj_offset[i] >= 0:
                    vector_proj_length = math.sqrt(displ_proj_strain_df.proj_offset[i] ** 2 +
                                               displ_proj_strain_df.z_offset[i] ** 2)
                else:
                    vector_proj_length = - (math.sqrt(displ_proj_strain_df.proj_offset[i] ** 2 +
                                                  displ_proj_strain_df.z_offset[i] ** 2))
                if displ_proj_strain_df.proj_offset[i] != 0:
                    angle_displ = math.atan(displ_proj_strain_df.z_offset[i] / displ_proj_strain_df.proj_offset[i])
                else:
                    angle_displ = 0
                angle_diff = abs(angle_displ - angle_to_toe)
                strain = (vector_proj_length * math.cos(angle_diff)) / (dist_to_toe)
                strain_list_dic.append(strain)
            elif PROFILE_DIR == 'left-right' and displ_proj_strain_df.meas_x_preEQ[i] > toe_x_value:
                strain = 0
                strain_list_dic.append(strain)
                angle_to_toe = 0
                angle_to_toe_list_deg.append(angle_to_toe)
            elif PROFILE_DIR == 'right-left' and displ_proj_strain_df.meas_x_preEQ[i] > toe_x_value:
                x_dist_to_toe = abs(toe_x_value - displ_proj_strain_df.meas_x_preEQ[i])
                z_dist_to_toe = abs(toe_z_value - displ_proj_strain_df.z_2015[i])
                dist_to_toe = math.sqrt(x_dist_to_toe**2 + z_dist_to_toe**2)
                angle_to_toe = math.atan(-1 * z_dist_to_toe/x_dist_to_toe)
                angle_to_toe_list.append(angle_to_toe)
                angle_to_toe_list_deg.append(angle_to_toe *180/math.pi)
                if displ_proj_strain_df.proj_offset[i] >= 0:
                    vector_proj_length = math.sqrt(displ_proj_strain_df.proj_offset[i] ** 2 +
                                               displ_proj_strain_df.z_offset[i] ** 2)
                else:
                    vector_proj_length = - (math.sqrt(displ_proj_strain_df.proj_offset[i] ** 2 +
                                                  displ_proj_strain_df.z_offset[i] ** 2))
                if displ_proj_strain_df.proj_offset[i] != 0:
                    angle_displ = math.atan(displ_proj_strain_df.z_offset[i] / displ_proj_strain_df.proj_offset[i])
                else:
                    angle_displ = 0
                angle_diff = abs(angle_displ - angle_to_toe)
                strain = (vector_proj_length * math.cos(angle_diff)) / (dist_to_toe)
                strain_list_dic.append(strain)
            elif PROFILE_DIR == 'right-left' and displ_proj_strain_df.meas_x_preEQ[i] < toe_x_value:
                strain = 0
                strain_list_dic.append(strain)
                angle_to_toe = 0
                angle_to_toe_list_deg.append(angle_to_toe)
        max_strain_dic = max(strain_list_dic)
        print('Strain from DIC measurements calculated. Maximum strain, method 1 = {:.3f}'.format(max_strain_dic))
        displ_proj_strain_df['strain_dic'] = strain_list_dic
        displ_proj_strain_df['angle_to_toe'] = angle_to_toe_list_deg
    return displ_proj_strain_df


def get_strain_method2(displ_proj_df, crack_x_locations, toe_x_value, toe_z_value):
    toe_x_2015 = toe_x_value
    toe_z_2015 = toe_z_value
    vector_length2D_proj_selected = []
    displ_angle_list = []
    if PROFILE_DIR == 'left-right':
        for i in range(0, len(displ_proj_df)):
            if displ_proj_df.meas_x_preEQ[i] >= min(crack_x_locations):
                vector_length2D_proj_selected.append(displ_proj_df.vector_length2D_proj[i])
                if displ_proj_df.meas_x_postEQ[i]-displ_proj_df.meas_x_preEQ[i] != 0:
                    displ_angle = math.atan(displ_proj_df.z_offset[i]/abs(displ_proj_df.meas_x_postEQ[i]-displ_proj_df.meas_x_preEQ[i]))
                else:
                    displ_angle = 0
                displ_angle_list.append(displ_angle)
        mean_displ_length = statistics.median(vector_length2D_proj_selected)
        mean_displ_angle = statistics.median(displ_angle_list)
        toe_x_2017 = toe_x_2015 + math.cos(mean_displ_angle) * 0.5 * mean_displ_length
        toe_z_2017 = toe_z_2015 + math.sin(mean_displ_angle) * 0.5 * mean_displ_length
    elif PROFILE_DIR == 'right-left':
        for i in range(0, len(displ_proj_df)):
            if displ_proj_df.meas_x_preEQ[i] <= max(crack_x_locations):
                vector_length2D_proj_selected.append(displ_proj_df.vector_length2D_proj[i])
                if displ_proj_df.meas_x_postEQ[i]-displ_proj_df.meas_x_preEQ[i] != 0:
                    displ_angle = math.atan(displ_proj_df.z_offset[i]/abs(displ_proj_df.meas_x_postEQ[i]-displ_proj_df.meas_x_preEQ[i]))
                else:
                    displ_angle = 0
                displ_angle_list.append(displ_angle)
        mean_displ_length = statistics.median(vector_length2D_proj_selected)
        mean_displ_angle = statistics.median(displ_angle_list)
        toe_x_2017 = toe_x_2015 - math.cos(mean_displ_angle) * 0.5 * mean_displ_length
        toe_z_2017 = toe_z_2015 + math.sin(mean_displ_angle) * 0.5 * mean_displ_length
    strain_list = []
    for i in range(0, len(displ_proj_df)):
        if displ_proj_df.meas_x_preEQ[i] >= min(crack_x_locations) and PROFILE_DIR == 'left-right':
            if displ_proj_df.meas_x_preEQ[i] < toe_x_value:
                x_dist_to_toe_2015 = toe_x_2015 - displ_proj_df.meas_x_preEQ[i]
                z_dist_to_toe_2015 = toe_z_2015 - displ_proj_df.z_2015[i]
                dist_to_toe_2015 = math.sqrt(x_dist_to_toe_2015 ** 2 + z_dist_to_toe_2015 ** 2)
                x_dist_to_toe_2017 = toe_x_2017 - displ_proj_df.meas_x_postEQ[i]
                z_dist_to_toe_2017 = toe_z_2017 - displ_proj_df.z_2017[i]
                dist_to_toe_2017 = math.sqrt(x_dist_to_toe_2017 ** 2 + z_dist_to_toe_2017 ** 2)
                strain = (dist_to_toe_2015 - dist_to_toe_2017)/ dist_to_toe_2015
                strain_list.append(strain)
            elif displ_proj_df.meas_x_preEQ[i] > toe_x_value:
                strain = 0
                strain_list.append(strain)
        elif displ_proj_df.meas_x_preEQ[i] <= max(crack_x_locations) and PROFILE_DIR == 'right-left':
            if displ_proj_df.meas_x_preEQ[i] > toe_x_value:
                x_dist_to_toe_2015 = toe_x_2015 - displ_proj_df.meas_x_preEQ[i]
                z_dist_to_toe_2015 = toe_z_2015 - displ_proj_df.z_2015[i]
                dist_to_toe_2015 = math.sqrt(x_dist_to_toe_2015 ** 2 + z_dist_to_toe_2015 ** 2)
                x_dist_to_toe_2017 = toe_x_2017 - displ_proj_df.meas_x_postEQ[i]
                z_dist_to_toe_2017 = toe_z_2017 - displ_proj_df.z_2017[i]
                dist_to_toe_2017 = math.sqrt(x_dist_to_toe_2017 ** 2 + z_dist_to_toe_2017 ** 2)
                strain = (dist_to_toe_2015 - dist_to_toe_2017)/ dist_to_toe_2015
                strain_list.append(strain)
            elif displ_proj_df.meas_x_preEQ[i] < toe_x_value:
                strain = 0
                strain_list.append(strain)
        else:
            strain = 0
            strain_list.append(strain)
    max_strain_dic = max(strain_list)
    print('Strain from DIC measurements calculated. Maximum strain, method 2 = {:.3f}'.format(max_strain_dic))
    displ_proj_df['strain_dic_m2'] = strain_list
    return displ_proj_df, toe_x_2017, toe_z_2017


def print_strain_results_method1(displ_proj_strain_df, toe_x_value, toe_z_value):
    """ Prints angle to toe values for maximum and last strain values for strain calculation method 1"""
    max_displ = max(displ_proj_strain_df.proj_offset)
    print('Maximum displacement = {:.1f}'.format(max_displ))
    max_strain = max(displ_proj_strain_df.strain_dic)
    row0 = (displ_proj_strain_df.loc[displ_proj_strain_df['strain_dic'] == max_strain]).index
    meas_x_max_strain = (displ_proj_strain_df.loc[row0, 'meas_x_preEQ']).values
    print('Distance along profile with max strain (method 1) = {:.1f} m'.format(meas_x_max_strain[0]))
    angle_to_toe_max_strain = (displ_proj_strain_df.loc[row0, 'angle_to_toe']).values
    print('Angle to toe at maximum strain value (method 1) = {:.1f} deg'.format(angle_to_toe_max_strain[0]))
    if PROFILE_DIR == 'left-right':
        meas_x_max = max(displ_proj_strain_df.meas_x_preEQ)
        row1 = (displ_proj_strain_df.loc[displ_proj_strain_df['meas_x_preEQ'] == meas_x_max]).index
        angle_to_toe_x_max = (displ_proj_strain_df.loc[row1, 'angle_to_toe']).values
        print('Angle to toe at last strain measurement (method 1) = {:.1f} deg'.format(angle_to_toe_x_max[0]))
    elif PROFILE_DIR == 'right-left':
        meas_x_max = min(displ_proj_strain_df.meas_x_preEQ)
        row1 = (displ_proj_strain_df.loc[displ_proj_strain_df['meas_x_preEQ'] == meas_x_max]).index
        angle_to_toe_x_max = (displ_proj_strain_df.loc[row1, 'angle_to_toe']).values
        print('Angle to toe at last strain measurement (method 1) = {:.1f} deg'.format(angle_to_toe_x_max[0]))


def print_strain_results_method2(displ_proj_strain_df, toe_x_value, toe_z_value):
    """ Prints angle to toe values for maximum and last strain values for strain calculation method 2"""
    max_strain = max(displ_proj_strain_df.strain_dic_m2)
    row2 = (displ_proj_strain_df.loc[displ_proj_strain_df['strain_dic_m2'] == max_strain]).index
    meas_x_max_strain = (displ_proj_strain_df.loc[row2, 'meas_x_preEQ']).values
    print('Distance along profile with max strain (method 2) = {:.1f} m'.format(meas_x_max_strain[0]))
    z_2015_max_strain = (displ_proj_strain_df.loc[row2, 'z_2015']).values
    x_dist_to_toe = abs(meas_x_max_strain[0] - toe_x_value)
    z_dist_to_toe = abs(z_2015_max_strain[0] - toe_z_value)
    angle_to_toe = (math.atan(-1 * z_dist_to_toe / x_dist_to_toe)) * 180 / math.pi
    print('Angle to toe at maximum strain value (method 2) = {:.1f} deg'.format(angle_to_toe))
    if PROFILE_DIR == 'left-right':
        meas_x_max = max(displ_proj_strain_df.meas_x_preEQ)
        row3 = (displ_proj_strain_df.loc[displ_proj_strain_df['meas_x_preEQ'] == meas_x_max]).index
        z_2015_max_x = (displ_proj_strain_df.loc[row3, 'z_2015']).values
        x_dist_to_toe_x_max = (toe_x_value - meas_x_max)
        z_dist_to_toe_x_max = abs(toe_z_value - z_2015_max_x[0])
        if x_dist_to_toe_x_max > 0:
            angle_to_toe_x_max = (math.atan(-1 * z_dist_to_toe_x_max / x_dist_to_toe_x_max)) * 180 / math.pi
        else:
            angle_to_toe_x_max = 0
        print('Angle to toe at last strain measurement (method 2) = {:.1f} deg'.format(angle_to_toe_x_max))
    elif PROFILE_DIR == 'right-left':
        meas_x_max = min(displ_proj_strain_df.meas_x_preEQ)
        row3 = (displ_proj_strain_df.loc[displ_proj_strain_df['meas_x_preEQ'] == meas_x_max]).index
        z_2015_max_x = (displ_proj_strain_df.loc[row3, 'z_2015']).values
        x_dist_to_toe_x_max = meas_x_max - toe_x_value
        z_dist_to_toe_x_max = abs(z_2015_max_x[0] - toe_z_value)
        if x_dist_to_toe_x_max > 0:
            angle_to_toe_x_max = (math.atan(-1 * z_dist_to_toe_x_max / x_dist_to_toe_x_max)) * 180 / math.pi
        else:
            angle_to_toe_x_max = 0
        print('Angle to toe at last strain measurement (method 2) = {:.1f} deg'.format(angle_to_toe_x_max))


def get_field_displ_df(profile_route):
    field_displ_df = pd.DataFrame()
    if SITE_FIELD_DISPL != '':
        field_points_proj = OUTPUT_GDB + '/field_points_proj'
        arcpy.sa.ExtractMultiValuesToPoints(SITE_FIELD_DISPL, [[POST_EQ_DSM, 'z_2017']], 'NONE')
        arcpy.LocateFeaturesAlongRoutes_lr(in_features=SITE_FIELD_DISPL, in_routes=profile_route,
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


def get_strain_field(field_displ_df, toe_x_value, toe_z_value):
    """ Calculates 1D strain along profile for field measurements """
    field_strain_df = field_displ_df
    if CALCULATE_STRAIN == 1:
        if SITE_FIELD_DISPL != '':
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
    else:
        print('Strain from field measurements not calculated.')
    return field_strain_df


def filter_outliers(displ_proj_strain_df):
    outlier_list = [False] * len(displ_proj_strain_df)
    proj_offset_ind =displ_proj_strain_df.columns.get_loc('proj_offset')
    #strain_ind = displ_proj_strain_df.columns.get_loc('strain_dic')
    for i in range(0, len(displ_proj_strain_df)):
        if displ_proj_strain_df.iloc[i, proj_offset_ind] < -1:
            outlier_list[i] = True
    #for i in range(1, len(displ_proj_strain_df)-1):
        #mov_avg = (displ_proj_strain_df.iloc[i-1, strain_ind] + displ_proj_strain_df.iloc[i+1, strain_ind])/2
        #mov_diff = abs(displ_proj_strain_df.iloc[i-1, strain_ind] - displ_proj_strain_df.iloc[i+1, strain_ind])
        #if displ_proj_strain_df.iloc[i, strain_ind] > (mov_avg + 20 * mov_diff) or \
            #displ_proj_strain_df.iloc[i, strain_ind] < (mov_avg - 20 * mov_diff):
            #outlier_list[i] = True
    displ_proj_strain_df['outlier'] = outlier_list
    displ_proj_strain_filt_df = displ_proj_strain_df[displ_proj_strain_df['outlier'] == False]
    return displ_proj_strain_filt_df


def get_strain_grad(displ_proj_strain_filt_df):
    displ_proj_strain_filt_sort_df = displ_proj_strain_filt_df.sort_values(by='meas_x_preEQ')
    strain_grad_list = []
    meas_x_strain_grad = []
    meas_x_ind = displ_proj_strain_filt_sort_df.columns.get_loc('meas_x_preEQ')
    strain_ind = displ_proj_strain_filt_sort_df.columns.get_loc('strain_dic')
    for i in range(0, (len(displ_proj_strain_filt_sort_df)-1)):
        x_value = (displ_proj_strain_filt_sort_df.iloc[i+1, meas_x_ind] + displ_proj_strain_filt_sort_df.iloc[i, meas_x_ind]) / 2
        meas_x_strain_grad.append(x_value)
        delta_x = displ_proj_strain_filt_sort_df.iloc[i+1, meas_x_ind] - displ_proj_strain_filt_sort_df.iloc[i, meas_x_ind]
        strain_delta = displ_proj_strain_filt_sort_df.iloc[i+1, strain_ind] - displ_proj_strain_filt_sort_df.iloc[i, strain_ind]
        if delta_x != 0:
            strain_grad = strain_delta / delta_x
        else:
            strain_grad = 0
        strain_grad_list.append(strain_grad)
    indices = []
    for row in displ_proj_strain_filt_sort_df.index:
        indices.append(row)
    strain_grad_data = {'meas_x_strain_grad': meas_x_strain_grad, 'strain_grad':strain_grad_list}
    strain_grad_df = pd.DataFrame(strain_grad_data)
    strain_grad_df.index = indices[:-1]
    displ_proj_strain_grad_filt_df = pd.concat([displ_proj_strain_filt_sort_df, strain_grad_df], axis=1)
    return displ_proj_strain_grad_filt_df


def get_strain_grad_sensitivity(sensitivity_filt_df, toe_x_list):
    sensitivity_filt_sort_df = sensitivity_filt_df.sort_values(by='meas_x_preEQ')
    meas_x_strain_grad_list = []
    meas_x_ind = sensitivity_filt_sort_df.columns.get_loc('meas_x_preEQ')
    for i in range(0, (len(sensitivity_filt_sort_df)-1)):
        x_value = (sensitivity_filt_sort_df.iloc[i + 1, meas_x_ind] + sensitivity_filt_sort_df.iloc[i, meas_x_ind]) / 2
        meas_x_strain_grad_list.append(x_value)
    strain_grad_df = pd.DataFrame({'meas_x_strain_grad': meas_x_strain_grad_list})
    indices = []
    for row in sensitivity_filt_sort_df.index:
        indices.append(row)
    strain_grad_df.index = indices[:-1]
    for x in toe_x_list:
        strain_grad_list = []
        strain_ind = sensitivity_filt_sort_df.columns.get_loc('strain_dic_{:.1f}m'.format(x))
        for i in range(0, (len(sensitivity_filt_sort_df)-1)):
            delta_x = sensitivity_filt_sort_df.iloc[i+1, meas_x_ind] - sensitivity_filt_sort_df.iloc[i, meas_x_ind]
            strain_delta = sensitivity_filt_sort_df.iloc[i+1, strain_ind] - sensitivity_filt_sort_df.iloc[i, strain_ind]
            if delta_x != 0:
                strain_grad = strain_delta / delta_x
            else:
                strain_grad = 0
            strain_grad_list.append(strain_grad)
        strain_grad_df['strain_grad_{:.1f}m'.format(x)] = strain_grad_list
    sensitivity_strain_grad_filt_df = pd.concat([sensitivity_filt_sort_df, strain_grad_df], axis=1)
    return sensitivity_strain_grad_filt_df


def get_strain_grad_sensitivity_m2(sensitivity_filt_df, toe_x_list):
    sensitivity_filt_sort_df = sensitivity_filt_df.sort_values(by='meas_x_preEQ')
    meas_x_strain_grad_list = []
    meas_x_ind = sensitivity_filt_sort_df.columns.get_loc('meas_x_preEQ')
    for i in range(0, (len(sensitivity_filt_sort_df)-1)):
        x_value = (sensitivity_filt_sort_df.iloc[i + 1, meas_x_ind] + sensitivity_filt_sort_df.iloc[i, meas_x_ind]) / 2
        meas_x_strain_grad_list.append(x_value)
    strain_grad_df = pd.DataFrame({'meas_x_strain_grad': meas_x_strain_grad_list})
    indices = []
    for row in sensitivity_filt_sort_df.index:
        indices.append(row)
    strain_grad_df.index = indices[:-1]
    for x in toe_x_list:
        strain_grad_list = []
        strain_ind = sensitivity_filt_sort_df.columns.get_loc('strain_dic_m2_{:.1f}m'.format(x))
        for i in range(0, (len(sensitivity_filt_sort_df)-1)):
            delta_x = sensitivity_filt_sort_df.iloc[i+1, meas_x_ind] - sensitivity_filt_sort_df.iloc[i, meas_x_ind]
            strain_delta = sensitivity_filt_sort_df.iloc[i+1, strain_ind] - sensitivity_filt_sort_df.iloc[i, strain_ind]
            if delta_x != 0:
                strain_grad = strain_delta / delta_x
            else:
                strain_grad = 0
            strain_grad_list.append(strain_grad)
        strain_grad_df['strain_grad_m2_{:.1f}m'.format(x)] = strain_grad_list
    sensitivity_strain_grad_filt_df = pd.concat([sensitivity_filt_sort_df, strain_grad_df], axis=1)
    print(sensitivity_strain_grad_filt_df.columns)
    return sensitivity_strain_grad_filt_df