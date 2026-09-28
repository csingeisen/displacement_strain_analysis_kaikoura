from dic_module_plot_all_profiles import *


def plot_all_profiles():
    failure_x_norm_list = []
    results_df = pd.DataFrame()
    for i in range(0, len(SITE_LIST)):
        profile_preEQ_topo, profile_postEQ_topo = get_topo_profiles(i)
        displ_field_coords, displ_field_coords_postEQ = get_gis_point_layers(i)
        displ_field_coords_filter_RMSE, displ_field_coords_filter_RMSE_mask = filter_point_layer(displ_field_coords,i)
        displ_field_selected = select_features_to_project(displ_field_coords, displ_field_coords_filter_RMSE,
                                                          displ_field_coords_filter_RMSE_mask)
        profile_route, preEQ_coord_proj_csv, postEQ_coord_proj_csv = get_pixel_locations(displ_field_selected, i)
        topo_df, displ_proj_df = create_dataframes(profile_preEQ_topo, profile_postEQ_topo,
                                                   preEQ_coord_proj_csv, postEQ_coord_proj_csv, i)
        crack_x_locations, failure_location = get_deformation_data(profile_route, topo_df, i)
        toe_x_value, toe_z_value = get_toe_location(topo_df, i)
        # Get field displacement data
        field_displ_df = get_field_displ_df(profile_route, i)
        # Calculate DIC strain
        displ_proj_strain_df = get_strain_dic(displ_proj_df, toe_x_value, toe_z_value, i)
        displ_proj_strain_filt_df = filter_outliers(displ_proj_strain_df)
        # Calculate field measurement strain
        field_strain_df = get_strain_field(field_displ_df, toe_x_value, toe_z_value, i)
        # Get normalised distance and plot displacement and strain along profile
        displ_proj_strain_filt_norm_df, field_strain_norm_df, crack_x_locations_norm, failure_x_norm = get_norm_dist(
            displ_proj_strain_filt_df, field_strain_df, toe_x_value, crack_x_locations, failure_location, i)
        plot_strain_overview(displ_proj_strain_filt_norm_df, field_strain_norm_df, crack_x_locations_norm,
                             failure_x_norm, i)
        failure_x_norm_list.append(failure_x_norm)
        # write results to new dataframe
        displ_proj_strain_filt_norm_df.to_csv('C:/Users/csi57/OneDrive for Business/02_PhD/04_Site_Characterisation/'
                                              '/Strain_Results_RemoteSensing/strain_{}.csv'.format(PROFILE_LIST[i]))
        copy_df = displ_proj_strain_filt_norm_df[['meas_x_preEQ_norm', 'proj_offset', 'strain_dic']].copy()
        copy_df.rename(columns={'meas_x_preEQ_norm': 'meas_x_preEQ_norm_{}'.format(PROFILE_LIST[i]),
                                'proj_offset': 'proj_offset_{}'.format(PROFILE_LIST[i]),
                                'strain_dic': 'strain_dic_{}'.format(PROFILE_LIST[i])}, inplace=True)
        print(copy_df.columns)
        results_df = pd.concat([results_df, copy_df], axis=1)
        print(results_df.columns)
    results_df.to_csv('C:/Users/csi57/OneDrive for Business/02_PhD/04_Site_Characterisation/strain_profiles.csv')
    failure_df = pd.DataFrame(failure_x_norm_list, columns=['failure_x_norm'])
    failure_df.to_csv('C:/Users/csi57/OneDrive for Business/02_PhD/04_Site_Characterisation/failure_loc_norm.csv')


def plot_summary():
    # Plot summary graph
    results_csv = 'C:/Users/csi57/OneDrive for Business/02_PhD/04_Site_Characterisation/' \
                  'Strain_Results_RemoteSensing/strain_profiles.csv'
    results_df = pd.read_csv(results_csv)
    failure_csv = 'C:/Users/csi57/OneDrive for Business/02_PhD/04_Site_Characterisation/' \
                  'Strain_Results_RemoteSensing/failure_loc_norm.csv'
    failure_df = pd.read_csv(failure_csv)
    plot_profiles(results_df, failure_df)



plot_all_profiles()
plot_summary()