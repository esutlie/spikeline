from scipy import signal
import matplotlib.pyplot as plt
import numpy as np


def butterworth_detrend(raw_separated, session_label, fps=80, plot='False'):
    detrended = raw_separated
    sos = signal.butter(2, 0.1, btype='highpass', fs=fps / 2, output='sos')
    plt.style.use('ggplot')
    for i in range(len(raw_separated.columns) - 2):
        sig = np.zeros(len(raw_separated) + 400)
        sig[400:] = raw_separated.iloc[:, i + 1].to_numpy()
        sig[0:400] = sig[400:800]
        sig = signal.sosfilt(sos, sig) + np.mean(sig)
        detrended.iloc[:, i + 1] = sig[400:]
        if plot:
            plt.plot(detrended.iloc[:, 0], detrended.iloc[:, i + 1], label=raw_separated.columns.values[i + 1])

    if plot:
        plt.legend()
        plt.title(session_label + ' signals after butterworth highpass filter')
        plt.show()

    return detrended
