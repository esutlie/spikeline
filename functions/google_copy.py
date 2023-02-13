# copy_if_missing.py
import os
import shutil
from functions import generate_file_lists
from file_paths import root_file_paths
from google.cloud import storage


def google_copy(file_paths):
    storage_client = storage.Client(project='spikeline')
    archive_bucket = storage_client.get_bucket('spikeline_archive')
    archive_files = storage_client.list_blobs('spikeline_archive')

    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for file in file_list['origin_path']:
        file_path = file.split(os.sep)
        external_path = os.path.join(file_paths['external_path'],
                                     *file_path[len(file_paths['origin_path'].split(os.sep)):])
        if external_path not in file_list['external_path']:
            dest = os.path.dirname(external_path)
            if not os.path.isdir(dest):
                os.mkdir(dest)
            print(f'copying {file} to {file_paths["external_path"]}')
            shutil.copy(file, external_path)


if __name__ == '__main__':
    paths = root_file_paths()
    google_copy(paths)
