# google_copy.py
import os
from file_paths import root_file_paths
from google.cloud import storage
import glob
import time
import json
import tkinter as tk
import tkinter.font as font
from threading import Thread

"""
A lot of the paths and functions in this file are specific to the evolving file structure of my (Elissa's) data
in the cloud. You can use this as a basis, but much of it will need to be changed. For this all files (original and 
processed) are stored on an external harddrive located by 'file_paths['external_path']'. The google_copy function copies
only the original (spikeGLX generated) files from that location to the cloud. You can change your 'external_path' 
location in 'file_paths.py' to have it copy from somewhere else. You can also remove the condition at the beginning of
the for loop ('for local_file in rel_paths:') to have it copy everything instead of just the original files. You will 
also need to change the 'key_file' location to you own credential file, which you can get from the google cloud console.
"""

stop = False
stopped = False


def google_copy():
    global stop
    global stopped
    t1 = Thread(target=StopButton)
    t1.start()
    project_dir = os.getcwd() if not os.path.basename(os.getcwd()) == 'functions' else os.path.dirname(os.getcwd())
    json_path = os.path.join(project_dir, 'cloud_archive.json')
    file_paths = root_file_paths()
    # change the line below to your own google cloud key file location
    key_file = os.path.join('C:\\', 'cloud', 'subtle-fulcrum-342318-b959d7141166.json')
    rel_paths = glob.glob(file_paths['external_path'] + '/**', recursive=True)
    cloud_archive = get_cloud_files(refresh=False)
    for local_file in rel_paths:
        if os.path.isfile(local_file):
            if not ((local_file[-16:] == '_t0.imec0.ap.bin') or (local_file[-17:] == '_t0.imec0.ap.meta') or
                    (local_file[-12:] == '_t0.nidq.bin') or (local_file[-13:] == '_t0.nidq.meta')):
                continue  # this skips the rest of the for loop if the file is not a SpikeGLX generated file
            local_path_parts = local_file.split(os.sep)
            remote_path = f'{"/".join(local_path_parts[len(file_paths["external_path"].split(os.sep)):])}'
            if remote_path in cloud_archive['archived']:
                continue
            print('Connecting to google cloud')
            storage_client = storage.Client.from_service_account_json(key_file, project='subtle-fulcrum')
            archive_bucket = storage_client.get_bucket('elissa_neuropixel_data')
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
            # else:
            #     print(f'uploading {full_remote_path}...' + ''.join(max(130 - len(full_remote_path), 1) * [' ']), end='')
            #     print('already uploaded')
        if stop:
            print('Stopped uploading to google cloud')
            stopped = True
            break
    if not stopped:
        print('Finished uploading to google cloud')
    stopped = True


def get_cloud_files(refresh=False):
    """
    This checks what files are currently on the cloud and saves them in a .json file. It costs a little money every time
    we check, so only run this with refresh=True if you manually changed which files are on the cloud. Otherwise the
    google_copy function will update the .json every time it uploads a new file and you will never need to scan the
    cloud, so we save some money.
    """
    project_dir = os.getcwd() if not os.path.basename(os.getcwd()) == 'functions' else os.path.dirname(os.getcwd())
    json_path = os.path.join(project_dir, 'cloud_archive.json')
    if os.path.exists(json_path):
        cloud_archive = load_json(json_path)
        cloud_archive['archived'].sort()

    else:
        cloud_archive = {'archived': []}
        save_json(json_path, cloud_archive)

    if refresh:
        # There are two here because my files are in two separate buckets, you should just have the subtle-fulcrum one.
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


class StopButton:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("300x200")
        self.root.title('Google Upload')
        my_font = font.Font(size=16)
        self.button = tk.Button(
            master=self.root,
            text='Stop After Current Upload',
            font=my_font,
            width=40,
            height=12,
            bg="white",
            fg="black",
            command=self.stop)
        self.button.pack()
        self._job = self.root.after(1000, self.check_continue)
        self.root.mainloop()

    def stop(self):
        global stop
        stop = True

    def check_continue(self):
        global stopped
        if stopped:
            if self._job is not None:
                self.root.after_cancel(self._job)
                self._job = None
            self.root.destroy()
        else:
            self._job = self.root.after(1000, self.check_continue)


if __name__ == '__main__':
    # get_cloud_files(refresh=True)
    google_copy()
