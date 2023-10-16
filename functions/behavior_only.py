from file_paths import root_file_paths
from functions.generate_file_lists import generate_file_lists
import os
import pandas as pd
from functions.read_pi_meta import read_pi_meta
import json


def behavior_only():
    exclude = ['half_sessions', 'testmouse', 'videos', 'data']
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for pi_dir in file_list['pi_path']:
        path_parts = pi_dir.split(os.sep)
        file_name = path_parts[-1]
        mouse = path_parts[-2]
        if mouse in exclude or file_name == 'desktop.ini':
            continue
        save_path = os.path.join(file_paths['behavior_only'], mouse, file_name[:-4])
        if os.path.exists(os.path.join(save_path, 'pi_events.pkl')) and os.path.exists(
                os.path.join(save_path, 'info.json')):
            continue
        pi_events = pd.read_csv(pi_dir, na_values=['None'], skiprows=3)
        pi_events['session_minutes'] = [x / 60 for x in pi_events['session_time']]
        info = read_pi_meta(pi_dir)
        pi_events['time'] = pi_events.session_time
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        pi_events.to_pickle(os.path.join(save_path, 'pi_events.pkl'))
        with open(os.path.join(save_path, 'info.json'), "w") as info_file:
            json.dump(info, info_file)


if __name__ == '__main__':
    behavior_only()
