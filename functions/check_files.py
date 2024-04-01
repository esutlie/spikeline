# check_files.py
import os
from functions.generate_file_lists import get_directories
import shutil


def check_files(file_location=os.path.join('E:\\', 'neuropixel_data'),
                source_location=os.path.join('\\\\10.16.79.239', 'ShulerLab', 'Elissa Sutlief', 'neuropixel_data',
                                             'ES029')):
    dirs = get_directories(file_location)
    for session in dirs:
        path1 = os.path.join(file_location, session, session + '_t0.nidq.bin')
        path2 = os.path.join(file_location, session, session + '_t0.nidq.meta')
        path3 = os.path.join(file_location, session, session + '_imec0', session + '_t0.imec0.ap.bin')
        path4 = os.path.join(file_location, session, session + '_imec0', session + '_t0.imec0.ap.meta')
        for path in [path1, path2, path3, path4]:
            if not os.path.exists(path):
                print(f'Missing {path}')
                tail = os.path.join(*path.split(os.sep)[len(file_location.split(os.sep)):])
                if tail[:5] == 'ES029':
                    print(f'copying to {path}')
                    directory = os.path.dirname(path)
                    if not os.path.exists(directory):
                        os.mkdir(directory)
                    shutil.copy(os.path.join(source_location, tail), path)
                    if not os.path.exists(path):
                        print('file not copied successfully')


def check_session_files(file_location, session):
    # path1 = os.path.join(file_location, session, session + '_t0.nidq.bin')
    # path2 = os.path.join(file_location, session, session + '_t0.nidq.meta')
    path1 = os.path.join(file_location, session, session + '_imec0', session + '_t0.imec0.ap.bin')
    path2 = os.path.join(file_location, session, session + '_imec0', session + '_t0.imec0.ap.meta')
    for path in [path1, path2]:
        if not os.path.exists(path):
            return False
    return True


def check_processing_files(file_location=os.path.join('E:\\', 'neuropixel_data'),
                           phy_ready_location=os.path.join('C:\\', 'phy_ready')):
    known_error = ['ES029_2022-09-16_bot192_1_g0', 'ES029_2022-09-22_checker0_199_1_g0',
                   'ES029_2022-09-23_checker0_199_0_g0', 'ES029_2022-09-26_checker0_199_0_g0',
                   'ES029_2022-09-27_checker0_199_0_g0', 'ES029_2022-09-28_checker0_199_0_g0',
                   'ES037_2023-12-20_bot336_1_g0']
    dirs = get_directories(file_location)
    phy_ready = []
    phy_complete = []
    phy_none = []
    data_ready = []
    data_not_ready = []
    catgt_done = []
    catgt_not_done = []
    for session in dirs:
        if os.path.exists(os.path.join(file_location, session, 'catgt_' + session, session + '_imec0',
                                       session + '_tcat.imec0.ap.xd_384_6_0.txt')):
            catgt_done += [session]
        elif session not in known_error:
            catgt_not_done += [session]

        if os.path.exists(os.path.join(file_location, session, 'processed_data')):
            data_ready += [session]
        elif session not in known_error:
            data_not_ready += [session]
        if os.path.exists(os.path.join(file_location, session, 'phy_output')):
            phy_complete += [session]
        if os.path.exists(os.path.join(phy_ready_location, session)):
            phy_ready += [session]
        if not os.path.exists(os.path.join(phy_ready_location, session)) and not os.path.exists(
                os.path.join(file_location, session, 'phy_output')) and session not in known_error:
            phy_none += [session]

    print(f'data ready sessions: {len(data_ready)}\n{data_ready}')
    print(f'data not ready sessions: {len(data_not_ready)}\n{data_not_ready}')
    print(f'phy ready sessions: {len(phy_ready)}\n{phy_ready}')
    print(f'phy complete sessions: {len(phy_complete)}\n{phy_complete}')
    print(f'no phy yet sessions: {len(phy_none)}\n{phy_none}')
    print(f'catgt done sessions: {len(catgt_done)}\n{catgt_done}')
    print(f'catgt not done sessions: {len(catgt_not_done)}\n{catgt_not_done}')
    print(f'known error sessions: {len(known_error)}\n{known_error}')


if __name__ == '__main__':
    check_processing_files()
