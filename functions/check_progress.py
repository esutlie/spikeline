import os
import shutil
from functions.generate_file_lists import generate_file_lists
from file_paths import root_file_paths
import numpy as np


def check_progress():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    processed = len(session_list['phy_processed_list'])
    total = len(session_list['external_path'])
    print(f'{processed} sessions sorted out of {total}')
    names = np.unique([s[:5] for s in session_list['external_path']])
    for mouse in names:
        processed = np.sum([mouse == s[:5] for s in session_list['phy_processed_list']])
        total = np.sum([mouse == s[:5] for s in session_list['external_path']])
        print(f'{mouse}: {processed} sessions sorted out of {total}')


if __name__ == '__main__':
    check_progress()
