from functions.read_meta import read_meta
from functions.read_pi_meta import read_pi_meta
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
import json
import matplotlib.pyplot as plt
from photometry import data_read_sync, check_framedrop, de_interleave, calculate_dFF0


def preprocess():
    save_root = os.path.join('C:\\', 'github', 'analysis_pipeline', 'z_photometry')
    unprocessed_root = os.path.join('C:\\', 'photometry_data')

    mice = []
    pi_data_fnames = []
    signal_data_fnames = []
    arduino_data_fnames = []

    # Walk through directory
    for root, directories, files in os.walk(unprocessed_root):
        for filename in files:
            if filename[:4] == 'data':
                mice.append(os.path.basename(root))
                pi_data_fnames.append(filename)
            elif filename[:2] == 'FP':
                signal_data_fnames.append(filename)
            elif filename[:2] == 'ar':
                arduino_data_fnames.append(filename)

    for i in range(len(mice)):
        date_time = pi_data_fnames[i][5:-4]
        session_name = f'{mice[i]}_{date_time}'
        pi_dir = os.path.join(unprocessed_root, mice[i], pi_data_fnames[i])
        signal_dir = os.path.join(unprocessed_root, mice[i], signal_data_fnames[i])
        arduino_dir = os.path.join(unprocessed_root, mice[i], arduino_data_fnames[i])
        pi_events, neural_events = data_read_sync(pi_dir, signal_dir, arduino_dir)
        check_framedrop(neural_events)
        raw_separated = de_interleave(neural_events, session_label=signal_dir[-23:-7])
        dFF0 = calculate_dFF0(raw_separated, session_label=signal_dir[-23:-7], plot=False, plot_middle_steps=False)
        dFF0 = dFF0.rename(columns={'time_recording': 'time'})

        pi_events.time = (pi_events.time - raw_separated.time_raw.min()) / 1000

        print(pi_data_fnames[i][5:-4])
        print(signal_data_fnames[i][10:-4].replace('_', '-').replace('T', '_'))
        print(arduino_data_fnames[i][21:-4].replace('_', '-').replace('T', '_'))
        save_path = os.path.join(save_root, session_name)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        pi_events.to_pickle(os.path.join(save_path, 'pi_events.pkl'))
        dFF0.to_pickle(os.path.join(save_path, 'neural_events.pkl'))

    # pi_events, neural_events = data_read_sync()

    # info = read_pi_meta(pi_dir)

    # session_names.appe
    # file_paths.append(os.path.join(root, filename))
    # file_names.append(filename)


if __name__ == '__main__':
    preprocess()
