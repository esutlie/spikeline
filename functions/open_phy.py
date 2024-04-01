# open_phy.py
import os
from functions.generate_file_lists import get_directories
from functions.unit_counts import get_unit_count
from file_paths import root_file_paths


def open_phy(save_folder):
    anaconda_prompt_cmd = ' '.join([os.path.join('C:\\', 'Users', 'Elissa', 'Anaconda3', 'Scripts', 'activate.bat'),
                                    os.path.join('C:\\', 'Users', 'Elissa', 'Anaconda3')])
    folder_path = f'cd /d {save_folder}'
    os.system(
        r"""start "My Spyder Package Installer" /wait cmd /c "%s&%s&%s&%s" """ % (
            anaconda_prompt_cmd, 'conda activate phy2', folder_path, 'phy template-gui params.py'))


if __name__ == '__main__':
    file_paths = root_file_paths()
    path = file_paths['phy_ready_path']
    dirs = get_directories(path)
    # open_phy(os.path.join(path, dirs[10]))
    for d in dirs[0:]:
        try:
            open_phy(os.path.join(path, d))
            print(f'{d}: {get_unit_count(os.path.join(path, d))}')
        finally:
            print()
