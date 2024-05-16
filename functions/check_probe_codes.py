import os


def check_probe_codes(folder):
    probe_codes = []
    for root, directories, files in os.walk(folder):
        for folder_name in directories:
            if folder_name[-5:-1] == 'imec':
                probe_codes.append(folder_name[-5:])
        break
    return probe_codes
