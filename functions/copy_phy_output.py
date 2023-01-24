# copy_phy_output.py
import os
import shutil
import pandas as pd
import numpy as np
from functions.generate_file_lists import generate_file_lists


def copy_phy_output(session_list, file_paths):
    for session in session_list['phy_ready_path']:
        path = os.path.join(file_paths['phy_ready_path'], session)
        cluster_group_path = os.path.join(path, 'cluster_group.tsv')
        cluster_group = pd.read_csv(cluster_group_path, sep='\t')
        is_labeled = [label in ['good', 'mua', 'noise'] for label in cluster_group.group.values]
        if np.all(is_labeled):
            if os.path.exists(os.path.join(path, 'recording.dat')):
                os.remove(os.path.join(path, 'recording.dat'))
            if os.path.exists(os.path.join(path, 'pc_features.npy')):
                os.remove(os.path.join(path, 'pc_features.npy'))
            if os.path.exists(os.path.join(path, '.phy')):
                shutil.rmtree(os.path.join(path, '.phy'))

            # Move data to main folder on E: drive
            dest_path = os.path.join(file_paths['external_path'], session, 'phy_output')
            if not os.path.exists(dest_path):
                shutil.copytree(path, dest_path)

            # Move data to backup folder on C: drive
            backup_path = os.path.join('C:\\', 'phy_backup', session, 'phy_output')
            if not os.path.isdir(os.path.dirname(backup_path)):
                os.mkdir(os.path.dirname(backup_path))
            if not os.path.exists(backup_path):
                shutil.copytree(path, backup_path)

            # Remove files from phy_ready folder
            shutil.rmtree(path)
    print('finished copying phy output')


if __name__ == '__main__':
    file_paths = {
        'origin_path': os.path.join('D:\\', 'recordings'),
        'external_path': os.path.join('E:\\', 'neuropixel_data'),
        'phy_ready_path': os.path.join('C:\\', 'phy_ready'),
        'phy_holding_path': os.path.join('E:\\', 'phy_holding'),
        'pi_path': os.path.join('C:\\', 'Users', 'Elissa', 'GoogleDrive', 'Code', 'Python', 'behavior_code', 'data')
    }
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    copy_phy_output(session_list, file_paths)
