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


def check_structure():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    external_sessions = session_list['external_path']
    for session in external_sessions:
        external_path = os.path.join(file_paths['external_path'], session)
        get_filepaths(os.path.join(external_path, 'phy_output'))
        external_files = get_filepaths(external_path)
        expected_files = [os.path.join(external_path, p) for p in expected_structure(session)]
        missing_files = [f for f in expected_files if f not in external_files]
        extra_files = [f for f in external_files if f not in expected_files]
        extra_files = [f for f in extra_files if f.split(os.sep)[-1][:4] != 'data']
        # if len(extra_files):
        #     print(session)
        #     print('   extra files:')
        #     for f in extra_files:
        #         print('        ' + f)
        #         # os.remove(f)
        if len(missing_files):
            print(session)
            print('   missing files:')
            for f in missing_files:
                print('        ' + f)

def expected_structure(name):
    phy_files = ['channel_groups.npy', 'channel_map.npy', 'channel_map_si.npy', 'channel_positions.npy',
                 'cluster_channel_group.tsv', 'cluster_group.tsv', 'cluster_info.tsv', 'cluster_si_unit_id.tsv',
                 'cluster_si_unit_ids.tsv', 'params.py', 'phy.log', 'similar_templates.npy', 'spike_clusters.npy',
                 'spike_templates.npy', 'spike_times.npy', 'templates.npy', 'template_ind.npy', 'whitening_mat_inv.npy',
                 'amplitudes.npy', 'pc_features.npy', 'pc_feature_ind.npy']
    processed_files = ['cluster_info.pkl', 'pi_events.pkl', 'spikes.pkl', 'templates.npy']
    structure = [
        os.path.join('catgt_' + name, name + '_imec0', name + '_tcat.imec0.ap.bin'),
        os.path.join('catgt_' + name, name + '_imec0', name + '_tcat.imec0.ap.meta'),
        os.path.join('catgt_' + name, name + '_imec0', name + '_tcat.imec0.ap.xd_384_6_0.txt'),
        os.path.join('catgt_' + name, name + '_imec0', name + '_tcat.imec0.ap.xd_384_6_500.txt'),
        os.path.join('catgt_' + name, name + '_ct_offsets.txt'),
        os.path.join('catgt_' + name, name + '_fyi.txt'),
        os.path.join(name + '_imec0', name + '_t0.imec0.ap.bin'),
        os.path.join(name + '_imec0', name + '_t0.imec0.ap.meta'),
        os.path.join(name + '_t0.nidq.bin'),
        os.path.join(name + '_t0.nidq.meta'),
        *[os.path.join('phy_output', file_name) for file_name in phy_files],
        *[os.path.join('phy_output_pre_align', file_name) for file_name in phy_files],
        *[os.path.join('processed_data', file_name) for file_name in processed_files],
    ]
    return structure


if __name__ == '__main__':
    # check_locations()
    check_structure()
