import numpy as np


def check_framedrop(neural_events):
    latter = neural_events.timestamps[1:].to_numpy()
    former = neural_events.timestamps[:-1].to_numpy()
    timestamp_diff = latter - former
    u = np.mean(timestamp_diff)
    s = np.std(timestamp_diff)
    frame_drop = np.array(np.where((timestamp_diff > u + 20 * s) | (timestamp_diff < u - 20 * s)))
    if not frame_drop.any():
        print(f'No abnormal frame rate detected')
    else:
        print(f'Abnormal frame rate detected in neural_events: {frame_drop}')
        print(f'These abnormal timestamp differences are: {timestamp_diff[frame_drop]} msec.')