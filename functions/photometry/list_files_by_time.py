import os
import time


def list_files_by_time(dir_name, file_type=None, print_names=False):
    # Get list of all files only in the given directory
    if file_type is None:
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)),
                               os.listdir(dir_name))
    else:
        list_of_files = filter(lambda x: os.path.isfile(os.path.join(dir_name, x)) and file_type in x,
                               os.listdir(dir_name))
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted(list_of_files,
                           key=lambda x: os.path.getmtime(os.path.join(dir_name, x))
                           )
    if print_names:
        # Iterate over sorted list of files and print file path
        # along with last modification time of file
        for file_name in list_of_files:
            file_path = os.path.join(dir_name, file_name)
            timestamp_str = time.strftime('%m/%d/%Y :: %H:%M:%S',
                                          time.gmtime(os.path.getmtime(file_path)))
            print(timestamp_str, ' -->', file_name)
    return list_of_files


if __name__ == '__main__':
    animal_str = 'SZ030'
    lab_dir = os.path.join('C:\\', 'Users', 'Shichen', 'OneDrive - Johns Hopkins', 'ShulerLab')
    animal_dir = os.path.join(lab_dir, 'TemporalDecisionMaking', 'imaging_during_task', animal_str)
    raw_dir = os.path.join(animal_dir, 'raw_data')
    # all_files = list_files_by_time(raw_dir, print_names=0)
    behav_files = list_files_by_time(raw_dir, file_type=".txt", print_names=0)
    neural_files = list_files_by_time(raw_dir, file_type="FP", print_names=0)
    ttl_files = list_files_by_time(raw_dir, file_type="arduino", print_names=0)

