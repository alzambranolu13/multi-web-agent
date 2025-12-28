"""
Script to analyze experiment results and categorize tasks by difficulty.

This script processes experiment results and categorizes tasks into hard, medium,
and easy based on achievement rates across multiple experiment runs.
"""
import os
import logging
from pathlib import Path
from agentlab.analyze import inspect_results
from agentlab.experiments.study import get_most_recent_study
import pandas as pd
import glob
import utils 
import matplotlib.pyplot as plt
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESULTS_DIR = os.environ.get("AGENTLAB_EXP_ROOT", None)
RESULTS_DIR = Path(RESULTS_DIR)
logger.info(f"Results directory: {RESULTS_DIR}")

def get_experiments_dfs(RESULTS_DIR):
    """
    Load experiment results from all studies in the results directory.
    
    Args:
        RESULTS_DIR: Path to the results directory
        
    Returns:
        List of dataframes containing experiment results
    """
    experiments = glob.glob(str(RESULTS_DIR) + "/*")
    logger.info(f"Found experiments: {len(experiments)}")
    dfs = []
    for a in experiments:
        study_name = a.split("/")[-1]
        if study_name.endswith(".zip") or study_name.endswith("archive"):
            logger.debug(f"Skipping archive: {study_name}")
            continue
        logger.info(f"Processing study: {study_name}")
        result_dir = get_most_recent_study(RESULTS_DIR, contains=study_name)
        result_df = inspect_results.load_result_df(result_dir)
        if result_df is None:
            logger.warning(f"No result found for study: {study_name}")
            continue
        dfs.append(result_df)
    return dfs


def prepare_df(df, i):
    """
    Prepare a dataframe for merging by extracting task names and cumulative rewards.
    
    Args:
        df: Input dataframe with experiment results
        i: Index of the experiment (for column naming)
        
    Returns:
        Processed dataframe with task_name as index and cumulative reward as column
    """
    df = df.reset_index()  # Brings env.task_name into columns
    df = df.drop_duplicates(subset='env.task_name')
    
    # Keep both env.task_name and cum_reward, then set the index
    df = df[['env.task_name', 'cum_reward']]
    df = df.set_index("env.task_name")
    
    # Rename cum_reward column
    df = df.rename(columns={"cum_reward": f"cum_reward_{i+1}"})
    return df


if __name__ == "__main__":
    dfs = get_experiments_dfs(RESULTS_DIR)
    # Process each dataframe
    prepared = [prepare_df(df, i) for i, df in enumerate(dfs)]

    # Merge all dataframes on the index
    reward_df = pd.concat(prepared, axis=1)
    num_experiments = len(reward_df.columns)
    reward_df["achieve_rate"] = (reward_df.sum(axis=1)) / num_experiments

    hard = reward_df[reward_df['achieve_rate'] == 0]
    medium = reward_df[reward_df['achieve_rate'].between(0, 1, inclusive='neither')]
    easy = reward_df[reward_df['achieve_rate'] == 1]

    len_hard = len(hard)
    len_medium = len(medium)
    len_easy = len(easy)

    logger.info(f"Number of Hard tasks: {len_hard}")
    logger.info(f"Number of Medium tasks: {len_medium}")
    logger.info(f"Number of Easy tasks: {len_easy}")

    # Save task IDs to JSON files
    hard_ids = [task.split('.')[1] for task in hard.index]
    with open("data/hard_tasks.json", "w") as f:
        json.dump(hard_ids, f)
    medium_ids = [task.split('.')[1] for task in medium.index]
    with open("data/medium_tasks.json", "w") as f:
        json.dump(medium_ids, f)
    easy_ids = [task.split('.')[1] for task in easy.index]
    with open("data/easy_tasks.json", "w") as f:
        json.dump(easy_ids, f)
    
    logger.info("Task categorization complete. Results saved to data/ directory.")





