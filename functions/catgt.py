# catgt.py
import os
from functions.generate_file_lists import generate_file_lists
from functions.check_probe_codes import check_probe_codes
import shutil
import numpy as np
from file_paths import root_file_paths


def run_catgt():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    for session in session_list['external_path']:
        probe_codes = check_probe_codes(os.path.join(file_paths['external_path'], session))
        for probe_code in probe_codes:
            sync_file_flex = os.path.join(file_paths['external_path'], session, 'catgt_' + session,
                                          session + '_' + probe_code,
                                          session + '_tcat.' + probe_code + '.ap.xd_384_6_0.txt')
            sync_file_500 = os.path.join(file_paths['external_path'], session, 'catgt_' + session,
                                         session + '_' + probe_code,
                                         session + '_tcat.' + probe_code + '.ap.xd_384_6_500.txt')
            if not (os.path.isfile(sync_file_flex) or os.path.isfile(sync_file_500)):
                path = os.path.join(file_paths['external_path'], session)
                catgt(path, path, probe_code=probe_code)


def catgt(input_path, output_path, probe_code='imec0'):
    tools_path = os.path.join('C:\\', 'spikeGLX', 'Tools2')

    path_parts = input_path.split(os.sep)
    run_name = path_parts[-1]
    directory = os.path.join(*path_parts[:-1])
    event_extractors = ''
    event_extractors += f'-xd=0,0,-1,{13},0 '  # extractors: stream type,stream index,word,bit,millisec

    print(f'Running CatGT for {run_name}...')
    command = f'runit.bat -dir={directory} -run={run_name[0:-3]} -g={run_name[-1]},{run_name[-1]} ' \
              f'-t=0,0 -prb=' + probe_code[-1] + ' -ap -xd=2,0,-1,6,0 ' \
                                                 f'-dest={output_path} -prb_fld -out_prb_fld -gblcar'
    # command = f'runit.bat -dir={directory} -run={run_name[0:-3]} -g={run_name[-1]},{run_name[-1]} -t=0,0 -prb=0 -ap -xd=2,0,-1,6,0' \
    #           f'-dest={output_path} -prb_fld -out_prb_fld -no_auto_sync -no_tshift'
    # command = f'runit.bat -dir={directory} -run={run_name[0:-3]} -g={run_name[-1]},{run_name[-1]} -t=0,0 -ap ' \
    #           f'-prb=0 -ni {event_extractors} -dest={output_path} -prb_fld -out_prb_fld -pass1_force_ni_ob_bin'
    # command = f'runit.bat -dir={input_path} -run={run_name[0:-3]} -prb_fld -g={run_name[-1]},{run_name[-1]} -t=0,0 -ap ' \
    #           f'-prb=0 -ni {event_extractors} -dest={output_path} -out_prb_fld -pass1_force_ni_ob_bin'
    print(command)
    result = os.system(f"cd {os.path.join(tools_path, 'CatGT-win')} & {command}")
    if result == 0:
        print(f'{run_name} done')
        if input_path != output_path:
            dest_ni = os.path.join(output_path, 'catgt_' + run_name)
            if not os.path.exists(dest_ni):
                os.mkdir(dest_ni)
            dest_imec = os.path.join(dest_ni, run_name + '_' + probe_code)
            if not os.path.exists(dest_imec):
                os.mkdir(dest_imec)
            shutil.move(os.path.join(input_path, run_name + '_ct_offsets.txt'), dest_ni)
            shutil.move(os.path.join(input_path, run_name + '_fyi.txt'), dest_ni)
            shutil.move(
                os.path.join(input_path, run_name + '_' + probe_code, run_name + '_tcat.' + probe_code + '.ap.bin'),
                dest_imec)
            shutil.move(
                os.path.join(input_path, run_name + '_' + probe_code, run_name + '_tcat.' + probe_code + '.ap.meta'),
                dest_imec)
            shutil.move(os.path.join(input_path, run_name + '_' + probe_code,
                                     run_name + '_tcat.' + probe_code + '.ap.xd_384_6_0.txt'),
                        dest_imec)
            shutil.move(os.path.join(input_path, run_name + '_' + probe_code,
                                     run_name + '_tcat.' + probe_code + '.ap.xd_384_6_500.txt'),
                        dest_imec)
    else:
        print(f'{run_name} catgt failed with exit code {result}. Check catgt.log in {tools_path}')


def combined_catgt(path_list, output_path):
    tools_path = os.path.join('C:\\', 'spikeGLX', 'Tools')
    supercat_strings = []
    for filepath in path_list:
        supercat_strings.append('{' + ','.join([os.path.dirname(filepath), os.path.basename(filepath)]) + '}')
    supercat_string = f'-supercat=' + ''.join(supercat_strings)

    if not os.path.exists(output_path):
        os.mkdir(output_path)
    print(f'Running CatGT for {os.path.basename(output_path)}...')
    command = f'runit.bat -prb=0 -ap -dest={output_path} -prb_fld -out_prb_fld {supercat_string}'
    print(command)
    result = os.system(f"cd {os.path.join(tools_path, 'CatGT-win')} & {command}")
    print(result)


def sort_files():
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    mouse_ids = []
    for session in session_list['external_path']:
        mouse_ids.append(session[:5])
    for mouse in np.unique(mouse_ids):
        mouse_session_ids = np.where(mouse == np.array(mouse_ids))[0]
        mouse_sessions = []
        for i in mouse_session_ids:
            mouse_sessions.append(session_list['external_path'][i])
        bot_rows = []
        for mouse_session in mouse_sessions:
            bot_rows.append(mouse_session[20:23])
        for bot_row in np.unique(bot_rows):
            merge_path = os.path.join(file_paths['external_path'], f'catgt_merge_{mouse}_bot{bot_row}')
            if not os.exists(merge_path):
                bot_row_ids = np.where(bot_row == np.array(bot_rows))[0]
                same_row_list = np.array(mouse_sessions)[bot_row_ids]
                paths = [os.path.join(file_paths['external_path'], sess, 'catgt_' + sess) for sess in same_row_list]
                all_files = True
                for path in paths:
                    if not os.path.exists(path):
                        print(f'{path} missing')
                        all_files = False
                if all_files:
                    print(f'combining {mouse} bot{bot_row} files')
                    combined_catgt(paths,
                                   os.path.join(file_paths['external_path'], f'catgt_merge_{mouse}_bot{bot_row}'))


if __name__ == '__main__':
    run_catgt()
    # sort_files()
