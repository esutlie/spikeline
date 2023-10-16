import matplotlib.pyplot as plt
import pandas as pd


def de_interleave(neural_events, session_label, plot=False):
    green_right_actual = neural_events[neural_events.signal_type == 'actual'].green_right.to_numpy()
    green_right_isos = neural_events[neural_events.signal_type == 'isosbestic'].green_right.to_numpy()
    green_left_actual = neural_events[neural_events.signal_type == 'actual'].green_left.to_numpy()
    green_left_isos = neural_events[neural_events.signal_type == 'isosbestic'].green_left.to_numpy()
    time_raw = neural_events[neural_events.signal_type == 'actual'].timestamps
    time_recording = time_raw - neural_events.timestamps[0]
    time_recording = time_recording.to_numpy()
    raw_neural_deinterleaved = pd.DataFrame(
        data=[time_recording, green_right_actual, green_right_isos, green_left_actual,
              green_left_isos, time_raw.to_numpy()]).T
    raw_neural_deinterleaved.columns = ['time_recording', 'green_right_actual', 'green_right_isos', 'green_left_actual',
                                        'green_left_isos', 'time_raw']

    if plot:
        num_color_site = int(len(raw_neural_deinterleaved.columns) / 2 - 1)
        plt.style.use('ggplot')
        for i in range(num_color_site):
            plt.plot(raw_neural_deinterleaved.iloc[:, 0], raw_neural_deinterleaved.iloc[:, 2 * i + 1],
                     label=raw_neural_deinterleaved.columns.values[2 * i + 1])
            plt.plot(raw_neural_deinterleaved.iloc[:, 0], raw_neural_deinterleaved.iloc[:, 2 * (i + 1)],
                     label=raw_neural_deinterleaved.columns.values[2 * (i + 1)])
        plt.legend()
        plt.title(session_label + ' raw deinterleaved')
        plt.show()
    return raw_neural_deinterleaved