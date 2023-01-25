from functions import *
import os
import shutil
import pandas as pd
import numpy as np
from time import sleep
from file_paths import root_file_paths


def run_pipeline():
    # File paths:
    file_paths = root_file_paths()


    while True:
        # Transfer new files
        # sleep_if()
        copy_if_missing(file_paths)

        # Run catgt on files where it's missing
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        for session in session_list['external_path']:
            if not os.path.isfile(os.path.join(file_paths['external_path'], session, session + '_imec0',
                                               session + '_tcat.imec0.ap.xd_384_6_0.txt')):
                path = os.path.join(file_paths['external_path'], session)
                catgt(path, path)


        # Find pi file
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        pi_process(file_paths, session_list)

        # Run spike interface to get phy folder prepped
        # sleep_if()
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        prep_phy(file_paths, session_list, file_list)

        # Transfer phy outputs if sorting is complete, and remove phy folder from prep
        # sleep_if()
        try:
            session_list, file_list = generate_file_lists(file_paths=file_paths)
            copy_phy_output(session_list, file_paths)
        finally:
            print('waited for copy_phy_output to finish')

        sleep(10)
        break


if __name__ == '__main__':
    run_pipeline()
