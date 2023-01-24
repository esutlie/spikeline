import boto3
import os
import json


def upload_to_archive(root, local_path, replace=False):
    path_parts = local_path.split(os.sep)
    remote_path = '/'.join(path_parts)
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket='elissa-archive')
    contents = response.get("Contents")
    contents = [info['Key'] for info in contents]
    print(f'uploading {path_parts[-1]}')
    if remote_path not in contents or replace:
        s3.upload_file(os.path.join(root, local_path), 'elissa-archive', remote_path)


def upload_to_input(root, local_path, replace=False):
    s3 = boto3.client('s3')
    s3.Bucket('hushu-input').objects.all()
    s3.Bucket('hushu-input').upload_file(os.path.join(root, local_path), local_path)


def get_transfer_record():
    if os.path.exists('sorting_record.json'):
        with open('sorting_record.json', 'r') as openfile:
            return json.load(openfile)
    else:
        transfer_record = {"success": [],
                           "fail": []}
        save_transfer_record(transfer_record)
        return transfer_record


def save_transfer_record(d):
    json_object = json.dumps(d, indent=4)
    with open("transfer_record.json", "w") as outfile:
        outfile.write(json_object)
