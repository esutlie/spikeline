import os
from functions.generate_file_lists import generate_file_lists, get_filepaths
from file_paths import root_file_paths
from google.cloud import storage
import numpy as np
import pandas as pd
from google_copy import get_cloud_files


def check_locations():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    origin_sessions = session_list['origin_path']
    external_sessions = session_list['external_path']
    cloud_archive = get_cloud_files()
    # key_file = os.path.join('C:\\', 'cloud', 'spikeline-753a261c881e.json')
    # storage_client = storage.Client.from_service_account_json(key_file, project='spikeline')
    # archive_files = [blob.name for blob in storage_client.list_blobs('spikeline_archive')]
    # google_sessions = np.unique([name.split('/')[0] for name in archive_files]).tolist()
    archive_files = cloud_archive['archived']
    google_sessions = np.unique([name.split('/')[0] for name in archive_files if name != '']).tolist()
    all_sessions = np.unique(origin_sessions + external_sessions + google_sessions)

    for session in all_sessions:
        origin_path = os.path.join(file_paths['origin_path'], session)
        external_path = os.path.join(file_paths['external_path'], session)
        origin_files = [name.split(os.sep)[-1] for name in get_filepaths(origin_path)]
        external_files = [name.split(os.sep)[-1] for name in get_filepaths(external_path)]
        google_files = [name.split('/')[-1] for name in archive_files if name.split('/')[0] == session]
        all_files = np.unique(origin_files + external_files + google_files)
        columns = ['origin', 'external', 'google']
        bool_data = np.array(
            [[file in location for file in all_files] for location in [origin_files, external_files, google_files]]).T
        session_df = pd.DataFrame(bool_data, columns=columns, index=all_files)
        if len(session_df[session_df.origin]):
            # print(session_df)
            if np.all(session_df[session_df.origin].external) & np.all(session_df[session_df.origin].google):
                print(f'{session} is okay to be deleted from origin')
            else:
                print(f'{session} should not be deleted')


if __name__ == '__main__':
    check_locations()
