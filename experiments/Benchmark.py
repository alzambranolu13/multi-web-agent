import numpy as np

from browsergym.experiments.benchmark.metadata.utils import (
    task_metadata,task_list_from_metadata
)
from browsergym.experiments.benchmark.utils import (
    make_env_args_list_from_repeat_tasks,make_env_args_list_from_fixed_seeds
)

from browsergym.experiments.benchmark.base import Benchmark, HighLevelActionSetArgs
from browsergym.experiments.benchmark.configs import DEFAULT_HIGHLEVEL_ACTION_SET_ARGS


from typing import List

TASK_IDS= [157,44,156]

class WebArenaBenchmarkWithoutReset(Benchmark):
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
                    
                    # default_instance.full_reset()  # no reset

                case _:
                    raise ValueError(f"Unknown benchmark backend {repr(backend)}. Note this is the class BenchmarkWithoutReset, which is a subclass of Benchmark that does not support reset, and only supports the webarena backend.")
                
def get_webarena_benchmark():
    # TODO: Might want to switch back to `Backend` when WA_FULL_RESET issue is resolved
    return WebArenaBenchmarkWithoutReset(
        name="webarena",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_repeat_tasks(
            task_list=task_list_from_metadata(metadata=task_metadata("webarena")),
            max_steps=20,
            n_repeats=1,
            seeds_rng=np.random.RandomState(42),
        ),
        task_metadata=task_metadata("webarena"),
    )

def get_mini_webarena_benchmark():
    # TODO: Might want to switch back to `Backend` when WA_FULL_RESET issue is resolved
    return WebArenaBenchmarkWithoutReset(
        name="webarena_100",
        high_level_action_set_args=DEFAULT_HIGHLEVEL_ACTION_SET_ARGS["webarena"],
        is_multi_tab=True,
        supports_parallel_seeds=False,
        backends=["webarena"],
        env_args_list=make_env_args_list_from_fixed_seeds(
            task_list=[f"webarena.{task_id}" for task_id in TASK_IDS],
            max_steps=20,
            fixed_seeds=[0],
        ),
        task_metadata=task_metadata("webarena"),
    )