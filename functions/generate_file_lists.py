# generate_file_lists.py
import os


def generate_file_lists(file_paths):
    external_sessions = get_directories(file_paths['external_path'])
    phy_processed = [session for session in external_sessions if
                     os.path.exists(os.path.join(file_paths['external_path'], session, 'phy_output'))]
    pi_processed = [session for session in external_sessions if
                    os.path.exists(os.path.join(file_paths['external_path'], session, 'processed_data', 'info.json'))]

    kilosort_fail_list = [
        'ES029_2022-09-28_checker0_199_0_g0',
        'ES029_2022-09-27_checker0_199_0_g0',
        'ES029_2022-09-26_checker0_199_0_g0',
        'ES029_2022-09-23_checker0_199_0_g0',
        'ES029_2022-09-22_checker0_199_1_g0',
        'ES029_2022-09-16_bot192_1_g0',
        'ES037_2023-12-20_bot336_1_g0'  # only one unit identified, so phy throws an error
    ]
    session_list = {
        'origin_path': get_directories(file_paths['origin_path']),
        'external_path': get_directories(file_paths['external_path']),
        'phy_ready_path': get_directories(file_paths['phy_ready_path']),
        'pi_path': get_directories(file_paths['pi_path']),
        'phy_processed_list': phy_processed,
        'pi_processed_list': pi_processed,
        'kilosort_fail_list': kilosort_fail_list
    }
    file_list = {
        'origin_path': get_filepaths(file_paths['origin_path']),
        'external_path': get_filepaths(file_paths['external_path']),
        'pi_path': get_filepaths(file_paths['pi_path']),
        'phy_ready_path': get_filepaths(file_paths['phy_ready_path']),
    }
    return session_list, file_list


def get_filepaths(directory=os.path.join('D:\\', 'Test')):
    # List to store paths
    file_paths = []

    # Walk through directory
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Add filename to list
            file_paths.append(os.path.join(root, filename))

            # Return all paths
    return file_paths


def get_directories(directory=os.path.join('D:\\', 'Test'), top_level_only=True):
    # List to store paths
    directory_list = []

    # Walk through directory
    for root, directories, files in os.walk(directory):
        for d in directories:
            # Add filename to list
            directory_list.append(d)
        if top_level_only:
            break

            # Return all paths
    return directory_list
