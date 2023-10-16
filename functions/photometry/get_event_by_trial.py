import pandas as pd


def get_reward_by_trial(trials_df):

    # region Initialize a dataframe that can store timestamps of entry, exit, and rewards
    max_num_reward = trials_df.num_exp_rewards.max()
    reward_df = pd.DataFrame(index=trials_df.index, columns=list(range(1, max_num_reward + 1)))
    reward_df = reward_df.add_prefix("reward_")
    head_df = pd.DataFrame(index=trials_df.index, columns=['entry', 'exit'])
    trial_event = pd.concat([head_df, reward_df], axis=1)
    # endregion

    # region Assign event timestamps to the corresponding columns/cells
    trial_event['entry'] = trials_df['entry']
    trial_event['exit'] = trials_df['exit']
    for trial in range(len(trial_event)):
        for r in range(2, max_num_reward + 2):
            try:
                trial_event.iloc[trial, r] = trials_df.rewards[trial][r-2]
            except:
                pass
    # endregion
    trial_event = trial_event.div(1000)
    return trial_event
