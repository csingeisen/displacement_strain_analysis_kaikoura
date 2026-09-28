""" Runfile for strain sensitivity analysis
"""
from dic_module_vector_proj import *
from dic_module_displ_plots import *
from dic_module_strain_calc import *
from dic_module_strain_plots import *
arcpy.env.workspace = PATH_DIC
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
os.chdir(PATH_DIC)
import os

def run_sensitivity():
    profile_preEQ_topo, profile_postEQ_topo = get_topo_profiles()
    displ_field_coords, displ_field_coords_postEQ = get_gis_point_layers()
    displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask = filter_point_layer(displ_field_coords)
    displ_field_selected = select_features_to_project(displ_field_coords, displ_field_coords_filter_RMSE,
                                                      displ_field_coords_filter_RMSE_mask)
    profile_route, preEQ_coord_proj_csv, postEQ_coord_proj_csv = get_pixel_locations(displ_field_selected)
    # displ_field_corr_df = join_field_dic(displ_field_selected)
    topo_df, displ_proj_df = create_dataframes(profile_preEQ_topo, profile_postEQ_topo,
                                               preEQ_coord_proj_csv, postEQ_coord_proj_csv)
    field_displ_df = get_field_displ_df(profile_route)
    crack_x_locations, failure_location = get_deformation_data(profile_route, topo_df)
    # create_map_plot(displ_field_coords, displ_field_coords_filter_RMSE_mask, displ_field_corr_df)
    # plot_field_dic_comparison(displ_field_corr_df)
    toe_x_value, toe_z_value = get_toe_location(profile_route, topo_df, displ_proj_df, failure_location)
    create_profile_plot(topo_df, displ_proj_df, toe_x_value, toe_z_value, failure_location)
    displ_proj_strain_df = get_strain_dic(displ_proj_df, toe_x_value, toe_z_value)
    print_strain_results_method1(displ_proj_strain_df, toe_x_value, toe_z_value)
    displ_proj_strain_df, toe_x_2017, toe_z_2017 = get_strain_method2(displ_proj_strain_df, crack_x_locations,
                                                                     toe_x_value, toe_z_value)
    # print_strain_results_method2(displ_proj_strain_df, toe_x_value, toe_z_value)
    displ_proj_strain_filt_df = filter_outliers(displ_proj_strain_df)
    displ_proj_strain_grad_filt_df = get_strain_grad(displ_proj_strain_filt_df)
    field_strain_df = get_strain_field(field_displ_df, toe_x_value, toe_z_value)
    print('<<strain plotted>>')
    # plot_strain_overview(displ_proj_strain_df, displ_proj_strain_grad_filt_df, field_strain_df, toe_x_value,
    #           crack_x_locations, failure_location)

    # plot_strain_indeces(displ_proj_strain_df, toe_x_value, crack_x_locations, failure_location)
    # plot_plunge(displ_proj_df)
    # plot_strain_with_slope(displ_proj_strain_grad_filt_df)

    # sensitivity = input('Should sensitivity analysis of toe location be carried out? [y/n] ')
    sensitivity = 'y'
    if sensitivity == 'y':
        sensitivity_dic_df = displ_proj_df
        sensitivity_field_df = field_displ_df
        toe_x_list_2015 = []
        toe_z_list_2015 = []
        toe_x_list_2017 = []
        toe_z_list_2017 = []
        for X_VALUE in TOE_X_RANGE:
            toe_x_value, toe_z_value = get_toe_x_z_sensitivity(X_VALUE, topo_df)
            toe_x_list_2015.append(toe_x_value)
            toe_z_list_2015.append(toe_z_value)
            displ_proj_strain_df = get_strain_dic(displ_proj_df, toe_x_value, toe_z_value)
            print_strain_results_method1(displ_proj_strain_df, toe_x_value, toe_z_value)
            sensitivity_dic_df['strain_dic_{:.1f}m'.format(toe_x_value)] = displ_proj_strain_df.strain_dic
            sensitivity_dic_df['angle_to_toe_{:.1f}m'.format(toe_x_value)] = displ_proj_strain_df.angle_to_toe
            displ_proj_strain_df, toe_x_2017, toe_z_2017 = get_strain_method2(displ_proj_strain_df, crack_x_locations,
                                                                        toe_x_value, toe_z_value)
            print_strain_results_method2(displ_proj_strain_df, toe_x_value, toe_z_value)
            sensitivity_dic_df['strain_dic_m2_{:.1f}m'.format(toe_x_value)] = displ_proj_strain_df.strain_dic_m2
            if SITE_FIELD_DISPL != '':
                field_strain_df0 = get_field_displ_df(profile_route)
                field_strain_df = get_strain_field(field_strain_df0, toe_x_value, toe_z_value)
                sensitivity_field_df['strain_field_{:.1f}m'.format(toe_x_value)] = field_strain_df.strain_field
            toe_x_list_2017.append(toe_x_2017)
            toe_z_list_2017.append(toe_z_2017)

        sensitivity_dic_filt_df = filter_outliers(sensitivity_dic_df)
        sensitivity_strain_grad_filt_df0 = get_strain_grad_sensitivity(sensitivity_dic_filt_df, toe_x_list_2015)
        sensitivity_strain_grad_filt_df = get_strain_grad_sensitivity_m2(sensitivity_strain_grad_filt_df0, toe_x_list_2015)
        plot_profile_sensitivity(topo_df, displ_proj_df, toe_x_list_2015, toe_z_list_2015,
                              toe_x_list_2017, toe_z_list_2017, failure_location)
        plot_strain_sensitivity(sensitivity_strain_grad_filt_df, sensitivity_field_df, toe_x_list_2015,
                            crack_x_locations, failure_location)
        create_displ_strain_plot(displ_proj_strain_df, displ_proj_strain_grad_filt_df,
                                 field_strain_df, toe_x_value, crack_x_locations, failure_location,
                                 sensitivity_strain_grad_filt_df, toe_x_list_2015)
    elif sensitivity == 'n':
        print('Sensitivity analysis not carried out.')
    else:
        print('User input not valid.')
    path = PATH_DIC + '/Output/temp/'
    for file_name in os.listdir(path):
        # construct full file path
        file = path + file_name
        if os.path.isfile(file):
            print('Deleting file:', file)
            os.remove(file)

run_sensitivity()