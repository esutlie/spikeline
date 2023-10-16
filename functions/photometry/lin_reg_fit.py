import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def lin_reg_fit(denoised_df, session_label, plot='False'):
    num_color_site = int(len(denoised_df.columns) / 2 - 1)
    fitted_df = denoised_df
    for i in range(num_color_site):
        x = denoised_df.iloc[:, (i + 1) * 2].to_numpy().reshape(-1, 1)  # x - isosbestic
        y = denoised_df.iloc[:, i * 2 + 1].to_numpy().reshape(-1, 1)  # y - actual
        reg = LinearRegression().fit(x, y)
        fitted_isos = reg.predict(x)
        fitted_df.iloc[:, (i + 1) * 2] = fitted_isos

    if plot:
        plt.style.use('ggplot')
        for i in range(num_color_site):
            plt.plot(fitted_df.iloc[10000:15000, 0], fitted_df.iloc[10000:15000, i * 2 + 1],
                     label=fitted_df.columns.values[i * 2 + 1])
            plt.plot(fitted_df.iloc[10000:15000, 0], fitted_df.iloc[10000:15000, (i + 1) * 2],
                     label=fitted_df.columns.values[(i + 1) * 2])
        plt.legend()
        plt.xlabel('Time recording (msec)')
        plt.ylabel('Fluorescence intensity')
        plt.title(session_label + ' After linear regression fitting')
        plt.show()
    return fitted_df
