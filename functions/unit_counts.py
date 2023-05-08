import os
from functions.generate_file_lists import generate_file_lists, get_filepaths
from file_paths import root_file_paths
from google.cloud import storage
import numpy as np
import pandas as pd
from google_copy import get_cloud_files


def unit_counts():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    sessions = session_list['external_path']
    for session in sessions:
        print(session)
        phy_path = os.path.join(file_paths['external_path'], session, 'phy_output')
        if os.path.isdir(phy_path):
            cluster_info = pd.read_csv(os.path.join(phy_path, 'cluster_info.tsv'), sep='\t')
            num_units = np.sum(cluster_info.group == 'good')
            print(f'    post_aligned: {num_units}')

        phy_path_pre_align = os.path.join(file_paths['external_path'], session, 'phy_output_pre_align')
        if os.path.isdir(phy_path_pre_align):
            cluster_info_pre_align = pd.read_csv(os.path.join(phy_path_pre_align, 'cluster_info.tsv'), sep='\t')
            num_units = np.sum(cluster_info_pre_align.group == 'good')
            print(f'    pre_aligned:  {num_units}')


def designate_old():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    sessions = session_list['external_path']
    for session in sessions:
        external_path = os.path.join(file_paths['external_path'], session, 'phy_output')
        if os.path.isdir(external_path):
            os.rename(external_path, os.path.join(file_paths['external_path'], session, 'phy_output_pre_align'))


if __name__ == '__main__':
    unit_counts()
    # designate_old()
