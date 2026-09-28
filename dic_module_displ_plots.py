import pandas as pd
import numpy as np
# import rasterio
# from rasterio.plot import show
# import geopandas
import matplotlib.pyplot as plt
from dic_global_constants import *


def get_toe_location(profile_route, topo_df, displ_proj_df, failure_location):
    """ Returns toe x and z value and gdb table toe_location"""
    if CALCULATE_STRAIN == 1:
        if TOE_CALC == 'shapefile':
            toe_location = OUTPUT_GDB + '/toe_location'
            arcpy.sa.ExtractMultiValuesToPoints(TOE, [[PRE_EQ_DSM, 'z_2015']], 'NONE')
            arcpy.LocateFeaturesAlongRoutes_lr(in_features=TOE, in_routes=profile_route, route_id_field='Profile',
                                       radius_or_tolerance='1 Meter', in_fields='FIELDS', out_table=toe_location)
            cursor = arcpy.da.SearchCursor(toe_location, field_names=['MEAS', 'z_2015'])
            toe_x_value = 0
            toe_z_value = 0
            for row in cursor:
                toe_x_value = row[0]
                toe_z_value = row[1]
            print('Toe location from shapefile at {:.1f} m along profile at {:.1f} m elevation.'.format(toe_x_value,
                                                                                                       toe_z_value))
            return toe_x_value, toe_z_value
        elif TOE_CALC == 'graphic':
            toe_x_location = max(topo_df.meas_x)
            toe_z_location = min(topo_df.z_2015)
            create_profile_plot(topo_df, displ_proj_df,toe_x_location, toe_z_location, failure_location)
            plt.title('Select toe location with click')
            toe_selected = plt.ginput(1)
            toe_x_value_list = [x[0] for x in toe_selected]
            toe_x_value = toe_x_value_list[0]
            toe_z_value_list = [z[1] for z in toe_selected]
            toe_z_value = toe_z_value_list[0]
            print('Toe location selected at {:.1f} m along profile at {:.1f} m elevation.'.format(toe_x_value,
                                                                                                  toe_z_value))
            return toe_x_value, toe_z_value
        elif TOE_CALC == 'numeric':
            x_value = int(input('Toe location along profile (x-value)? '))
            meas_x = topo_df['meas_x'].tolist()
            z_2015 = topo_df['z_2015'].tolist()
            n = [abs(i - x_value) for i in meas_x]
            idx = n.index(min(n))
            toe_x_value = meas_x[idx]
            toe_z_value = z_2015[idx]
            print('Toe location selected at {:.1f} m along profile at {:.1f} m elevation.'.format(toe_x_value,
                                                                                                  toe_z_value))
            return toe_x_value, toe_z_value
        else:
            print('User input not valid.')


def get_toe_x_z_sensitivity(X_VALUE, topo_df):
    meas_x = topo_df['meas_x'].tolist()
    z_2015 = topo_df['z_2015'].tolist()
    n = [abs(i - X_VALUE) for i in meas_x]
    idx = n.index(min(n))
    toe_x_value = meas_x[idx]
    toe_z_value = z_2015[idx]
    print('Toe location selected at {:.1f} m along profile at {:.1f} m elevation.'.format(toe_x_value,
                                                                                          toe_z_value))
    return toe_x_value, toe_z_value


def get_deformation_data(profile_route, topo_df):
    """ Extracts locations of mapped ground cracks and the onset of catastrophic failure along the profile line"""
    crack_x_locations = []
    failure_location = ()
    if GROUND_CRACKS != '':
        ground_cracks_proj = OUTPUT_GDB + '/ground_cracks_proj'
        intersection_points = OUTPUT_GDB + '/intersection_points'
        if arcpy.Exists(ground_cracks_proj):
            arcpy.Delete_management(ground_cracks_proj)
        if arcpy.Exists(ground_cracks_proj):
            arcpy.Delete_management(ground_cracks_proj)
        arcpy.Intersect_analysis([GROUND_CRACKS, PROFILE_LINE], intersection_points, output_type='POINT')
        arcpy.LocateFeaturesAlongRoutes_lr(intersection_points, profile_route, 'Profile', '1 Meters',
                                           out_table=ground_cracks_proj, out_event_properties='Profile POINT MEAS')
        mapped_cracks = arcpy.da.SearchCursor(ground_cracks_proj, field_names='MEAS')
        for row in mapped_cracks:
            crack_x_locations.append(row[0])
    if CATASTROPHIC_FAILURE != '':
        failure_proj = OUTPUT_GDB + '/failure_proj'
        intersection = OUTPUT_GDB + '/intersection'
        if arcpy.Exists(failure_proj):
            arcpy.Delete_management(failure_proj)
        if arcpy.Exists(intersection):
            arcpy.Delete_management(intersection)
        arcpy.Intersect_analysis([CATASTROPHIC_FAILURE, PROFILE_LINE], intersection, output_type='POINT')
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


def add_failure_surface():
    pass


def create_profile_plot(topo_df, displ_proj_df, toe_x_location, toe_z_location, failure_location):
    """ Creates plot showing a profile view of the DIC displacements"""
    if PLOT_PROFILE == 1:
        fig1, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
        #ax.scatter(toe_x_location, toe_z_location, c='black', s=10, marker='x', label='assumed landslide toe')
        ax.plot(topo_df['meas_x'], topo_df['z_2015'], c='grey', label='DSM 2015, ICP corrected', linewidth=0.5)
        #ax.plot(topo_df['meas_x'], topo_df['z_2017'], c='black', label='DSM 2017', linewidth=0.5)
        # if PROFILE_DIR == 'left-right':
        #     displ = ax.quiver(displ_proj_df['meas_x_preEQ'], displ_proj_df['z_2015'],
        #             displ_proj_df['proj_offset'], displ_proj_df['z_offset'], color='red',
        #             angles='xy', scale_units='xy', scale=0.1, width=0.0015, headwidth=6, headlength=6, headaxislength=6)
        # elif PROFILE_DIR == 'right-left':
        #     x_offset_data = []
        #     for i in range(0, len(displ_proj_df)):
        #         x_offset = displ_proj_df.proj_offset[i] * -1
        #         x_offset_data.append(x_offset)
        #     displ = ax.quiver(displ_proj_df['meas_x_preEQ'], displ_proj_df['z_2015'],
        #             x_offset_data, displ_proj_df['z_offset'], color='red',
        #             angles='xy', scale_units='xy', scale=0.1, width=0.0015, headwidth=6, headlength=6, headaxislength=6)
        # else:
        #     print('Profile direction variable not valid.')
        # ax.quiverkey(displ, X=0.05, Y=-0.2, U=20, labelpos='E',
        #              label='Displacement vectors projected to profile plane \n(with RMSE and spatial mask filter)')
        # if CATASTROPHIC_FAILURE != '':
        #     ax.scatter(failure_location[0], failure_location[1], c='black', s=10, marker='x', label='catastrophic failure')
        ax.set_aspect(1)
        ax.set_title(PROFILE_TITLE, fontsize=10)
        ax.set_ylabel('Elevation [m.a.s.l.]', fontsize=8)
        ax.set_xlabel('Distance along profile [m]', fontsize=8)
        ax.legend(loc='best', fontsize=10)
        ax.tick_params(labelsize=8)
        plt.show()


def plot_profile_sensitivity(topo_df, displ_proj_df, toe_x_list_2015, toe_z_list_2015,
                             toe_x_list_2017, toe_z_list_2017, failure_location):
    fig1, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    for i in range(0, len(toe_x_list_2015)):
        ax.scatter(toe_x_list_2015[i], toe_z_list_2015[i], c='black', s=10, marker='x')
        ax.scatter(toe_x_list_2017[i], toe_z_list_2017[i], c='grey', s=10, marker='x')
    ax.plot(topo_df['meas_x'], topo_df['z_2015'], c='black', label='DSM 2015, ICP corrected', linewidth=0.5)
    ax.plot(topo_df['meas_x'], topo_df['z_2017'], c='grey', label='DSM 2017', linewidth=0.5)
    if PROFILE_DIR == 'left-right':
        displ = ax.quiver(displ_proj_df['meas_x_preEQ'], displ_proj_df['z_2015'],
                        displ_proj_df['proj_offset'], displ_proj_df['z_offset'], color='red',
                        angles='xy', scale_units='xy', scale=1, width=0.0005, headwidth=8, headlength=8, headaxislength=8)
    elif PROFILE_DIR == 'right-left':
        x_offset_data = []
        for i in range(0, len(displ_proj_df)):
            x_offset = displ_proj_df.proj_offset[i] * -1
            x_offset_data.append(x_offset)
        displ = ax.quiver(displ_proj_df['meas_x_preEQ'], displ_proj_df['z_2015'],
                          x_offset_data, displ_proj_df['z_offset'], color='red',
                          angles='xy', scale_units='xy', scale=1, width=0.0005, headwidth=8, headlength=8,
                          headaxislength=8)
    ax.quiverkey(displ, X=0.05, Y=-0.1, U=20, labelpos='E',
                 label='Displacement vectors projected to profile plane \n(with RMSE and spatial mask filter)')
    if CATASTROPHIC_FAILURE != '':
        ax.scatter(failure_location[0], failure_location[1], c='red', s=10, marker='x')
    ax.set_aspect(1)
    ax.set_title(PROFILE_TITLE, fontsize=10)
    ax.set_ylabel('Elevation', fontsize=8)
    ax.legend(loc='best', fontsize=10)
    ax.tick_params(labelsize=8)
    plt.show()


def create_map_plot(displ_field_coords, displ_field_coords_filter_RMSE_mask, displ_field_corr_df):
    """ Creates plot showing map view of the DIC displacements"""
    if PlOT_MAP == 1:
        fig2, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
        hillshade = rasterio.open(DIC_HILLSHADE)
        plot_extent = rasterio.plot.plotting_extent(hillshade)
        hs = hillshade.read(1)
        ax.imshow(hs, extent=plot_extent, cmap='gray', alpha=1)

        ortho = rasterio.open(DIC_ORTHO)
        red = ortho.read(3)
        green = ortho.read(2)
        blue = ortho.read(1)

        def normalize(array):
            array_min, array_max = array.min(), array.max()
            return (array - array_min) / (array_max - array_min)

        red_norm = normalize(red)
        green_norm = normalize(green)
        blue_norm = normalize(blue)
        rgb = np.dstack((red_norm, green_norm, blue_norm))
        # ax.imshow(rgb, extent=plot_extent, alpha=0.3)
        # if CATASTROPHIC_FAILURE != '':
        #     profile = geopandas.read_file(CATASTROPHIC_FAILURE)
        #     profile.plot(ax=ax, color='red', linewidth=1.0, label='catastrophic failure')
        profile = geopandas.read_file(PROFILE_LINE)
        profile.plot(ax=ax, color='black', linewidth=1.0)
        displ_field_coords_table = OUTPUT + '/displ_field_coords.csv'
        arcpy.TableToTable_conversion(in_rows=displ_field_coords, out_path=OUTPUT, out_name='displ_field_coords.csv')
        displ_field_dic = pd.read_csv(displ_field_coords_table)
        displ_field_dic['y_offset_corr'] = displ_field_dic.y_offset * (-1)
        displ = ax.quiver(displ_field_dic['x_coord'], displ_field_dic['y_coord'], displ_field_dic['x_offset'],
                  displ_field_dic['y_offset_corr'], angles='xy', scale_units='xy', scale=1,
                  width=0.0015, headwidth=5, headlength=5, headaxislength=5, color='black')
        ax.quiverkey(displ, X=0.05, Y=-0.07, U=20, label='DIC displacement vectors', labelpos='E')
        if RMSE_FILTER == 1 and USE_MASK == 1:
            displ_field_coords_filter_table = OUTPUT + '/displ_field_coords_filter.csv'
            arcpy.TableToTable_conversion(in_rows=displ_field_coords_filter_RMSE_mask, out_path=OUTPUT,
                                          out_name='displ_field_coords_filter.csv')
            displ_field_dic_filter = pd.read_csv(displ_field_coords_filter_table)
            y_offset_corr = []
            for i in range(0, len(displ_field_dic_filter)):
                y_offset_corr.append(displ_field_dic_filter.y_offset[i] * (-1))
            displ_field_dic_filter['y_offset_corr'] = y_offset_corr
            displ_filt = ax.quiver(displ_field_dic_filter['x_coord'], displ_field_dic_filter['y_coord'],
                      displ_field_dic_filter['x_offset'], displ_field_dic_filter['y_offset_corr'],
                      angles='xy', scale_units='xy', scale=1,
                      width=0.0015, headwidth=5, headlength=5, headaxislength=5, color='red')
            ax.quiverkey(displ_filt, X=0.05, Y=-0.1, U=20,
                         label='DIC displacement vectors (with RMSE and spatial mask filter)', labelpos='E')
        if SITE_FIELD_DISPL != '':
            ax.scatter(displ_field_corr_df['POINT_X'], displ_field_corr_df['POINT_Y'],
                       label='field measurements', color='black', s=4, marker='o')
        ax.tick_params(labelsize=10)
        ax.ticklabel_format(axis='both', style='plain', scilimits=(0, 0), useOffset=False)
        #ax.legend(loc='lower left', fontsize=12)
        plt.tight_layout()
        plt.show()


def plot_field_dic_comparison(displ_field_corr_df):
    """ Create scatter plots comparing field and DIC displacements"""
    if PLOT_SCATTER_PLOTS == 1 and SITE_FIELD_DISPL != '':
        fig3, ax = plt.subplots(nrows=1, ncols=3, figsize=(15, 8))

        ax[0].scatter(displ_field_corr_df['MEAN_magnitude'], displ_field_corr_df['cum_H_disp'],
                      c=displ_field_corr_df['OBJECTID'])
        ax[0].plot([0, 5], [0, 5], color='black')
        ax[0].set_aspect(1)
        ax[0].set_title('Horizontal displacement', fontsize=10)
        ax[0].set_xlabel('DIC horizontal displacement in [m]', fontsize=8)
        ax[0].set_ylabel('Field horizontal displacement in [m]', fontsize=8)
        ax[0].tick_params(labelsize=8)
        ax[0].grid(True)
        ax[1].scatter(displ_field_corr_df['MEAN_z_offset'], displ_field_corr_df['cum_V_disp'],
                      c=displ_field_corr_df['OBJECTID'])
        ax[1].plot([0, -5], [0, -5], color='black')
        ax[1].set_aspect(1)
        ax[1].set_title('Vertical displacement', fontsize=10)
        ax[1].set_xlabel('DIC/DSM vertical displacement in [m]', fontsize=8)
        ax[1].set_ylabel('Field vertical displacement in [m]', fontsize=8)
        ax[1].tick_params(labelsize=8)
        ax[1].grid(True)
        ax[2].scatter(displ_field_corr_df['MEAN_mag_3D'], displ_field_corr_df['cum_3D_mag'],
                      c=displ_field_corr_df['OBJECTID'])
        ax[2].plot([0, 8], [0, 8], color='black')
        ax[2].set_aspect(1)
        ax[2].set_title('3D displacement', fontsize=10)
        ax[2].set_xlabel('DIC/DSM 3D displacement in [m]', fontsize=8)
        ax[2].set_ylabel('Field 3D displacement in [m]', fontsize=8)
        ax[2].tick_params(labelsize=8)
        ax[2].grid(True)
        plt.tight_layout()
        plt.show()


def plot_plunge(displ_proj_df):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
    pl = ax.scatter(displ_proj_df.meas_x_preEQ, displ_proj_df.displ_plunge, c=displ_proj_df.mag_3D,vmin=0,vmax=10)
    ax.set_xlabel('distance along profile [m]', fontsize=12)
    ax.set_ylabel('plunge of displacement vector [°]', fontsize=12)
    cbar = fig.colorbar(pl)
    # plt.clim(0, 10)
    cbar.set_label('3D magnitude of displacement vector [m]')
    plt.show()
