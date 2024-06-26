# prep_phy.py
from functions.spikeline import spikeline
from functions.check_files import check_session_files
from functions.generate_file_lists import generate_file_lists
import os
import psutil
import random
from file_paths import root_file_paths
import time
from functions.check_probe_codes import check_probe_codes


def prep_phy():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    # not_processed = session_list['external_path'][:1]
    not_processed = []
    for session in session_list['external_path']:
        if (session not in session_list['phy_ready_path'] + session_list['phy_processed_list'] +
                session_list['kilosort_fail_list']):
            probe_codes = check_probe_codes(os.path.join(file_paths['external_path'], session))
            if len(probe_codes) == 1:
                not_processed.append(session)
            else:
                for code in probe_codes:
                    if session + '_' + code not in session_list['phy_ready_path']:
                        not_processed.append(session)
                        break

    # not_processed = [session for session in session_list['external_path'] if
    #                  session not in session_list['phy_ready_path'] + session_list['phy_processed_list']
    #                  + session_list['kilosort_fail_list']]
    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')
    for i in range(len(not_processed)):
        hdd = psutil.disk_usage(file_paths['phy_ready_path'])
        if hdd.free / (2 ** 30) > 200:
            if check_session_files(file_paths['external_path'], not_processed[i]):
                try:
                    print(f'started {not_processed[i]} at {time.strftime("%H:%M:%S", time.localtime())}')
                    file_path = os.path.join(file_paths['external_path'], not_processed[i])
                    spikeline(file_path, file_paths['phy_ready_path'])
                    print(f'finished {not_processed[i]} at {time.strftime("%H:%M:%S", time.localtime())}')
                except Exception as e:
                    print(f'spikeline threw the following error while processing {not_processed[i]}')
                    print(e)
                    continue
                    # raise e
                break
            else:
                print(f'{not_processed[i]} is missing file[s]')


if __name__ == '__main__':
    prep_phy()
