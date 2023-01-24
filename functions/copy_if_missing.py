# copy_if_missing.py
import os
import shutil


def copy_if_missing(source_list, destination_list):
    for file in source_list:
        file_path = file.split(os.sep)
        external_path = os.path.join(destination_list, *file_path[2:])
        if external_path not in destination_list:
            dest = os.path.dirname(external_path)
            if not os.path.isdir(dest):
                os.mkdir(dest)
            shutil.copy(file, external_path)



