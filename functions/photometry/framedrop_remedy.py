import numpy as np
from matplotlib import pyplot as plt


def check_channel_switching(actual_np, isos_np):
    actual_minus_isos = actual_np - isos_np
    try:
        sign_change = actual_minus_isos[1:] / actual_minus_isos[:-1]
    except:
        pass
    indices_switch = np.asarray(np.where(sign_change < 0))
    if indices_switch.any():
        indices_switch = indices_switch + 1
    return indices_switch


def framedrop_remedy(raw_deinterleaved, plot='False'):
    num_color_site = int(len(raw_deinterleaved.columns) / 2 - 1)
    for i in range(num_color_site):
        actual_np = raw_deinterleaved.iloc[:, i * 2 + 1].to_numpy()
        isos_np = raw_deinterleaved.iloc[:, (i + 1) * 2].to_numpy()
        indices_switch = check_channel_switching(actual_np, isos_np)

        if indices_switch.any():
            total_indices_num = len(indices_switch[0])
            if (len(indices_switch) % 2) == 1:
                temporary_isos = isos_np[indices_switch[0, -1]:]
                replacement_array = np.copy(temporary_isos)
                isos_np[indices_switch[0, -1]:] = actual_np[indices_switch[0, -1]:]

                actual_np[indices_switch[0, -1]:] = replacement_array
                total_indices_num = total_indices_num - 1

            if total_indices_num > 0:
                for j in range(int(total_indices_num / 2)):
                    index_range = np.arange(indices_switch[0, (2 * j)], indices_switch[0, (2 * j + 1)], 1)
                    temp_isos = isos_np[index_range]
                    replc_arr = np.copy(temp_isos)
                    isos_np[index_range] = actual_np[index_range]
                    actual_np[index_range] = replc_arr
    if plot:
        plt.style.use('ggplot')
        for i in range(num_color_site):
            plt.plot(raw_deinterleaved.iloc[:, 0], raw_deinterleaved.iloc[:, 2 * i + 1],
                     label=raw_deinterleaved.columns.values[2 * i + 1])
            plt.plot(raw_deinterleaved.iloc[:, 0], raw_deinterleaved.iloc[:, 2 * (i + 1)],
                     label=raw_deinterleaved.columns.values[2 * (i + 1)])
        plt.legend()
        plt.title('raw deinterleaved after framedrop remedy')
        plt.show()

    return raw_deinterleaved
