import numpy as np
from file_paths import root_file_paths
from functions.generate_file_lists import get_filepaths, generate_file_lists
import os
import pandas as pd


def gen_full_template(templates, template_ind):
    templates_full = np.zeros([templates.shape[0], templates.shape[1], 384])
    for i in range(template_ind.shape[0]):
        for j in range(template_ind.shape[1]):
            templates_full[i, :, template_ind[i, j]] = templates[i, :, j]
    return templates_full


def add_templates(session):
    phy_dir = os.path.join(file_paths['external_path'], session, 'phy_output')
    data_dir = os.path.join(file_paths['external_path'], session, 'processed_data')

    templates = np.load(os.path.join(phy_dir, 'templates.npy'))
    template_ind = np.load(os.path.join(phy_dir, 'template_ind.npy'))

    np.save(os.path.join(data_dir, 'templates'), templates)
    np.save(os.path.join(data_dir, 'template_ind'), template_ind)


def add_template_ids(session):
    print(session)
    phy_dir = os.path.join(file_paths['external_path'], session, 'phy_output')
    data_dir = os.path.join(file_paths['external_path'], session, 'processed_data')

    cluster_info = pd.read_pickle(os.path.join(data_dir, 'cluster_info.pkl'))

    template_id = pd.read_csv(os.path.join(phy_dir, 'cluster_si_unit_ids.tsv'), sep='\t')
    template_id = template_id.set_index('si_unit_id')
    template_id.loc[-1] = np.nan
    ind = cluster_info.si_unit_id.values
    ind[np.isnan(ind)] = -1
    cluster_info['template_id'] = template_id.loc[cluster_info.si_unit_id.values].cluster_id.values

    cluster_info.to_pickle(os.path.join(data_dir, 'cluster_info.pkl'))


if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for session in session_list['external_path']:
        try:
            # add_templates(session)  # should be redundant with pi process for all future sessions
            add_template_ids(session)  # should be redundant with pi process for all future sessions
        except FileNotFoundError:
            pass
