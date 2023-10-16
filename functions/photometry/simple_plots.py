from datetime import date
import os
from tkinter import *
import time
from os import walk
import pandas as pd
from csv import DictReader, reader
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from .user_info import get_user_info

info_dict = get_user_info()
initials = info_dict['initials']
start_date = info_dict['start_date']


def get_today_filepaths(days_back=0):
    file_paths = []
    for root, dirs, filenames in walk(os.path.join(os.getcwd(), 'data')):
        if len(dirs) == 0 and os.path.basename(root)[:2] == initials:
            mouse = os.path.basename(root)
            for f in filenames:
                if f == 'desktop.ini':
                    continue
                file_date = date(int(f[5:9]), int(f[10:12]), int(f[13:15]))
                dif = date.today() - file_date
                if dif.days <= days_back:
                    # if f[5:15] == time.strftime("%Y-%m-%d"):
                    file_paths.append(os.path.join(mouse, f))
    return file_paths


def min_dif(a, b, tolerance=0, return_index=False, rev=False):
    if type(a) == pd.core.series.Series:
        a = a.values
    if type(b) == pd.core.series.Series:
        b = b.values
    if rev:
        outer = -1 * np.subtract.outer(a, b)
        outer[outer <= tolerance] = np.nan
    else:
        outer = np.subtract.outer(b, a)
        outer[outer <= tolerance] = np.nan
    # noinspection PyBroadException
    mins = np.nanmin(outer, axis=0)
    if return_index:
        index = np.nanargmin(outer, axis=0)
        return index, mins
    return mins


def gen_data(file_paths):
    d = {}
    for f in file_paths:
        path = os.path.join(os.getcwd(), 'data', f)
        data = pd.read_csv(path, na_values=['None'], skiprows=3)
        mouse = os.path.dirname(f)
        data = data_reduction(data)
        if mouse in d.keys():
            d[mouse].append(data)
        else:
            d[mouse] = [data]
    return d


def remove(df, key, tolerance, port):
    on_times = df[(df.key == key) & (df.value == 1) & (df.port == port)].session_time.to_numpy()
    off_times = df[(df.key == key) & (df.value == 0) & (df.port == port)].session_time.to_numpy()
    forward = min_dif(on_times, off_times)
    forward_off = min_dif(on_times, off_times, rev=True)
    forward[np.isnan(forward)] = tolerance
    forward_off[np.isnan(forward_off)] = tolerance
    on_times = on_times[forward >= tolerance]
    off_times = off_times[forward_off >= tolerance]

    back = min_dif(off_times, on_times, rev=True)
    back_off = min_dif(off_times, on_times)
    back[np.isnan(back)] = tolerance
    back_off[np.isnan(back_off)] = tolerance
    on_times = on_times[back >= tolerance]
    off_times = off_times[back_off >= tolerance]

    df = df[((df.key != key) | (df.value != 1) | (df.port != port)) | (df.session_time.isin(on_times))]
    df = df[((df.key != key) | (df.value != 0) | (df.port != port)) | (df.session_time.isin(off_times))]
    return df


def data_reduction(df, lick_tol=.01, head_tol=.2):
    df = df[df.key != 'camera']
    df = df[df.phase != 'setup']
    df = remove(df, 'head', head_tol, port=1)
    df = remove(df, 'head', head_tol, port=2)
    df = remove(df, 'lick', lick_tol, port=1)
    df = remove(df, 'lick', lick_tol, port=2)
    return df


def consumption_time(df):
    bg_end_times = df[(df.key == 'LED') & (df.port == 2) & (df.value == 1)]
    exp_entries = df[(df.key == 'head') & (df.port == 1) & (df.value == 1)]
    dif = min_dif(bg_end_times.session_time, exp_entries.session_time)
    bg_consumption = dif[~np.isnan(dif)]
    if df.task.iloc[10] != 'single_reward':
        consumption_df = pd.DataFrame()
        consumption_df['consumption time'] = bg_consumption
        consumption_df['port'] = ['bg'] * len(bg_consumption)
        return consumption_df

    exp_end_times = df[(df.key == 'LED') & (df.port == 1) & (df.value == 1)]
    bg_entries = df[(df.key == 'head') & (df.port == 2) & (df.value == 1)]
    dif = min_dif(exp_end_times.session_time, bg_entries.session_time)
    exp_consumption = dif[~np.isnan(dif)]
    consumption_df = pd.DataFrame()
    consumption_df['consumption time'] = np.concatenate([bg_consumption, exp_consumption])
    consumption_df['port'] = ['bg'] * len(bg_consumption) + ['exp'] * len(exp_consumption)
    return consumption_df


def block_leave_times(df):
    reward_trials = df[(df.key == 'reward_initiate')].trial.to_numpy()
    non_reward = ~df.trial.isin(reward_trials)
    bg_end_times = df[(df.key == 'LED') & (df.port == 2) & (df.value == 1) & non_reward]
    exp_entries = df[(df.key == 'head') & (df.value == 1) & (df.port == 1) & non_reward]
    exp_exits = df[(df.key == 'head') & (df.value == 0) & (df.port == 1) & non_reward]
    bg_end_times = bg_end_times[bg_end_times.session_time < exp_entries.session_time.max()]
    ind, dif = min_dif(bg_end_times.session_time, exp_entries.session_time, return_index=True)
    exp_entries = exp_entries.iloc[np.unique(ind)]
    exp_entries = exp_entries.groupby('trial').session_time.max()
    exp_exits = exp_exits.groupby('trial').session_time.max()
    valid_trials = np.intersect1d(exp_exits.index.values, exp_entries.index.values)
    exp_exits = exp_exits.loc[valid_trials]
    exp_entries = exp_entries.loc[valid_trials]
    if len(exp_exits.to_numpy()) != len(exp_entries.to_numpy()):
        print()
    leave_times = exp_exits.to_numpy() - exp_entries.to_numpy()

    trial_blocks = bg_end_times[bg_end_times.trial.isin(exp_entries.index.values)].phase.to_numpy()
    block_leaves_df = pd.DataFrame()
    block_leaves_df['leave time'] = leave_times
    block_leaves_df['block'] = trial_blocks
    return block_leaves_df


def get_entry_exit(df, trial):
    is_trial = df.trial == trial
    start = df.value == 1
    end = df.value == 0
    port1 = df.port == 1
    port2 = df.port == 2

    trial_start = df[is_trial & start & (df.key == 'trial')].time_recording.values[0]
    trial_middle = df[is_trial & end & (df.key == 'LED') & port2].time_recording.values[0]
    trial_end = df[is_trial & end & (df.key == 'trial')].time_recording.values[0]

    bg_entries = df[is_trial & port2 & start & (df.key == 'head')].time_recording.to_numpy()
    bg_exits = df[is_trial & port2 & end & (df.key == 'head')].time_recording.to_numpy()

    if len(bg_entries) == 0 or bg_entries[0] > bg_exits[0]:
        bg_entries = np.concatenate([[trial_start], bg_entries])
    if trial_end - bg_entries[-1] < .1:
        bg_entries = bg_entries[:-1]
    if len(bg_exits) == 0 or bg_entries[-1] > bg_exits[-1]:
        bg_entries = np.concatenate([bg_exits, [trial_middle]])

    exp_entries = df[is_trial & port1 & start & (df.key == 'head') &
                     (df.time_recording > trial_middle)].time_recording.to_numpy()
    exp_exits = df[is_trial & port1 & end & (df.key == 'head') &
                   (df.time_recording > trial_middle)].time_recording.to_numpy()

    if not (len(exp_entries) == 0 and len(exp_exits) == 0):
        if len(exp_entries) == 0:
            exp_entries = np.concatenate([[trial_middle], exp_entries])
        if len(exp_exits) == 0:
            exp_exits = np.concatenate([exp_exits, [trial_end]])

        if exp_entries[0] > exp_exits[0]:
            exp_entries = np.concatenate([[trial_middle], exp_entries])
        if exp_entries[-1] > exp_exits[-1]:
            exp_exits = np.concatenate([exp_exits, [trial_end]])

    early_exp_entries = df[is_trial & port1 & start & (df.key == 'head') &
                           (df.time_recording < trial_middle)].time_recording.to_numpy()
    early_exp_exits = df[is_trial & port1 & end & (df.key == 'head') &
                         (df.time_recording < trial_middle)].time_recording.to_numpy()

    if not (len(early_exp_entries) == 0 and len(early_exp_exits) == 0):
        if len(early_exp_entries) == 0:
            early_exp_entries = np.concatenate([[trial_start], early_exp_entries])
        if len(early_exp_exits) == 0:
            early_exp_exits = np.concatenate([early_exp_exits, [trial_middle]])

        if early_exp_entries[0] > early_exp_exits[0]:
            early_exp_entries = np.concatenate([[trial_start], early_exp_entries])
        if early_exp_entries[-1] > early_exp_exits[-1]:
            early_exp_exits = np.concatenate([early_exp_exits, [trial_middle]])

    if len(bg_entries) != len(bg_exits):
        print()
    if len(exp_entries) != len(exp_exits):
        print()
    if len(early_exp_entries) != len(early_exp_exits):
        print()

    return bg_entries, bg_exits, exp_entries, exp_exits, early_exp_entries, early_exp_exits


def percent_engaged(df):
    travel_time = .5
    blocks = df.phase.unique()
    blocks.sort()
    time_engaged = []
    block_time = []
    block_rewards = []
    for block in blocks:
        engaged = []
        all_time = []
        rewards = []
        block_trials = df[(df.value == 0) & (df.key == 'trial') & (df.phase == block)].trial
        for trial in block_trials:
            bg_entries, bg_exits, exp_entries, exp_exits, _, _ = get_entry_exit(df, trial)
            is_trial = df.trial == trial
            start = df.value == 1
            end = df.value == 0
            # port1 = df.port == 1
            # port2 = df.port == 2
            #
            trial_start = df[is_trial & start & (df.key == 'trial')].session_time.values[0]
            # trial_middle = df[is_trial & start & (df.key == 'LED') & port2].session_time.values[0]
            trial_end = df[is_trial & end & (df.key == 'trial')].session_time.values[0]
            #
            # bg_entries = df[is_trial & port2 & start & (df.key == 'head')].session_time.to_numpy()
            # bg_exits = df[is_trial & port2 & end & (df.key == 'head')].session_time.to_numpy()
            #
            # if len(bg_entries) == 0 or bg_entries[0] > bg_exits[0]:
            #     bg_entries = np.concatenate([[trial_start], bg_entries])
            # if trial_end - bg_entries[-1] < .1:
            #     bg_entries = bg_entries[:-1]
            # if len(bg_exits) == 0 or bg_entries[-1] > bg_exits[-1]:
            #     bg_entries = np.concatenate([bg_exits, [trial_middle]])
            #
            # if not (len(bg_entries) == len(bg_exits) and np.all(bg_exits - bg_entries > 0)):
            #     print('stop')
            # bg_engaged = sum(bg_exits - bg_entries)
            #
            # exp_entries = df[is_trial & port1 & start & (df.key == 'head') &
            #                  (df.session_time > trial_middle)].session_time.to_numpy()
            # exp_exits = df[is_trial & port1 & end & (df.key == 'head') &
            #                (df.session_time > trial_middle)].session_time.to_numpy()
            #
            # if len(exp_entries) == 0 and len(exp_exits) == 0:
            #     exp_engaged = 0
            # else:
            #     if len(exp_entries) == 0:
            #         exp_entries = np.concatenate([[trial_middle], exp_entries])
            #     if len(exp_exits) == 0:
            #         exp_exits = np.concatenate([exp_exits, [trial_end]])
            #
            #     if exp_entries[0] > exp_exits[0]:
            #         exp_entries = np.concatenate([[trial_middle], exp_entries])
            #     if exp_entries[-1] > exp_exits[-1]:
            #         exp_exits = np.concatenate([exp_exits, [trial_end]])
            #     exp_engaged = sum(exp_exits - exp_entries)
            #
            #     # if not len(exp_entries) == len(exp_exits) and len(exp_entries):
            #     #     print('stop')
            #     # if len(exp_entries):

            if len(exp_entries):
                exp_engaged = sum(exp_exits - exp_entries)
            else:
                exp_engaged = 0
            bg_engaged = sum(bg_exits - bg_entries)

            all_time.append(trial_end - trial_start)
            engaged.append(bg_engaged + exp_engaged)
            rewards.append(len(df[is_trial & start & (df.key == 'reward')]))

        time_engaged.append(sum(engaged) + travel_time * 2 * len(block_trials))
        block_time.append(sum(all_time))
        block_rewards.append(sum(rewards))
    engaged_df = pd.DataFrame()
    engaged_df['percent engaged'] = np.array(time_engaged) / np.array(block_time)
    engaged_df['block'] = blocks
    engaged_df['time engaged'] = time_engaged
    engaged_df['rewards earned'] = block_rewards
    engaged_df['reward rate'] = np.array(block_rewards) / np.array(time_engaged)
    return engaged_df


def add_h_lines(data=None, x=None, y=None, hue=None, ax=None, palette=None):
    palette = sns.color_palette(palette)
    for i, hue_key in enumerate(data[hue].unique()):
        df = data[data[hue] == hue_key]
        if df[x].max() > 3:
            hue_mean = df[(df[x] > df[x].max() - 3)][y].mean()
            ax.hlines(hue_mean, 0, df[x].max(), palette[i], alpha=.5)


def simple_plots():
    dif = date.today() - start_date
    data = gen_data(get_today_filepaths(days_back=dif.days))
    for mouse in data.keys():
        engaged = pd.DataFrame()
        consumption = pd.DataFrame()
        block_leaves = pd.DataFrame()
        for i, session in enumerate(data[mouse]):
            engaged_df = percent_engaged(session)
            engaged_df['day'] = [i] * len(engaged_df)
            engaged = pd.concat([engaged, engaged_df])

            consumption_df = consumption_time(session)
            consumption_df['day'] = [i] * len(consumption_df)
            consumption = pd.concat([consumption, consumption_df])

            block_leaves_df = block_leave_times(session)
            block_leaves_df['day'] = [i] * len(block_leaves_df)
            block_leaves = pd.concat([block_leaves, block_leaves_df])
        engaged.sort_values('block', inplace=True)
        block_leaves.sort_values('block', inplace=True)
        fig, axes = plt.subplots(2, 2, figsize=[11, 8], layout="constrained")
        sns.lineplot(data=block_leaves.reset_index(), x='day', y='leave time', hue='block', ax=axes[0, 0],
                     palette='Set2')
        add_h_lines(data=block_leaves.reset_index(), x='day', y='leave time', hue='block', ax=axes[0, 0],
                    palette='Set2')
        sns.lineplot(data=consumption.reset_index(), x='day', y='consumption time', hue='port', ax=axes[0, 1],
                     palette='Set1')
        add_h_lines(data=consumption.reset_index(), x='day', y='consumption time', hue='port', ax=axes[0, 1],
                    palette='Set1')
        sns.lineplot(data=engaged.reset_index(), x='day', y='reward rate', hue='block', ax=axes[1, 0],
                     palette='Set2')
        add_h_lines(data=engaged.reset_index(), x='day', y='reward rate', hue='block', ax=axes[1, 0],
                    palette='Set2')
        sns.lineplot(data=engaged.reset_index(), x='day', y='percent engaged', hue='block', ax=axes[1, 1],
                     palette='Set2')
        add_h_lines(data=engaged.reset_index(), x='day', y='percent engaged', hue='block', ax=axes[1, 1],
                    palette='Set2')

        axes[0, 0].set_title('Leave Time by Block')
        axes[0, 1].set_title('Consumption Time by Port')
        axes[1, 0].set_title('Reward Rate by Block')
        axes[1, 1].set_title('Percent Time Engaged by Block')

        # axes[0, 0].set_ylim([0, axes[0, 0].get_ylim()[1]])
        # axes[0, 1].set_ylim([0, axes[0, 1].get_ylim()[1]])
        # axes[1, 0].set_ylim([0, axes[1, 0].get_ylim()[1]])
        # axes[1, 1].set_ylim([0, 1])
        axes[0, 0].set_ylim([0, 20])
        axes[0, 1].set_ylim([0, 20])
        axes[1, 0].set_ylim([0, .65])
        axes[1, 1].set_ylim([0, 1])
        plt.suptitle(mouse, fontsize=20)
        plt.show()


def single_session():
    data = gen_data(get_today_filepaths(days_back=5))
    for mouse in data.keys():
        last_session = data[mouse][-1]
        session_summary(last_session, mouse)


def session_summary(data, mouse):
    fig, [ax1, ax2] = plt.subplots(1, 2, figsize=[10, 10])
    port_palette = sns.color_palette('Set1')
    block_palette = sns.color_palette('Set2')
    start = data.value == 1
    end = data.value == 0
    head = data.key == 'head'
    lick = data.key == 'lick'
    reward = data.key == 'reward'
    port1 = data.port == 1
    port2 = data.port == 2
    max_trial = data.trial.max()

    bg_rectangles = []
    exp_rectangles_in_bg = []
    exp_rectangles = []
    block1_rectangles = []
    block2_rectangles = []
    bg_reward_events = []
    exp_reward_events = []
    bg_lick_events = []
    exp_lick_events = []
    bg_lengths = []
    exp_lengths = []
    trial_blocks = data.groupby(['trial'])['phase'].agg(pd.Series.mode)
    blocks = data.phase.unique()
    blocks.sort()
    for trial in data.trial.unique():
        if np.isnan(trial):
            continue
        is_trial = data.trial == trial
        try:
            trial_start = data[is_trial & start & (data.key == 'trial')].session_time.values[0]
            trial_middle = data[is_trial & end & (data.key == 'LED') & port2].session_time.values[0]
            trial_end = data[is_trial & end & (data.key == 'trial')].session_time.values[0]
        except IndexError:
            continue

        bg_rewards = data[is_trial & start & port2 & reward].session_time.values
        exp_rewards = data[is_trial & start & port1 & reward].session_time.values
        bg_licks = data[is_trial & start & lick & (data.session_time < trial_middle)].session_time.values
        exp_licks = data[is_trial & start & lick & (data.session_time > trial_middle)].session_time.values

        bg_lengths.append(trial_middle - trial_start)
        exp_lengths.append(trial_end - trial_middle)

        bg_entries, bg_exits, exp_entries, exp_exits, early_exp_entries, early_exp_exits = get_entry_exit(data, trial)
        bg_intervals = list(zip(bg_entries, bg_exits))
        exp_intervals = list(zip(exp_entries, exp_exits))
        early_exp_intervals = list(zip(early_exp_entries, early_exp_exits))
        for [s, e] in bg_intervals:
            bg_rectangles.append(Rectangle((s - trial_start, trial), e - s, .7))
        for [s, e] in early_exp_intervals:
            exp_rectangles_in_bg.append(Rectangle((s - trial_start, trial), e - s, .7))
        for [s, e] in exp_intervals:
            exp_rectangles.append(Rectangle((s - trial_middle, trial), e - s, .7))
        if np.where(blocks == trial_blocks.loc[trial])[0][0] == 0:
            block1_rectangles.append(Rectangle((0, trial), 100, 1))
        else:
            block2_rectangles.append(Rectangle((0, trial), 100, 1))
        bg_reward_events.append(bg_rewards - trial_start)
        exp_reward_events.append(exp_rewards - trial_middle)
        bg_lick_events.append(bg_licks - trial_start)
        exp_lick_events.append(exp_licks - trial_middle)

    alpha = .5
    pc_b1 = PatchCollection(block1_rectangles, facecolors=block_palette[0], alpha=alpha)
    pc_b2 = PatchCollection(block2_rectangles, facecolors=block_palette[1], alpha=alpha)
    ax1.add_collection(pc_b1)
    ax1.add_collection(pc_b2)
    pc_b12 = PatchCollection(block1_rectangles, facecolors=block_palette[0], alpha=alpha)
    pc_b22 = PatchCollection(block2_rectangles, facecolors=block_palette[1], alpha=alpha)
    ax2.add_collection(pc_b12)
    ax2.add_collection(pc_b22)

    pc_bg = PatchCollection(bg_rectangles, edgecolor=port_palette[0], facecolor='w', alpha=1)
    ax1.add_collection(pc_bg)

    pc_exp_bg = PatchCollection(exp_rectangles_in_bg, edgecolor=port_palette[1], facecolor='w', alpha=1)
    ax1.add_collection(pc_exp_bg)

    pc_exp = PatchCollection(exp_rectangles, edgecolor=port_palette[1], facecolor='w', alpha=1)
    ax2.add_collection(pc_exp)

    offsets = np.array(list(range(len(bg_reward_events)))) + 1.4
    ax1.eventplot(bg_reward_events, color='purple', linelengths=.62, lineoffsets=offsets)
    offsets = np.array(list(range(len(exp_reward_events)))) + 1.4
    ax2.eventplot(exp_reward_events, color='purple', linelengths=.62, lineoffsets=offsets)

    light = [.8, .7, .8]
    dark = [.2, .2, .2]
    offsets = np.array(list(range(len(bg_lick_events)))) + 1.4
    ax1.eventplot(bg_lick_events, color=light, linelengths=.25, lineoffsets=offsets)
    offsets = np.array(list(range(len(exp_lick_events)))) + 1.4
    ax2.eventplot(exp_lick_events, color=light, linelengths=.25, lineoffsets=offsets)

    session_summary_axis_settings([ax1, ax2], max_trial)
    plt.suptitle(mouse)
    plt.show()


def session_summary_axis_settings(axes, max_trial):
    for ax in axes:
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.get_yaxis().set_visible(False)
        ax.set_ylim([-1, max_trial + 1])
        ax.set_xlim([0, 20])
        ax.invert_yaxis()
        ax.set_ylabel('Trial')
        ax.set_xlabel('Time (sec)')


if __name__ == '__main__':
    simple_plots()
    single_session()
