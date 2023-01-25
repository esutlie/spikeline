# catgt.py
import os
from functions.generate_file_lists import generate_file_lists


def catgt(input_path, output_path):
    tools_path = os.path.join('C:\\', 'spikeGLX', 'Tools')

    path_parts = input_path.split(os.sep)
    run_name = path_parts[-1]
    directory = os.path.join(*path_parts[:-1])
    event_extractors = ''
    event_extractors += f'-xd=0,0,-1,{13},0 '  # extractors: stream type,stream index,word,bit,millisec

    print(f'Running CatGT for {run_name}...')
    command = f'runit.bat -dir={directory} -run={run_name[0:-3]} -g={run_name[-1]},{run_name[-1]} -t=0,0 -prb=0 -ap -xd=2,0,-1,6,0' \
              f'-dest={output_path} -prb_fld -out_prb_fld -no_auto_sync -no_tshift'
    # command = f'runit.bat -dir={directory} -run={run_name[0:-3]} -g={run_name[-1]},{run_name[-1]} -t=0,0 -ap ' \
    #           f'-prb=0 -ni {event_extractors} -dest={output_path} -prb_fld -out_prb_fld -pass1_force_ni_ob_bin'
    # command = f'runit.bat -dir={input_path} -run={run_name[0:-3]} -prb_fld -g={run_name[-1]},{run_name[-1]} -t=0,0 -ap ' \
    #           f'-prb=0 -ni {event_extractors} -dest={output_path} -out_prb_fld -pass1_force_ni_ob_bin'
    result = os.system(f"cd {os.path.join(tools_path, 'CatGT-win')} & {command}")
    if result == 0:
        print(f'{run_name} done')
    else:
        print(f'{run_name} catgt failed with exit code {result}. Check catgt.log in {tools_path}')



if __name__ == '__main__':
    file_paths = {
        'origin_path': os.path.join('D:\\', 'recordings'),
        'external_path': os.path.join('E:\\', 'neuropixel_data'),
        'phy_ready_path': os.path.join('C:\\', 'phy_ready'),
        'phy_holding_path': os.path.join('E:\\', 'phy_holding'),
        'pi_path': os.path.join('C:\\', 'Users', 'Elissa', 'GoogleDrive', 'Code', 'Python', 'behavior_code', 'data'),
        'processed_data': os.path.join('C:\\', 'processed_data')
    }

    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for session in session_list['external_path']:
        if not os.path.isfile(os.path.join(file_paths['external_path'], session, session + '_imec0',
                                           session + '_tcat.imec0.ap.xd_384_6_0.txt')):
            path = os.path.join(file_paths['external_path'], session)
            catgt(path, path)
