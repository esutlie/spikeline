from functions import *
import os
import shutil
import pandas as pd
import numpy as np
from time import sleep


def run_pipeline():
    # File paths:
    file_paths = {
        'origin_path': os.path.join('D:\\', 'recordings'),
        'external_path': os.path.join('E:\\', 'neuropixel_data'),
        'phy_ready_path': os.path.join('C:\\', 'phy_ready'),
        'phy_holding_path': os.path.join('E:\\', 'phy_holding'),
        'pi_path': os.path.join('C:\\', 'Users', 'Elissa', 'GoogleDrive', 'Code', 'Python', 'behavior_code', 'data'),
        'processed_data': os.path.join('C:\\', 'processed_data')
    }

    while True:
        # Transfer new files
        sleep_if()
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        copy_if_missing(file_list['origin_path'], file_list['external_path'])

        # Run catgt on files where it's missing
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        for session in session_list['external_path']:
            try:
                if not os.path.isfile(os.path.join(file_paths['external_path'], session, session + '_imec0',
                                                   session + '_tcat.imec0.ap.xd_384_6_0.txt')):
                    path = os.path.join(file_paths['external_path'], session)
                    catgt(path, path)
            finally:
                print('waited for catgt to finish')

        # Find pi file
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        pi_process(file_paths, session_list)

        # Run spike interface to get phy folder prepped
        sleep_if()
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        prep_phy(file_paths, session_list, file_list)

        # Transfer phy outputs if sorting is complete, and remove phy folder from prep
        sleep_if()
        try:
            session_list, file_list = generate_file_lists(file_paths=file_paths)
            copy_phy_output(session_list, file_paths)
        finally:
            print('waited for copy_phy_output to finish')

        sleep(10)


if __name__ == '__main__':
    run_pipeline()
