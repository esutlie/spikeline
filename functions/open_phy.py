# open_phy.py
import os
from functions.generate_file_lists import get_directories


def open_phy(save_folder):
    anaconda_prompt_cmd = ' '.join([os.path.join('C:\\', 'Users', 'Elissa', 'Anaconda3', 'Scripts', 'activate.bat'),
                                    os.path.join('C:\\', 'Users', 'Elissa', 'Anaconda3')])
    folder_path = f'cd /d {save_folder}'
    os.system(
        r"""start "My Spyder Package Installer" /wait cmd /c "%s&%s&%s&%s" """ % (
            anaconda_prompt_cmd, 'conda activate phy2', folder_path, 'phy template-gui params.py'))


if __name__ == '__main__':
    path = os.path.join('C:\\', 'phy_ready')
    dirs = get_directories(path)
    # open_phy(os.path.join(path, dirs[10]))
    for d in dirs:
        try:
            open_phy(os.path.join(path, d))
        finally:
            print('waited for open_phy to finish')
