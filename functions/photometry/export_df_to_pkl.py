def export_df_to_pkl(my_df, my_path):
    path = my_path + '.pkl'
    my_df.to_pickle(path)
    print(my_df.name + ' of animal ' + my_path[95:100] + ' session ' + my_path[-19:] + ' exported as pkl')