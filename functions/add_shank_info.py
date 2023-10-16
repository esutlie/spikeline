import numpy as np
import os
import pandas as pd
from functions.generate_file_lists import generate_file_lists
from file_paths import root_file_paths


def add_shank_info(cluster_info, phy_dir):
    channel_positions = np.load(os.path.join(phy_dir, 'channel_positions.npy'))
    channel_shanks = np.round(channel_positions[:, 0] / 250)
    channel_row = np.round(channel_positions[:, 1] / 15)
    cluster_info['shank'] = channel_shanks[cluster_info.ch.values]
    cluster_info['row'] = channel_row[cluster_info.ch.values]
    return cluster_info


if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for session in session_list['external_path']:
        cluster_info_dir = os.path.join(file_paths['external_path'], session, 'processed_data', 'cluster_info.pkl')
        phy_dir = os.path.join(file_paths['external_path'], session, 'phy_output')
        if os.path.exists(cluster_info_dir):
            cluster_info = pd.read_pickle(cluster_info_dir)
            cluster_info = add_shank_info(cluster_info, phy_dir)
            cluster_info.to_pickle(cluster_info_dir)
