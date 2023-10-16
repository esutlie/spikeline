import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np


def data_read_sync(pi_dir, signal_dir, arduino_dir):
    pi_events = pd.read_csv(pi_dir, na_values=['None'], skiprows=3)

    neural_events = np.loadtxt(signal_dir)
    columns = ['timestamps', 'timestamps_we_dont_like', 'green_right', 'green_left']
    neural_events = pd.DataFrame(neural_events, columns=columns)
    # neural_events.drop(0, inplace=True)
    # neural_events.reset_index(drop=True, inplace=True)
    signal_types = ['actual', 'isosbestic'] * len(neural_events)
    neural_events['signal_type'] = signal_types[:len(neural_events)]
    if (len(neural_events) % 2) == 1:
        neural_events = neural_events.iloc[:-1, :]

    # neural_events[neural_events.signal_type == 'actual'].green_right.to_numpy()

    arduino_events = pd.read_csv(arduino_dir, delimiter=' ', header=None)
    arduino_events = arduino_events.rename(columns={0: 'signal_bool', 1: 'timestamp'})
    arduino_events = arduino_events.drop(arduino_events.columns[2], axis=1)
    # arduino_events = arduino_events[['signal_bool', 'timestamp']]

    duplicates = arduino_events.timestamp.values[1:] == arduino_events.timestamp.values[:-1]
    arduino_events = arduino_events.loc[np.where(~duplicates)[0]]
    arduino_events.reset_index(drop=True, inplace=True)

    edges = arduino_events.signal_bool.values[1:].astype(int) - arduino_events.signal_bool.values[:-1].astype(int)
    highs = arduino_events.loc[np.where(edges == 1)[0] + 1].timestamp.values / 1000
    lows = arduino_events.loc[np.where(edges == 1)[0]].timestamp.values / 1000
    other_times = (highs + lows) / 2

    # other_times[1:]-other_times[:-1]
    camera = pi_events.key == 'camera'
    start = pi_events.value == 1
    pi_times = pi_events[camera & start].session_time.to_numpy()
    # pi_times[1:]-pi_times[:-1]

    minlen = min(len(other_times), len(pi_times))
    pi_times = pi_times[-minlen:]
    other_times = other_times[-minlen:]

    reg = LinearRegression().fit(pi_times.reshape(-1, 1), other_times)
    adjusted_pi_times = reg.predict(pi_events.session_time.to_numpy().reshape(-1, 1))
    pi_events['time'] = adjusted_pi_times * 1000
    pi_times = pi_events[camera & start].time.to_numpy()
    pi_times = pi_times[-len(other_times):] / 1000

    print(f'first pass median error: {np.median(np.abs(pi_times - other_times))}')

    return pi_events, neural_events
