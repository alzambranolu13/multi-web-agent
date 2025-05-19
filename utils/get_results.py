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


def prepare_df(df, i):
    df = df.reset_index()  # brings env.task_name into columns
    df = df.drop_duplicates(subset='env.task_name')
    
    # Keep both env.task_name and cum_reward, then set the index
    df = df[['env.task_name', 'cum_reward']]
    df = df.set_index("env.task_name")
    
    # Rename cum_reward column
    df = df.rename(columns={"cum_reward": f"cum_reward_{i+1}"})
    return df



# Process each dataframe
prepared = [prepare_df(df,i) for i,df in enumerate(dfs)]

# Merge all dataframes on the index
reward_df = pd.concat(prepared, axis=1)
num_experiments= len(reward_df.columns)
reward_df["achieve_rate"] = (reward_df.sum(axis=1))/num_experiments

hard=reward_df[reward_df['achieve_rate'] ==0]
medium=reward_df[reward_df['achieve_rate'].between(0,1,inclusive='neither')]
easy = reward_df[reward_df['achieve_rate'] == 1]



len_hard = len(hard)
len_medium = len(medium)
len_easy = len(easy)

print("Number of Hard tasks:", len_hard)
print("Number of Medium tasks:", len_medium)
print("Number of Easy tasks:", len_easy)

# plt.figure(figsize=(10, 5))
# plt.bar(['Hard', 'Medium', 'Easy'], [len_hard, len_medium, len_easy], color=['red', 'orange', 'green'])
# plt.savefig('hardset_results.png', bbox_inches='tight')


hard_ids= [ task.split('.')[1] for task in hard.index]
with open("data/hard_tasks.json", "w") as f:
    json.dump(hard_ids, f)
medium_ids= [ task.split('.')[1] for task in medium.index]
with open("data/medium_tasks.json", "w") as f:
    json.dump(medium_ids, f)
easy_ids= [ task.split('.')[1] for task in easy.index]
with open("data/easy_tasks.json", "w") as f:
    json.dump(easy_ids, f)





