from functions import sleep_if, copy_if_missing, google_copy, run_catgt, generate_file_lists, pi_process, prep_phy, \
    copy_phy_output
import os
import shutil
import pandas as pd
import numpy as np
from time import sleep
from file_paths import root_file_paths


def run_pipeline():
    sleepy = False
    while True:
        file_paths = root_file_paths()
        sleep_if(sleepy)
        copy_if_missing()  # Copy new files to external hard drive

        sleep_if(sleepy)
        # google_copy()  # Copy new files to google cloud storage

        sleep_if(sleepy)
        run_catgt()  # Run catgt anywhere it hasnt been run

        # Find pi file
        sleep_if(sleepy)
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        pi_process(file_paths, session_list)

        # Run spike interface to get phy folder prepped
        sleep_if(sleepy)
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        prep_phy(file_paths, session_list)

        # Transfer phy outputs if sorting is complete, and remove phy folder from prep
        sleep_if(sleepy)
        session_list, file_list = generate_file_lists(file_paths=file_paths)
        copy_phy_output(session_list, file_paths)

        sleep(10)
        # break


if __name__ == '__main__':
    run_pipeline()
