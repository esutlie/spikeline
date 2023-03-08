# prep_phy.py
from functions.spikeline import spikeline
from functions.check_files import check_session_files
from functions.generate_file_lists import generate_file_lists
import os
import psutil
import random
from file_paths import root_file_paths


def prep_phy(file_paths, session_list):
    not_processed = [session for session in session_list['external_path'] if
                     session not in session_list['phy_ready_path'] + session_list['phy_processed_list']
                     + session_list['kilosort_fail_list']]
    # not_processed = not_processed[::-1]
    hdd = psutil.disk_usage('/')
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')
    # i = random.randint(0, len(not_processed) - 1)
    for i in range(len(not_processed)):
        if hdd.free / (2 ** 30) > 100 and len(not_processed):
            if check_session_files(file_paths['external_path'], not_processed[i]):
                try:
                    file_path = os.path.join(file_paths['external_path'], not_processed[i])
                    spikeline(file_path, file_paths['phy_ready_path'])
                except Exception as e:
                    print(f'spikeline threw the following error while processing {not_processed[i]}')
                    print(e)
            else:
                print(f'{not_processed[i]} is missing file[s]')



if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    prep_phy(file_paths, session_list)
