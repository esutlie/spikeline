# reset_folder.py
import os
from shutil import rmtree


def reset_folder(name, local=True):
    count = 0
    while True:
        save_folder = name + str(count)
        folder_path = f'./{save_folder}' if local else save_folder
        try:
            if os.path.isdir(folder_path):
                rmtree(folder_path)
            break
        except PermissionError:
            count += 1
    return save_folder
