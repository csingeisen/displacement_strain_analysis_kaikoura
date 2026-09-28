import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from dic_global_constants import *
import pandas
import math

def create_displ_strain_plot(displ_proj_strain_df, displ_proj_strain_grad_filt_df,
                field_strain_df, toe_x_value, crack_x_locations, failure_location,sensitivity_strain_grad_filt_df, toe_x_list):
    fig1, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 7))
    if CATASTROPHIC_FAILURE != '' and PROFILE_DIR == 'left-right':
        max_x_graph = max(failure_location[0] + 5, toe_x_value + 5)
    elif PROFILE_DIR == 'left-right':
        max_x_graph = toe_x_value + 5
    elif PROFILE_DIR == 'right-left':
        max_x_graph = max(displ_proj_strain_grad_filt_df.meas_x_preEQ)
        min_x_graph = min(toe_x_list)-5
    # Create displacement subplot
    max_displ = max(displ_proj_strain_df['proj_offset'])
    min_displ = min(displ_proj_strain_df['proj_offset'])
    ax[0].scatter(displ_proj_strain_df['meas_x_preEQ'], displ_proj_strain_df['proj_offset'],
                      s=8, color='salmon', marker='x',
                      label='Projected displacement vector magnitudes in profile plane (from DIC) - removed outliers')
    ax[0].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], displ_proj_strain_grad_filt_df['proj_offset'],
                      s=8, color='red', label='Projected displacement vector magnitudes in profile plane (from DIC)')
    for x in crack_x_locations:
        ax[0].plot([x, x], [min_displ, max_displ+5], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax[0].plot([failure_location[0], failure_location[0]], [min_displ, max_displ+5], color='black',
                        linestyle='--', linewidth='1', label='catastrophic failure')
    if SITE_FIELD_DISPL != '':
        ax[0].scatter(field_strain_df['meas_x_field'], field_strain_df['cum_3D_mag'],
                          color='black', s=8,
                          label='Displacement magnitude 3D (from field measurements)')
    ax[0].set_ylabel('displacement [m]', fontsize=10)
    if PROFILE_DIR == 'left-right':
        ax[0].set_xlim(0, max_x_graph)
    elif PROFILE_DIR == 'right-left':
        ax[0].set_xlim(0, max_x_graph)
    ax[0].set_ylim(0, max_displ+1) #
    ax[0].tick_params(labelsize=10)
    ax[0].legend(loc='lower left', fontsize=10, bbox_to_anchor=(1,-0.1))
    # Create strain subplot
    if PROFILE_DIR == 'left-right':
        max_strain_graph = max(sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(toe_x_list[0])])
        min_strain_graph = min(sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(toe_x_list[0])])
    else:
        max_strain_graph = max(sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(toe_x_list[-1])])
        min_strain_graph = min(sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(toe_x_list[-1])])
    for x in crack_x_locations:
        ax[1].plot([x, x], [min_strain_graph, max_strain_graph + 0.005], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax[1].plot([failure_location[0], failure_location[0]], [min_strain_graph, max_strain_graph + 0.005], color='black',
                linestyle='--', linewidth='1')
    colors0 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    colors1 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        max_strain = (sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(x)]).max()
        max_strain_str = str('{:.3f}'.format(max_strain))
        ax[1].scatter(sensitivity_strain_grad_filt_df['meas_x_preEQ'],
                      sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(x)], s=8, color=next(colors0),
                      label='Method 1: max strain = {}'.format(max_strain_str))
        ax[1].plot([0, max_x_graph], [max_strain, max_strain], color=next(colors1), linestyle='dashdot', linewidth=0.5)
    # colors0 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    # colors1 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    # for x in toe_x_list:
    #     max_strain = (sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(x)]).max()
    #     max_strain_str = str('{:.3f}'.format(max_strain))
    #     ax[1].scatter(sensitivity_strain_grad_filt_df['meas_x_preEQ'],
    #                   sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(x)], s=8, color=next(colors0),
    #                   marker='x', alpha=0.5,
    #                   label='Method 2: max strain = {}'.format(max_strain_str))
    #     ax[1].plot([0, max_x_graph], [max_strain, max_strain], color=next(colors1), linestyle='dashdot', linewidth=0.5)
    colors = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        # ax.plot([x, x], [max_strain_graph + 0.001, 0], color=next(colors), linewidth=0.5)
        ax[1].plot([x, x], [max_strain_graph + 0.005, min_strain_graph], color=next(colors), linewidth=0.5)
    ax[1].set_ylabel('strain [-]', fontsize=10)
    ax[1].set_xlabel('distance along profile [m]', fontsize=10)
    ax[1].set_ylim(-0.001, max_strain_graph + 0.005) # max_strain_graph + 0.005
    ax[1].set_xlim(0, max_x_graph)
    ax[1].tick_params(labelsize=10)
    plt.show()


def plot_strain_overview(displ_proj_strain_df, displ_proj_strain_grad_filt_df,
                field_strain_df, toe_x_value, crack_x_locations, failure_location):
    """ Plots 3 subplots showing projected displacement magnitudes, strain and strain gradient """
    fig1, ax = plt.subplots(nrows=3, ncols=1, figsize=(10, 8))
    if CATASTROPHIC_FAILURE != '' and PROFILE_DIR == 'left-right':
        max_x_graph = max(failure_location[0] + 5, toe_x_value + 5)
    elif PROFILE_DIR == 'left-right':
        max_x_graph = toe_x_value + 5
    elif PROFILE_DIR == 'right-left':
        max_x_graph = max(displ_proj_strain_grad_filt_df.meas_x_preEQ)
    # Create displacement subplot
    max_displ = max(displ_proj_strain_df['proj_offset'])
    min_displ = min(displ_proj_strain_df['proj_offset'])
    ax[0].scatter(displ_proj_strain_df['meas_x_preEQ'], displ_proj_strain_df['proj_offset'],
                      s=8, color='salmon', marker='x',
                      label='Projected displacement vector magnitudes in profile plane (from DIC) - removed outliers')
    ax[0].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], displ_proj_strain_grad_filt_df['proj_offset'],
                      s=8, color='red', label='Projected displacement vector magnitudes in profile plane (from DIC)')
    for x in crack_x_locations:
        ax[0].plot([x, x], [min_displ, max_displ+5], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax[0].plot([failure_location[0], failure_location[0]], [min_displ, max_displ], color='black',
                        linestyle='--', linewidth='1', label='catastrophic failure')
    if SITE_FIELD_DISPL != '':
        ax[0].scatter(field_strain_df['meas_x_field'], field_strain_df['cum_3D_mag'],
                          color='black', s=8,
                          label='Displacement magnitude 3D (from field measurements)')
    ax[0].set_ylabel('displacement [m]', fontsize=10)
    ax[0].set_xlim(0, 205)
    ax[0].set_ylim(-5, 12)
    ax[0].tick_params(labelsize=10)
    ax[0].legend(loc='lower left', fontsize=10, bbox_to_anchor=(1,-0.1))
    # Create strain subplot
    max_strain = max(displ_proj_strain_df['strain_dic'])
    min_strain = min(displ_proj_strain_df['strain_dic'])
    x_label = str('{:.0f}'.format(toe_x_value))
    max_strain_str = str('{:.3f}'.format(max_strain))
    max_strain_m2 = max(displ_proj_strain_df['strain_dic_m2'])
    max_strain_m2_str = str('{:.3f}'.format(max_strain_m2))
    ax[1].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], displ_proj_strain_grad_filt_df['strain_dic'],
                  s=8, color='teal',
                  label='Method 1: max strain = {} with toe location at {} m'.format(max_strain_str, x_label))
    ax[1].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], displ_proj_strain_grad_filt_df['strain_dic_m2'],
                  marker='x', s=8, color='cadetblue',
                  label='Method 2: max strain = {} with toe location at {} m'.format(max_strain_m2_str, x_label))
    ax[1].plot([toe_x_value, toe_x_value], [min_strain, max_strain], color='black', label='toe location')
    for x in crack_x_locations:
        ax[1].plot([x, x], [min_strain, max_strain], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax[1].plot([failure_location[0], failure_location[0]], [min_strain, max_strain], color='black',
                   linestyle='--', linewidth='1', label='catastrophic_failure')
    if SITE_FIELD_DISPL != '':
        ax[1].scatter(field_strain_df['meas_x_field'], field_strain_df['strain_field'], color='black', s=8,
                      label='Field measurements (Method 1): max strain = {:.3f}'.format(
                          max(field_strain_df.strain_field)))
    ax[1].set_ylabel('strain', fontsize=8)
    ax[1].set_xlim(0, max_x_graph)
    ax[1].set_ylim(-0.001, 0.1) # max_strain + 0.1 * (max_strain)
    ax[1].tick_params(labelsize=8)
    ax[1].legend(loc='lower right', fontsize=8)
    # Get values for slope and strain index plots
    angle_to_toe_pos = []
    strain_div_slope = []
    strain_mult_slope = []
    for i in range(0, len(displ_proj_strain_grad_filt_df)):
        slope_col = displ_proj_strain_grad_filt_df.columns.get_loc('angle_to_toe')
        strain_col = displ_proj_strain_grad_filt_df.columns.get_loc('strain_dic')
        angle_pos = (-1) * displ_proj_strain_grad_filt_df.iloc[i, slope_col]
        angle_to_toe_pos.append(angle_pos)
        if angle_pos != 0:
            strain_ind1 = displ_proj_strain_grad_filt_df.iloc[i, strain_col] / angle_pos
        else:
            strain_ind1 = 0
        strain_div_slope.append(strain_ind1)
        strain_ind2 = displ_proj_strain_grad_filt_df.iloc[i, strain_col] * angle_pos
        strain_mult_slope.append(strain_ind2)
    min_strain_ind1 = min(strain_div_slope)
    max_strain_ind1 = max(strain_div_slope)
    min_strain_ind2 = min(strain_mult_slope)
    max_strain_ind2 = max(strain_mult_slope)
    # Create slope subplot
    max_angle = max(angle_to_toe_pos)
    min_angle = min(angle_to_toe_pos)
    ax[2].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], angle_to_toe_pos, color='green', s=8,
                  label='angle to toe in [°]')
    for x in crack_x_locations:
        ax[2].plot([x, x], [min_angle, max_angle], color='dimgray', linestyle='--', linewidth='0.5')
    ax[2].plot([toe_x_value, toe_x_value], [min_angle, max_angle], color='black', label='toe location')
    if CATASTROPHIC_FAILURE != '':
        ax[2].plot([failure_location[0], failure_location[0]], [min_angle, max_angle], color='black',
                   linestyle='--', linewidth='1', label='catastrophic_failure')
    ax[2].set_ylabel('angle to toe in [°]', fontsize=8)
    ax[2].set_xlim(0, max_x_graph)
    ax[2].set_ylim(min_angle - 1, max_angle + 1)
    ax[2].tick_params(labelsize=8)
    ax[2].legend(loc='lower right', fontsize=8)
    # Create plot showing strain/ slope values along profile
    fig2, ax2 = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))
    ax2[0].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], strain_div_slope, color='black', s=8)
    for x in crack_x_locations:
        ax2[0].plot([x, x], [min_strain_ind1, max_strain_ind1], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax2[0].plot([failure_location[0], failure_location[0]], [min_strain_ind1, min_strain_ind1], color='black',
            linestyle='--', linewidth='1', label='catastrophic_failure')
    ax2[0].set_xlim(0, toe_x_value)
    ax2[0].set_ylim(min_strain_ind1, max_strain_ind1)
    ax2[0].set_ylabel('strain/slope (angle to toe [°])', fontsize=8)
    ax2[0].tick_params(labelsize=8)
    ax2[0].legend(loc='best', fontsize=8)
    # Create plot showing strain * slope values along profile
    ax2[1].scatter(displ_proj_strain_grad_filt_df['meas_x_preEQ'], strain_mult_slope, color='black', s=8, marker='x')
    for x in crack_x_locations:
        ax2[1].plot([x, x], [min_strain_ind2, max_strain_ind2], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax2[1].plot([failure_location[0], failure_location[0]], [min_strain_ind2, min_strain_ind2], color='black',
            linestyle='--', linewidth='1', label='catastrophic_failure')
    ax2[1].set_xlim(0, toe_x_value)
    ax2[1].set_ylim(min_strain_ind2, max_strain_ind2)
    ax2[1].set_ylabel('strain * slope (angle to toe [°])', fontsize=8)
    ax2[1].tick_params(labelsize=8)
    ax2[1].legend(loc='best', fontsize=8)
    if CATASTROPHIC_FAILURE != '':
        max_strain = max(displ_proj_strain_grad_filt_df.strain_dic)
        row = (displ_proj_strain_grad_filt_df.loc[displ_proj_strain_df['strain_dic'] == max_strain]).index
        meas_x_max_strain = (displ_proj_strain_grad_filt_df.loc[row, 'meas_x_preEQ']).values
        dist_max_fail = abs(failure_location[0] - meas_x_max_strain[0])
        print('Distance between maximum strain measurement and failure = {:.1f} m'.format(dist_max_fail))
        if PROFILE_DIR == 'left-right':
            meas_x_max = max(displ_proj_strain_grad_filt_df.meas_x_preEQ)
            dist_x_max_fail = failure_location[0] - meas_x_max
            print('Distance between last strain measurement and failure = {:.1f} m'.format(dist_x_max_fail))
    plt.show()


def plot_strain_sensitivity(sensitivity_strain_grad_filt_df, sensitivity_field_df, toe_x_list,
                            crack_x_locations, failure_location):
    fig1, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
    if CATASTROPHIC_FAILURE != '' and PROFILE_DIR == 'left-right':
        max_x_graph = max(failure_location[0] + 5, max(toe_x_list) + 5)
    elif PROFILE_DIR == 'left-right':
        max_x_graph = max(toe_x_list) + 5
    elif PROFILE_DIR == 'right-left':
        max_x_graph = max(sensitivity_strain_grad_filt_df.meas_x_preEQ)
    max_strain_graph = max(sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(toe_x_list[0])])
    min_strain_graph = min(sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(toe_x_list[0])])
    for x in crack_x_locations:
        ax.plot([x, x], [min_strain_graph, max_strain_graph + 0.005], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax.plot([failure_location[0], failure_location[0]], [min_strain_graph, max_strain_graph + 0.005], color='black',
                linestyle='--', linewidth='1')
    colors0 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    colors1 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        max_strain = (sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(x)]).max()
        max_strain_str = str('{:.3f}'.format(max_strain))
        ax.scatter(sensitivity_strain_grad_filt_df['meas_x_preEQ'],
                      sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(x)], s=8, color=next(colors0),
                      label='Method 1: max strain = {}'.format(max_strain_str))
        ax.plot([0, max_x_graph], [max_strain, max_strain], color=next(colors1), linestyle='dashdot', linewidth=0.5)
    colors0 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    colors1 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    # for x in toe_x_list:
    #     max_strain = (sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(x)]).max()
    #     max_strain_str = str('{:.3f}'.format(max_strain))
    #     ax.scatter(sensitivity_strain_grad_filt_df['meas_x_preEQ'],
    #                   sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(x)], s=8, color=next(colors0),
    #                   marker='x', alpha=0.5,
    #                   label='Method 2: max strain = {}'.format(max_strain_str))
    #     ax.plot([0, max_x_graph], [max_strain, max_strain], color=next(colors1), linestyle='dashdot', linewidth=0.5)
    colors = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        #ax.plot([x, x], [max_strain_graph + 0.001, 0], color=next(colors), linewidth=0.5)
        ax.plot([x, x], [max_strain_graph + 0.005, min_strain_graph], color=next(colors), linewidth=0.5)
    ax.set_ylabel('strain [-]', fontsize=10)
    ax.set_xlabel('distance along profile [m]', fontsize=10)
    ax.set_ylim(-0.01, max_strain_graph + 0.005)
    ax.set_xlim(0, max_x_graph)
    ax.tick_params(labelsize=10)

    fig2, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
    if CATASTROPHIC_FAILURE != '' and PROFILE_DIR == 'left-right':
        max_x_graph = max(failure_location[0] + 5, max(toe_x_list) + 5)
    elif PROFILE_DIR == 'left-right':
        max_x_graph = max(toe_x_list) + 5
    elif PROFILE_DIR == 'right-left':
        max_x_graph = max(sensitivity_strain_grad_filt_df.meas_x_preEQ)
    max_strain_graph = max(sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(toe_x_list[0])])
    min_strain_graph = min(sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(toe_x_list[0])])
    for x in crack_x_locations:
        ax.plot([x, x], [min_strain_graph, max_strain_graph + 0.005], color='dimgray', linestyle='--', linewidth='0.5')
    if CATASTROPHIC_FAILURE != '':
        ax.plot([failure_location[0], failure_location[0]], [min_strain_graph, max_strain_graph + 0.005], color='black',
                linestyle='--', linewidth='1')
    colors0 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    colors1 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        max_strain = (sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(x)]).max()
        max_strain_str = str('{:.3f}'.format(max_strain))
        ax.scatter(sensitivity_strain_grad_filt_df['meas_x_preEQ'],
                   sensitivity_strain_grad_filt_df['strain_dic_{:.1f}m'.format(x)], s=8, color=next(colors0),
                   label='Method 1: max strain = {}'.format(max_strain_str))
        ax.plot([0, max_x_graph], [max_strain, max_strain], color=next(colors1), linestyle='dashdot', linewidth=0.5)
    colors0 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    colors1 = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        max_strain = (sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(x)]).max()
        max_strain_str = str('{:.3f}'.format(max_strain))
        ax.scatter(sensitivity_strain_grad_filt_df['meas_x_preEQ'],
                   sensitivity_strain_grad_filt_df['strain_dic_m2_{:.1f}m'.format(x)], s=8, color=next(colors0),
                   marker='x', alpha=0.5,
                   label='Method 2: max strain = {}'.format(max_strain_str))
        ax.plot([0, max_x_graph], [max_strain, max_strain], color=next(colors1), linestyle='dashdot', linewidth=0.5)
    colors = iter(cm.winter(np.linspace(0, 1, len(toe_x_list))))
    for x in toe_x_list:
        ax.plot([x, x], [max_strain_graph + 0.005, min_strain_graph + 0.005], color=next(colors), linewidth=0.5)
    ax.set_ylabel('strain [-]', fontsize=10)
    ax.set_xlabel('distance along profile [m]', fontsize=10)
    ax.set_xlim(0, max_x_graph)
    ax.tick_params(labelsize=10)
    legend = ax.legend(loc='lower right', fontsize=10)
    legend.get_frame().set_linewidth(0.0)
    plt.show()


def plot_strain_with_slope(displ_proj_strain_grad_filt_df):
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(10, 8))
    ax[0].scatter(displ_proj_strain_grad_filt_df.strain_dic, displ_proj_strain_grad_filt_df.angle_to_toe, marker='o',
                  s=8, color='teal')
    ax[0].scatter(displ_proj_strain_grad_filt_df.strain_dic_m2, displ_proj_strain_grad_filt_df.angle_to_toe, marker='x',
                  s=8, color='cadetblue')
    ax[0].set_ylabel('angle to toe', fontsize=8)
    ax[0].set_xlabel('strain', fontsize=8)
    ax[0].tick_params(labelsize=8)
    meas_x = []
    strain_norm_method1_list = []
    strain_norm_method2_list = []
    for i in range(0, len(displ_proj_strain_grad_filt_df)):
        strain_norm_method1 = displ_proj_strain_grad_filt_df.strain_dic/ displ_proj_strain_grad_filt_df.angle_to_toe
        strain_norm_method2 = displ_proj_strain_grad_filt_df.strain_dic_m2/ displ_proj_strain_grad_filt_df.angle_to_toe
        strain_norm_method1_list.append(strain_norm_method1)
        strain_norm_method2_list.append(strain_norm_method2)
        meas_x.append(displ_proj_strain_grad_filt_df.meas_x_preEQ)
    ax[1].scatter(meas_x, strain_norm_method1_list, marker='o', s=8, color='teal')
    ax[1].scatter(meas_x, strain_norm_method2_list, marker='x', s=8, color='cadetblue')
    ax[1].set_ylabel('strain normalised by slope', fontsize=8)
    ax[1].tick_params(labelsize=8)
    ax[2].scatter(displ_proj_strain_grad_filt_df.meas_x_preEQ, displ_proj_strain_grad_filt_df.angle_to_toe, marker='o',
                  s=8, color='black')
    ax[2].set_ylabel('angle to toe', fontsize=8)
    ax[2].set_xlabel('distance along profile line', fontsize=8)
    ax[2].tick_params(labelsize=8)

    plt.show()
