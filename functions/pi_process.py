# pi_process.py
from functions.read_meta import read_meta
from functions.generate_file_lists import get_filepaths, generate_file_lists
import os
from datetime import datetime
from pathlib import Path
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
from csv import DictReader
import shutil
from file_paths import root_file_paths


def pi_process(file_paths, session_list):
    for session in session_list['external_path']:
        try:
            if session not in session_list['pi_processed_list'] and session in session_list['phy_processed_list']:
                meta_data = read_meta(Path(
                    os.path.join(file_paths['external_path'], session, session + '_imec0', session + '_t0.imec0.ap.bin')))
                recording_time = meta_data['fileCreateTime']
                dt_object = datetime.strptime(recording_time, "%Y-%m-%dT%H:%M:%S")
                mouse = session[:5]

                pi_file_names = [path.split(os.sep)[-1] for path in
                                 get_filepaths(os.path.join(file_paths['pi_path'], mouse))]
                pi_file_times = [datetime.strptime(file_name[5:-4], "%Y-%m-%d_%H-%M-%S") for file_name in pi_file_names if
                                 file_name != 'desktop.ini']
                pi_file_name = 'data_' + pi_file_times[np.argmin([abs(file_time - dt_object) for file_time in
                                                                  pi_file_times])].strftime("%Y-%m-%d_%H-%M-%S") + '.txt'
                pi_dir = os.path.join(file_paths['pi_path'], mouse, pi_file_name)
                data_dir = os.path.join(file_paths['external_path'], session, 'processed_data')
                phy_dir = os.path.join(file_paths['external_path'], session, 'phy_output')
                hz = 30000.325941

                spike_clusters = np.load(os.path.join(phy_dir, 'spike_clusters.npy'))
                spike_templates = np.load(os.path.join(phy_dir, 'spike_templates.npy'))
                spike_times = np.load(os.path.join(phy_dir, 'spike_times.npy'))
                templates = np.load(os.path.join(phy_dir, 'templates.npy'))
                cluster_info = pd.read_csv(os.path.join(phy_dir, 'cluster_info.tsv'), sep='\t')

                spikes = pd.DataFrame(np.concatenate([spike_times, np.expand_dims(spike_clusters, axis=1), spike_templates],
                                                     axis=1), columns=['cycle', 'cluster', 'template'])
                spikes['time'] = spikes.cycle / hz

                pi_events = pd.read_csv(pi_dir, na_values=['None'], skiprows=3)
                pi_events['session_minutes'] = [x / 60 for x in pi_events['session_time']]

                catgt_path = os.path.join(file_paths['external_path'], session, session + '_imec0',
                                           session + '_tcat.imec0.ap.xd_384_6_0.txt')
                with open(catgt_path) as f:
                    np_times = [float(s.rstrip()) for s in f.readlines()]
                camera = pi_events.key == 'camera'
                start = pi_events.value == 1
                pi_times = pi_events[camera & start].session_time.to_numpy()
                pi_times = pi_times[-len(np_times):]

                reg = LinearRegression().fit(pi_times.reshape(-1, 1), np_times)
                adjusted_pi_times = reg.predict(pi_events.session_time.to_numpy().reshape(-1, 1))
                outer = np.subtract.outer(adjusted_pi_times, np_times)
                outer = np.abs(outer)
                print(f'first pass median error: {np.median(np.nanmin(outer, axis=1))}')

                pi_events['time'] = adjusted_pi_times
                pi_events['sync_error'] = np.nanmin(outer, axis=1)


                cluster_info = cluster_info[cluster_info.group == 'good']
                spikes = spikes[spikes.cluster.isin(cluster_info.id)]
                spikes = remove_dup_spikes(spikes, cluster_info)

                # This saves the pd data frames so they can easily be reloaded
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                spikes.to_pickle(os.path.join(data_dir, 'spikes.pkl'))
                cluster_info.to_pickle(os.path.join(data_dir, 'cluster_info.pkl'))
                pi_events.to_pickle(os.path.join(data_dir, 'pi_events.pkl'))
                np.save(os.path.join(data_dir, 'templates'), templates)
                print(f'{session} has {len(cluster_info)} units')
        except Exception as e:
            print(f'{session} threw error: {e}')


def remove_dup_spikes(spikes, cluster_info):
    to_remove = []
    for unit in cluster_info.id:
        dif = spikes[spikes.cluster == unit].time - np.roll(
            spikes[spikes.cluster == unit].time, 1)
        dif = dif[1:]
        ind = np.where((0 < dif) & (dif < 0.0004))[0]
        if len(ind):
            to_remove.append([dif.index[i] for i in ind])
    to_remove = [item for sublist in to_remove for item in sublist]
    spikes.drop(to_remove)
    return spikes


def aligned_pi_events(data):
    all_pi_files = get_all_filenames(data.mouse)
    pi_files = []
    for f in all_pi_files:
        if f[5:15] == data.date.replace('_', '-'):
            pi_files += [f]
    if len(pi_files) > 1:
        pi_files = [pi_files[int(data.directory[-1])]]
    pi_events = [preprocess_data(f, data.mouse) for f in pi_files]
    pi_events = pi_events[0]

    np_events = data.events
    reward = np_events.key == 'reward'
    trial = np_events.key == 'trial'
    stop = np_events.value == 0
    np_events = np_events[~((reward | trial) & stop)]
    np_events = np_events[np_events.key != 'none']

    keys = ['camera']
    pi_times = pi_events[pi_events.key.isin(keys)].session_time.to_numpy()
    np_times = np_events[np_events.key.isin(keys)].time.to_numpy()
    pi_times = pi_times[-len(np_times):]

    reg = LinearRegression().fit(pi_times.reshape(-1, 1), np_times)
    adjusted_pi_times = reg.predict(pi_events.session_time.to_numpy().reshape(-1, 1))
    outer = np.subtract.outer(adjusted_pi_times, np_events.time.to_numpy())
    outer = np.abs(outer)
    print(f'first pass median error: {np.median(np.nanmin(outer, axis=1))}')

    pi_events['time'] = adjusted_pi_times
    pi_events['sync_error'] = np.nanmin(outer, axis=1)

    return pi_events


def get_all_filenames(mouse):
    path = "C:\\Users\\Elissa\\GoogleDrive\\Code\\Python\\behavior_code\\data"

    [[_, _, filenames]] = os.walk(path + '/' + mouse)
    for f in filenames:
        if f[0] == '.':
            filenames.remove(f)
        if f == 'desktop.ini':
            filenames.remove(f)
        if f == 'Icon\r':
            filenames.remove(f)
    filenames.sort()
    return filenames


def preprocess_data(filename, mouse, return_info=False, verbose=False, date_range=None):
    path = "C:\\Users\\Elissa\\GoogleDrive\\Code\\Python\\behavior_code\\data"
    if date_range:
        if not (date_range[0] < filename[6:] & filename[6:] < date_range[1]):
            return None
    filepath = path + '/' + mouse + '/' + filename
    data = pd.read_csv(filepath, na_values=['None'], skiprows=3)
    data['session_minutes'] = [x / 60 for x in data['session_time']]
    if verbose:
        print(f'processed {filename}')
    if return_info:
        with open(filepath, 'r') as file:  # Read meta data from first two lines into a dictionary
            reader = DictReader(file)
            info = []
            info.append(next(reader))
        return info
    return data



if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    pi_process(file_paths, session_list)
