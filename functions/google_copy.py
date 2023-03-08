# copy_if_missing.py
import os
import shutil
from functions import generate_file_lists
from file_paths import root_file_paths
from google.cloud import storage
import glob
# from functions import Timer
import time
import json

"""A lot of the paths and functions in this file are specific to the evolving file structure of my (Elissa's) data
in the cloud. You can use this as a basis, but much of it will need to be changed."""


def google_copy():
    json_path = os.path.join(os.getcwd(), 'cloud_archive.json')
    file_paths = root_file_paths()
    key_file = os.path.join('C:\\', 'cloud', 'subtle-fulcrum-342318-b959d7141166.json')
    storage_client = storage.Client.from_service_account_json(key_file, project='subtle-fulcrum')
    archive_bucket = storage_client.get_bucket('elissa_neuropixel_data')
    rel_paths = glob.glob(file_paths['external_path'] + '/**', recursive=True)
    cloud_archive = get_cloud_files(json_path=json_path, refresh=False)
    for local_file in rel_paths:
        if os.path.isfile(local_file):
            local_path_parts = local_file.split(os.sep)
            remote_path = f'{"/".join(local_path_parts[len(file_paths["external_path"].split(os.sep)):])}'
            if remote_path in cloud_archive['archived']:
                continue
            full_remote_path = 'recordings/' + remote_path
            origin_path = os.path.join(file_paths['origin_path'],
                                       *local_path_parts[len(file_paths["external_path"].split(os.sep)):])
            blob = archive_bucket.blob(full_remote_path)
            if not blob.exists():
                print(f'uploading {full_remote_path}...' + ''.join(max(130 - len(full_remote_path), 1) * [' ']), end='')
                tic = time.time()
                try:
                    if os.path.exists(origin_path):
                        blob.upload_from_filename(origin_path, timeout=600)
                    else:
                        blob.upload_from_filename(local_file, timeout=600)
                    print('done')
                    print(f'uploaded in {time.time() - tic} seconds')
                    cloud_archive['archived'].append(remote_path)
                    save_json(json_path, cloud_archive)
                except Exception as e:
                    print('failed')
                    print(f'attempt took {time.time() - tic} seconds')
                    print(e)
            else:
                print(f'uploading {full_remote_path}...' + ''.join(max(130 - len(full_remote_path), 1) * [' ']), end='')
                print('already uploaded')

    print('Finished uploading to google cloud')


def get_cloud_files(json_path=os.path.join(os.getcwd(), 'cloud_archive.json'), refresh=False):
    if os.path.exists(json_path):
        cloud_archive = load_json(json_path)
        cloud_archive['archived'].sort()

    else:
        cloud_archive = {'archived': []}
        save_json(json_path, cloud_archive)

    if refresh:
        archive_files1 = cloud_file_list('subtle-fulcrum-342318-b959d7141166', 'subtle-fulcrum',
                                         'elissa_neuropixel_data')
        archive_files2 = cloud_file_list('spikeline-753a261c881e', 'spikeline', 'spikeline_archive')
        archive_files1 = ['/'.join(file.split('/')[1:]) for file in archive_files1]
        cloud_archive['archived'] = archive_files1 + archive_files2
        cloud_archive['archived'].sort()
        save_json(json_path, cloud_archive)
    return cloud_archive


def save_json(path, var):
    json_object = json.dumps(var, indent=4)
    with open(path, "w") as outfile:
        outfile.write(json_object)


def load_json(path):
    with open(path, 'r') as openfile:
        var = json.load(openfile)
    return var


def cloud_file_list(key_name, project, bucket):
    key_file = os.path.join('C:\\', 'cloud', f'{key_name}.json')
    storage_client = storage.Client.from_service_account_json(key_file, project=project)
    return [blob.name for blob in storage_client.list_blobs(bucket)]


if __name__ == '__main__':
    # get_cloud_files(refresh=True)
    google_copy()
