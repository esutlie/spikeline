import numpy as np

from functions import catgt, generate_file_lists
from file_paths import root_file_paths
import os


def combined_session():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    mice = []
    for session in session_list:
        mice.append(session[:5])
    mice = np.array(mice)
    # for mouse in np.unique(mice):


if __name__ == '__main__':
    combined_session()
