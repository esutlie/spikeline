import os


def root_file_paths(origin_path=os.path.join('D:\\', 'recordings'),
                    external_path=os.path.join('E:\\', 'neuropixel_data'),
                    phy_ready_path=os.path.join('C:\\', 'phy_ready'),
                    phy_holding_path=os.path.join('E:\\', 'phy_holding'),
                    pi_path=os.path.join('C:\\', 'Users', 'Elissa', 'GoogleDrive', 'Code', 'Python', 'behavior_code',
                                         'data'),
                    processed_data=os.path.join('C:\\', 'processed_data')):
    """change root filepaths here to your own"""

    file_paths = {
        'origin_path': origin_path,
        'external_path': external_path,
        'phy_ready_path': phy_ready_path,
        'phy_holding_path': phy_holding_path,
        'pi_path': pi_path,
        'processed_data': processed_data
    }
    return file_paths
