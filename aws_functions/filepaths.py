import os
import boto3


# def get_filepaths(directory=os.path.join('D:\\', 'Test')):
#     # List to store paths
#     file_paths = []
#
#     # Walk through directory
#     for root, directories, files in os.walk(directory):
#         for filename in files:
#             # Add filename to list
#             file_paths.append(os.path.join(root, filename))
#
#             # Return all paths
#     return file_paths
#
# def get_directories(directory=os.path.join('D:\\', 'Test')):
#     # List to store paths
#     directory_list = []
#
#     # Walk through directory
#     for root, directories, files in os.walk(directory):
#         for d in directories:
#             # Add filename to list
#             directory_list.append(d)
#
#             # Return all paths
#     return directory_list

\
def get_file_paths_in_s3_bucket(bucket_name):
    s3 = boto3.client('s3')
    bucket = s3.list_objects(Bucket=bucket_name)
    file_paths = []
    for file in bucket['Contents']:
        file_paths.append(file['Key'])
    return file_paths