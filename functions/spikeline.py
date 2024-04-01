# spikeline.py

import os
import psutil
import numpy as np
from time import sleep
from shutil import rmtree
from functions.reset_folder import reset_folder
from sklearn.preprocessing import normalize
from functions.generate_file_lists import generate_file_lists
from file_paths import root_file_paths

import spikeinterface.full as si
import spikeinterface.sorters as ss
import spikeinterface.extractors as se
import spikeinterface.comparison as sc
from spikeinterface.exporters import export_to_phy
from spikeinterface.curation import remove_excess_spikes

# Change these paths to your own
ks3_path = os.path.join('C:\\', 'github', 'Kilosort')
ks2_5_path = os.path.join('C:\\', 'github', 'Kilosort2_5')

os.environ['KILOSORT3_PATH'] = ks3_path
os.environ['KILOSORT2_5_PATH'] = ks2_5_path

probe_code = 'imec1'

def remove_empty_or_one(sorter):
    units_to_keep = []
    for segment_index in range(sorter.get_num_segments()):
        for unit in sorter.get_unit_ids():
            spikes = sorter.get_unit_spike_train(unit, segment_index=segment_index)
            if spikes.size > 1:
                units_to_keep.append(unit)
    units_to_keep = np.unique(units_to_keep)
    return sorter.select_units(units_to_keep)


def spikeline(data_path, phy_folder, working_folder=os.path.join('Y:\\', 'phy_temp'), supercat_path=None):
    n_jobs = 12

    if not os.path.isdir(working_folder):
        os.mkdir(working_folder)

    file_paths = root_file_paths()
    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')

    folder_name = data_path.split(os.sep)[-1]
    phy_folder = os.path.join(phy_folder, folder_name)
    if supercat_path:
        recording_path = os.path.join(data_path, supercat_path)
    else:
        recording_name = folder_name + '_' + probe_code
        recording_path = os.path.join(data_path, 'catgt_' + folder_name, recording_name)
    # recording_path = os.path.join(data_path, recording_name)
    print(f'specified recording save path: {recording_path}')

    # recording = si.load_extractor(os.path.join(working_folder, 'recording_save0'))

    recording = se.read_spikeglx(recording_path, stream_id=probe_code+'.ap')
    print(f'read spikeGLX')

    recording_cmr = recording
    recording_f = si.bandpass_filter(recording, freq_min=300, freq_max=6000)
    recording_cmr = recording_f
    # recording_cmr = si.common_reference(recording_f, reference='local', operator='median',
    #                                     local_radius=(30, 200))
    # recording_cmr = si.common_reference(recording_f, reference='global', operator='median')
    kwargs = {'n_jobs': n_jobs, 'total_memory': '8G'}
    print('attempting to apply filters')
    applied = False
    attempt = 1
    while not applied:
        try:
            sleep(5)
            recording_save = reset_folder(os.path.join(working_folder, 'recording_save'), local=False)
            print(f'attempt {attempt}')
            recording = recording_cmr.save(format='binary', folder=recording_save, **kwargs)
            applied = True
            print(f'succeeded on attempt {attempt}')
        except Exception as e:
            attempt += 1
            if attempt > 4:
                print(f'failed to apply filters after {attempt} attempts')
                raise e
            else:
                print(e)

    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')

    sorter_params = {"keep_good_only": True}
    ss.Kilosort3Sorter.set_kilosort3_path(ks3_path)
    print(f'starting kilosort3...')

    kilosort3_folder = reset_folder(os.path.join(working_folder, 'kilosort3'), local=False)
    ks3_sorter = ss.run_sorter(sorter_name='kilosort3', recording=recording, output_folder=kilosort3_folder,
                               verbose=False, **sorter_params)
    ks3_sorter = remove_empty_or_one(ks3_sorter)
    # kilosort3_folder = os.path.join(working_folder, 'kilosort30')
    # ks3_sorter = si.read_sorter_folder(kilosort3_folder)
    print(f'finished kilosort3...')
    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')
    sorter_params = {"keep_good_only": False}
    ss.Kilosort2_5Sorter.set_kilosort2_5_path(ks2_5_path)
    print(f'starting kilosort2_5...')
    kilosort2_5_folder = reset_folder(os.path.join(working_folder, 'kilosort2_5'), local=False)
    ks2_5_sorter = ss.run_sorter(sorter_name='kilosort2_5', recording=recording,
                                 output_folder=kilosort2_5_folder,
                                 verbose=False, **sorter_params)
    ks2_5_sorter = remove_empty_or_one(ks2_5_sorter)
    # kilosort2_5_folder = os.path.join(working_folder, 'kilosort2_50')
    # ks2_5_sorter = si.read_sorter_folder(kilosort2_5_folder)
    print(f'finished kilosort2_5...')

    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')

    print(f'starting consensus...')
    consensus = sc.compare_multiple_sorters(sorting_list=[ks3_sorter, ks2_5_sorter],
                                            name_list=['kilosort3', 'kilosort2_5'], verbose=False,
                                            delta_time=.2,
                                            match_score=.3,
                                            spiketrain_mode='union')
    agreement = consensus.get_agreement_sorting(minimum_agreement_count=2)
    kilosort3_templates = np.load(os.path.join(kilosort3_folder, 'sorter_output', 'templates.npy'))
    kilosort2_5_templates = np.load(os.path.join(kilosort2_5_folder, 'sorter_output', 'templates.npy'))

    template_similarty = np.array([np.sum(
        (normalize(np.max(abs(kilosort3_templates[int(unit['kilosort3']), :, :]), axis=0, keepdims=True)) -
         normalize(np.max(abs(kilosort2_5_templates[int(unit['kilosort2_5']), :, :]), axis=0,
                          keepdims=True))) ** 2) for unit in agreement._properties['unit_ids']]) / 2
    print(
        f'template filtering would remove {len(np.where(template_similarty >= .9)[0])} from {len(agreement.unit_ids)}')
    agreement = agreement.select_units(agreement.unit_ids[np.where(template_similarty < .9)[0]])
    agreement = remove_excess_spikes(agreement, recording)
    consensus_folder = reset_folder(os.path.join(working_folder, 'consensus'), local=False)
    agreement = agreement.save(folder=consensus_folder)

    waveforms_folder = reset_folder(os.path.join(working_folder, 'waveforms'), local=False)
    waveforms = si.WaveformExtractor.create(recording, agreement, waveforms_folder)
    waveforms.set_params(ms_before=3., ms_after=4., max_spikes_per_unit=500)
    waveforms.run_extract_waveforms(n_jobs=n_jobs, chunk_size=30000)
    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')

    sparsity_dict = dict(method="radius", radius_um=50, peak_sign='both')
    print(f'got waveforms')
    print(f'starting phy export')
    job_kwargs = {'n_jobs': n_jobs, 'total_memory': '8G'}
    export_to_phy(waveforms, phy_folder, compute_pc_features=False, compute_amplitudes=False, copy_binary=True,
                  remove_if_exists=True, **job_kwargs)
    # export_to_phy(waveforms, phy_folder, compute_pc_features=False, compute_amplitudes=False, copy_binary=True,
    #               remove_if_exists=True, sparsity_dict=sparsity_dict, max_channels_per_template=None,
    #               **job_kwargs)


    print(f'finished phy export')

    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')

    print(f'removing intermediate data folders')

    rmtree(working_folder, ignore_errors=True)

    hdd = psutil.disk_usage(file_paths['phy_ready_path'])
    print(f'remaining disk: {hdd.free / (2 ** 30)} GiB')


if __name__ == '__main__':
    file_paths = root_file_paths()
    session_list, file_list = generate_file_lists(file_paths=file_paths)
    file_path = os.path.join(file_paths['external_path'], 'catgt_merge_ES029_bot72_')
    super_cat = os.path.join('supercat_ES029_2022-08-31_bot72_0_g0', 'ES029_2022-08-31_bot72_0_g0_imec0')
    spikeline(file_path, os.path.join('E:\\', 'phy_ready'), working_folder=os.path.join('E:\\', 'phy_temp'),
              supercat_path=super_cat)
