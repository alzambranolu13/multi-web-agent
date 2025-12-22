import os
from pathlib import Path
from agentlab.analyze import inspect_results
from agentlab.experiments.study import get_most_recent_study
import pandas as pd
import glob
import utils
import matplotlib.pyplot as plt
import json

RESULTS_DIR = os.environ.get("AGENTLAB_EXP_ROOT", None)
RESULTS_DIR=Path(RESULTS_DIR)
print(RESULTS_DIR)

def get_experiments_dfs(RESULTS_DIR):
    experiments = glob.glob(str(RESULTS_DIR)+"/*")
    print("Found experiments:",(experiments))
    dfs= []
    for a in experiments:
        print("Experiment:", a)
        study_name = a.split("/")[-1]
        if study_name.endswith(".zip") or study_name.endswith("archive"):
            print("Skipping archive:", study_name)
            continue
        print("Study Name:",study_name)
        result_dir= get_most_recent_study(RESULTS_DIR, contains=study_name)
        result_df = inspect_results.load_result_df(result_dir)
        if result_df is None:
            print("No result found for study:", study_name)
            continue
        dfs.append(result_df)
    return dfs

experiments = {}
def prepare_df(df, i):
    model_name = df.axes[0][0][1]
    if model_name not in experiments:
        experiments[model_name] = 0
    else:
        experiments[model_name] += 1
    df = df.reset_index()  # brings env.task_name into columns
    df = df.drop_duplicates(subset='env.task_name')
    
    # Keep both env.task_name and cum_reward, then set the index
    df = df[['env.task_name', 'cum_reward']]
    df = df.set_index("env.task_name")
    
    # Rename cum_reward column
    df = df.rename(columns={"cum_reward": f"{model_name}_reward_{experiments[model_name]}"})
    return df


dfs= get_experiments_dfs(RESULTS_DIR)
# Process each dataframe
prepared = [prepare_df(df,i) for i,df in enumerate(dfs)]

# Merge all dataframes on the index
reward_df = pd.concat(prepared, axis=1)

string = '0'
sets= []
for i in range(5):
    focal_df = reward_df.loc[:,reward_df.columns.str.endswith(tuple(string))]
    num_experiments= len(focal_df.columns)
    focal_df["achieve_rate"] = (focal_df.sum(axis=1))/num_experiments

    hard=focal_df[focal_df['achieve_rate'] ==0].index
    #medium=reward_df[reward_df['achieve_rate'].between(0,1,inclusive='neither')].index
    #easy = reward_df[reward_df['achieve_rate'] == 1].index
    sets.append(hard)
    string += str(i+1)


first= sets[0]
second= sets[1]
third= sets[2]
fourth= sets[3]
fifth= sets[4]

print('Hard set in first experiment:', len(first))
inter1 = first.intersection(second)
print("Hard tasks after 2 runs:", len(inter1))
inter2 = inter1.intersection(third)
print("Hard tasks after 3 runs:", len(inter2))
inter3 = inter2.intersection(fourth)
print("Hard tasks after 4 runs:", len(inter3))
final_intersection = inter3.intersection(fifth)
print("Hard tasks after 5 runs:", len(final_intersection))

print("Overlap 1", len(first.intersection(final_intersection)))










