import matplotlib.pyplot as plt


def moving_average_denoise(detrended_df, session_label, plot='False', win_size=8):
    denoised_df = detrended_df
    for i in range(len(detrended_df.columns) - 2):
        denoised_df.iloc[:, i + 1] = detrended_df.iloc[:, i + 1].rolling(win_size).mean()
        denoised_df.iloc[0:win_size, i + 1] = denoised_df.iloc[win_size, i + 1]

    if plot:
        plt.style.use('ggplot')
        for k in range(len(detrended_df.columns) - 2):
            plt.plot(denoised_df.iloc[10000:15000, 0], denoised_df.iloc[10000:15000, k + 1],
                     label=denoised_df.columns.values[k + 1])
        plt.legend()
        plt.title(session_label + ' Moving average denoised')
        plt.xlabel('Time recording')
        plt.ylabel('FP readout')
        plt.show()

    return denoised_df
