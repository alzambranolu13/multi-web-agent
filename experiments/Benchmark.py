import numpy as np
import json
import os

from browsergym.experiments.benchmark.metadata.utils import (
    task_metadata,task_list_from_metadata
)
from browsergym.experiments.benchmark.utils import (
    make_env_args_list_from_repeat_tasks,make_env_args_list_from_fixed_seeds
)

from browsergym.experiments.benchmark.base import Benchmark, HighLevelActionSetArgs
from browsergym.experiments.benchmark.configs import DEFAULT_HIGHLEVEL_ACTION_SET_ARGS


from typing import List



def get_task_ids_sampled_wa(package='data', task_file='webarena.task_ids.mini.json') -> List[int]:
    task_ids_path = os.path.join(package,task_file)
    
    with open(task_ids_path) as f:
        task_ids = json.load(f)
    
    assert isinstance(task_ids, list), f"Expected a list of task ids, got {task_ids}. This is an internal error that should be reported."

    return list(sorted(task_ids))
TASK_IDS_MINI: List[int] = get_task_ids_sampled_wa(task_file='webarena.mini_ids.json')
TASK_IDS_TRAIN: List[int] = get_task_ids_sampled_wa(task_file='webarena.train_ids.json')
TASK_IDS_TEST: List[int] = get_task_ids_sampled_wa(task_file='webarena.test_ids.json')
TASK_VALID_TEST: List[int] = get_task_ids_sampled_wa(task_file='val_split.json')
TASK_HARD: List[int] = get_task_ids_sampled_wa(task_file='hard_tasks.json')
TASK_MEDIUM: List[int] = get_task_ids_sampled_wa(task_file='medium_tasks.json')
TASK_EASY: List[int] = get_task_ids_sampled_wa(task_file='easy_tasks.json')

class WebArenaBenchmarkWithoutReset(Benchmark):
    """Benchmark class for WebArena that does not perform full instance resets."""
    
    def prepare_backends(self):
        print("Preparing backends for WebArenaBenchmarkWithoutReset")
        for backend in self.backends:
            match backend:
                case "webarena":
                    # register environments
                    import browsergym.webarena

                    # full reset the instance (requires environment variables properly set up)
                    from browsergym.webarena.instance import WebArenaInstance

                    default_instance = WebArenaInstance()
                    
                    #default_instance.full_reset()  # comment this line for no reset 

                case _:
                    raise ValueError(f"Unknown benchmark backend {repr(backend)}. Note this is the class BenchmarkWithoutReset, which is a subclass of Benchmark that does not support reset, and only supports the webarena backend.")
    def subset_from_regexp(self, column, regexp):
        # extract the filtered task_name subset
        task_name_subset = task_list_from_metadata(self.task_metadata, {column: regexp})

        # return the sub benchmark
        return WebArenaBenchmarkWithoutReset(
            name=f"{self.name}[{column}=/{regexp}/]",
            high_level_action_set_args=self.high_level_action_set_args,
            is_multi_tab=self.is_multi_tab,
            supports_parallel_seeds=self.supports_parallel_seeds,
            backends=self.backends,
            env_args_list=[
                env_args
                for env_args in self.env_args_list
                if env_args.task_name in task_name_subset
            ],
            task_metadata=self.task_metadata,
        )
                
def get_webarena_benchmark():
    """
    Get the full WebArena benchmark.
    
    Returns:
        Benchmark instance with all WebArena tasks
    """
    return Benchmark(
        name="webarena",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_repeat_tasks(
            task_list=task_list_from_metadata(metadata=task_metadata("webarena")),
            max_steps=30,
            n_repeats=1,
            seeds_rng=np.random.RandomState(42),
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_mini_webarena_benchmark():
    """
    Get a mini WebArena benchmark with a subset of tasks (no full reset).
    
    Returns:
        WebArenaBenchmarkWithoutReset instance with a subset of WebArena tasks
    """
    return WebArenaBenchmarkWithoutReset(
        name="webarena_100",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_repeat_tasks(
            task_list=[f"webarena.{task_id}" for task_id in TASK_IDS_MINI],
            max_steps=30,
            n_repeats=1,
            seeds_rng=np.random.RandomState(42),
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_train_webarena_benchmark():
    """
    Get the WebArena training set benchmark.
    
    Returns:
        Benchmark instance with training set tasks
    """
    return Benchmark(
        name="webarena_train",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=[f"webarena.{task_id}" for task_id in TASK_IDS_TRAIN],
            max_steps=30,
            fixed_seeds=[0],
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_test_webarena_benchmark():
    """
    Get the WebArena test set benchmark.
    
    Returns:
        Benchmark instance with test set tasks
    """
    return Benchmark(
        name="webarena_test",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=[f"webarena.{task_id}" for task_id in TASK_IDS_TEST],
            max_steps=30,
            fixed_seeds=[0],
        ),
        task_metadata=task_metadata("webarena"),
    )


def get_valid_webarena_benchmark():
    """
    Get the WebArena validation set benchmark.
    
    Returns:
        Benchmark instance with validation set tasks
    """
    return Benchmark(
        name="webarena",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_repeat_tasks(
            task_list=[f"webarena.{task_id}" for task_id in TASK_VALID_TEST],
            max_steps=30,
            n_repeats=3,
            seeds_rng=np.random.RandomState(42),
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_hard_webarena_benchmark():
    """
    Get the WebArena hard difficulty benchmark.
    
    Returns:
        Benchmark instance with hard difficulty tasks
    """
    return Benchmark(
        name="webarena_hard",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=[f"webarena.{task_id}" for task_id in TASK_HARD],
            max_steps=30,
            fixed_seeds=[0],
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_medium_webarena_benchmark():
    """
    Get the WebArena medium difficulty benchmark.
    
    Returns:
        Benchmark instance with medium difficulty tasks
    """
    return Benchmark(
        name="webarena_medium",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=[f"webarena.{task_id}" for task_id in TASK_MEDIUM],
            max_steps=30,
            fixed_seeds=[0],
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_easy_webarena_benchmark():
    """
    Get the WebArena easy difficulty benchmark.
    
    Returns:
        Benchmark instance with easy difficulty tasks
    """
    return Benchmark(
        name="webarena_easy",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=[f"webarena.{task_id}" for task_id in TASK_EASY],
            max_steps=30,
            fixed_seeds=[0],
        ),
        task_metadata=task_metadata("webarena"),
    )