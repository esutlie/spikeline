import os
import shutil
from generate_file_lists import generate_file_lists
from file_paths import root_file_paths
import numpy as np
from sklearn.preprocessing import normalize
import pandas as pd
import scipy.spatial as sp
import math
import matplotlib.pyplot as plt


def same_unit_lists(file_paths, session_list):
    template_list = []
    mouse_ids = []
    session_name = []
    good_units = []
    unit_channels = []
    for session in session_list['external_path']:
        path = os.path.join(file_paths['external_path'], session, 'processed_data')
        if os.path.exists(path):
            templates = np.load(os.path.join(path, 'templates.npy'))
            cluster_info = pd.read_pickle(os.path.join(path, 'cluster_info.pkl'))
            good_ids = cluster_info['id'].values
            channels = cluster_info.set_index('id')['ch']
            template_list.append(templates)
            mouse_ids.append(session[:5])
            session_name.append(session)
            good_units.append(good_ids)
            unit_channels.append(channels)
    per_mouse_list = []
    for mouse in np.unique(mouse_ids):
        mouse_inds = np.where(np.array(mouse_ids) == mouse)[0]
        per_sess1_list = []
        for i in mouse_inds:
            template1 = template_list[i]
            channels1 = unit_channels[i]
            units1 = good_units[i]
            per_sess2_list = []
            for j in mouse_inds:
                unit_similarity = np.zeros([len(good_units[i]), len(good_units[j])])
                if i != j:
                    template2 = template_list[j]
                    channels2 = unit_channels[j]
                    units2 = good_units[j]
                    for u1_ind, u1 in enumerate(units1):
                        for u2_ind, u2 in enumerate(units2):
                            channel_dif = channels1[u1] - channels2[u2]
                            if (channel_dif > 3) or (u1 >= len(template1)) or (u2 >= len(template2)):
                                similarity = 0
                            else:
                                argmax1 = np.argmax(np.max(abs(template1[u1, :, :]), axis=0, keepdims=True))
                                argmax2 = np.argmax(np.max(abs(template2[u2, :, :]), axis=0, keepdims=True))
                                min1 = channels1[u1] - argmax1
                                max1 = channels1[u1] + len(template1[u1, 0, :]) - argmax1
                                min2 = channels2[u2] - argmax2
                                max2 = channels2[u2] + len(template2[u2, 0, :]) - argmax2
                                combined_max = min([max1, max2])
                                combined_min = max([min1, min2])
                                if combined_min < combined_max:
                                    min_trim1 = max([0, argmax1 - channels1[u1] + combined_min])
                                    max_trim1 = min([len(template1[u1, 0, :]), argmax1 - channels1[u1] + combined_max])
                                    min_trim2 = max([0, argmax2 - channels2[u2] + combined_min])
                                    max_trim2 = min([len(template2[u2, 0, :]), argmax2 - channels2[u2] + combined_max])
                                    template1_trimmed = template1[u1, :, min_trim1:max_trim1]
                                    template2_trimmed = template2[u2, :, min_trim2:max_trim2]
                                    similarity = math.sqrt(sum(sum((template1_trimmed - template2_trimmed) ** 2)))
                                else:
                                    similarity = 0
                            unit_similarity[u1_ind, u2_ind] = similarity
                per_sess2_list.append(unit_similarity)
            per_sess1_list.append(per_sess2_list)
        per_mouse_list.append(per_sess1_list)
    for i, mouse in enumerate(np.unique(mouse_ids)):
        similarities = per_mouse_list[i]
        flat_list = [val.tolist() for sublist in similarities for val in sublist]
        flat_list2 = [val for sublist in flat_list for val in sublist]
        flat_list3 = [val for sublist in flat_list2 for val in sublist]
        flat_list4 = [val if val != np.inf else 0 for val in flat_list3]
        flat_list5 = [val for val in flat_list4 if val != 0]
        plt.hist(flat_list5, bins=1000, range=(0, 500))
        plt.show()

        np.column_stack([val for sublist in similarities for val in sublist])

    print('test')


if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    same_unit_lists(file_paths, session_list)
