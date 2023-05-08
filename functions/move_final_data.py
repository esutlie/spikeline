import os
import shutil
from generate_file_lists import generate_file_lists
from file_paths import root_file_paths


def move_final_data(dest=os.path.join('C://', 'processed_data'), replace=True):
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    if not os.path.exists(dest):
        os.mkdir(dest)
    for session in session_list['external_path']:
        path = os.path.join(file_paths['external_path'], session, 'processed_data')
        dest_path = os.path.join(dest, session)
        if os.path.exists(path):
            if replace and os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            if not os.path.exists(dest_path):
                shutil.copytree(path, dest_path)
                print(f'copied {session} final data')


if __name__ == '__main__':
    move_final_data()
