import numpy as np
import os
import pandas as pd
from functions.generate_file_lists import generate_file_lists
from file_paths import root_file_paths


def remove_dup_spikes(spikes, cluster_info):
    to_remove = []
    for unit in cluster_info.id:
        dif = spikes[spikes.cluster == unit].time - np.roll(
            spikes[spikes.cluster == unit].time, 1)
        dif = dif[1:]
        ind = np.where((dif < 0.0004))[0]
        print(
            f'{len(np.where((dif < 0.0004))[0])} = {len(np.where((-.0001 < dif) & (dif < 0.0004))[0])} != {len(np.where((0 < dif) & (dif < 0.0004))[0])}')
        print(f'removing {len(ind)}/{len(spikes[spikes.cluster == unit])} spikes')
        if len(ind):
            to_remove.append([dif.index[i] for i in ind])
    to_remove = [item for sublist in to_remove for item in sublist]
    spikes = spikes.drop(to_remove)
    return spikes


if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for session in session_list['external_path']:
        spike_dir = os.path.join(file_paths['external_path'], session, 'processed_data', 'spikes.pkl')
        cluster_info_dir = os.path.join(file_paths['external_path'], session, 'processed_data', 'cluster_info.pkl')
        if os.path.exists(spike_dir):
            spikes = pd.read_pickle(spike_dir)
            cluster_info = pd.read_pickle(cluster_info_dir)
            spikes = remove_dup_spikes(spikes, cluster_info)
            spikes.to_pickle(spike_dir)
