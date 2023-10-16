def export_df_to_txt(my_df, my_path):
    path = my_path + my_df.name + '.txt'

    # export DataFrame to text file (keep header row, but not index column)
    # 'w' means overwrite, 'a' means 'append'
    with open(path, 'w') as f:
        df_string = my_df.to_string(index=False)
        f.write(df_string)

    print(my_df.name + ' of animal ' + my_path[95:100] + ' session ' + my_path[-19:] + ' exported as txt')
