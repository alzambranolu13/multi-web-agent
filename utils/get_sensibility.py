"""
Script to analyze experiment results across multiple runs to identify consistently hard tasks.

This script processes experiment results from multiple runs and identifies tasks that
are consistently hard across different experiment runs.
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

experiments = {}


def prepare_df(df, i):
    """
    Prepare a dataframe for merging by extracting task names and cumulative rewards.
    
    Args:
        df: Input dataframe with experiment results
        i: Index of the experiment (for column naming)
        
    Returns:
        Processed dataframe with task_name as index and cumulative reward as column
    """
    model_name = df.axes[0][0][1]
    if model_name not in experiments:
        experiments[model_name] = 0
    else:
        experiments[model_name] += 1
    df = df.reset_index()  # Brings env.task_name into columns
    df = df.drop_duplicates(subset='env.task_name')
    
    # Keep both env.task_name and cum_reward, then set the index
    df = df[['env.task_name', 'cum_reward']]
    df = df.set_index("env.task_name")
    
    # Rename cum_reward column
    df = df.rename(columns={"cum_reward": f"{model_name}_reward_{experiments[model_name]}"})
    return df


if __name__ == "__main__":
    dfs = get_experiments_dfs(RESULTS_DIR)
    # Process each dataframe
    prepared = [prepare_df(df, i) for i, df in enumerate(dfs)]

    # Merge all dataframes on the index
    reward_df = pd.concat(prepared, axis=1)

    # Analyze hard tasks across multiple experiment runs
    string = '0'
    sets = []
    for i in range(5):
        focal_df = reward_df.loc[:, reward_df.columns.str.endswith(tuple(string))]
        num_experiments = len(focal_df.columns)
        focal_df["achieve_rate"] = (focal_df.sum(axis=1)) / num_experiments

        hard = focal_df[focal_df['achieve_rate'] == 0].index
        sets.append(hard)
        string += str(i + 1)

    first = sets[0]
    second = sets[1]
    third = sets[2]
    fourth = sets[3]
    fifth = sets[4]

    logger.info(f'Hard set in first experiment: {len(first)}')
    inter1 = first.intersection(second)
    logger.info(f"Hard tasks after 2 runs: {len(inter1)}")
    inter2 = inter1.intersection(third)
    logger.info(f"Hard tasks after 3 runs: {len(inter2)}")
    inter3 = inter2.intersection(fourth)
    logger.info(f"Hard tasks after 4 runs: {len(inter3)}")
    final_intersection = inter3.intersection(fifth)
    logger.info(f"Hard tasks after 5 runs: {len(final_intersection)}")

    logger.info(f"Overlap between first and final: {len(first.intersection(final_intersection))}")










