"""
Note: This script is a convenience script to launch experiments instead of using
the command line.

Don't push your changes to this file to git unless you are making structural changes.
"""

import logging
import argparse

from agentlab.agents.agent_args import AgentArgs

from experiments.Study import MyStudy
from experiments.Benchmark import get_webarena_benchmark, get_mini_webarena_benchmark
#import nltk; nltk.download('punkt');nltk.download('punkt_tab')

logging.getLogger().setLevel(logging.INFO)

def run_experiment(config,n_jobs):
    ## select the benchmark to run on
    #benchmark = "miniwob_tiny_test"
    # benchmark = "miniwob"
    # benchmark = "workarena.l1"
    # benchmark = "workarena.l2"
    # benchmark = "workarena.l3"
    #benchmark = "webarena"
    benchmark = get_webarena_benchmark()


    # Set reproducibility_mode = True for reproducibility
    # this will "ask" agents to be deterministic. Also, it will prevent you from launching if you have
    # local changes. For your custom agents you need to implement set_reproducibility_mode
    reproducibility_mode = False 

    # Set relaunch = True to relaunch an existing study, this will continue incomplete
    # experiments and relaunch errored experiments
    relaunch = False

    ## Number of parallel jobs
    #n_jobs = 4  # Make sure to use 1 job when debugging in VSCode
    # n_jobs = -1  # to use all available cores

    if relaunch:
        #  relaunch an existing study
        study = MyStudy.load_most_recent(contains=None)
        study.find_incomplete(include_errors=True)   
    else: 
        study =  MyStudy(config=config,agent_args=None, benchmark=benchmark,logging_level_stdout= logging.DEBUG)

    study.run(n_jobs=n_jobs, parallel_backend="joblib", strict_reproducibility=reproducibility_mode, n_relaunch=3)

    if reproducibility_mode:
        study.append_to_journal(strict_reproducibility=True)


if __name__ == "__main__":  # necessary for dask backend

    #TODO MAKE FUNCTION FOR REPRODUCTABILITY

    parser = argparse.ArgumentParser()

    parser.add_argument(
            "--config",
            type=str,
            default="CP",
            help="""Python path to the agent config. Defaults to : "agents.generic_agent.AGENT_4o".""",
        )
    parser.add_argument(
            "--n_jobs",
            type=str,
            default="1",
            help="""Python path to the agent config. Defaults to : "agents.generic_agent.AGENT_4o".""",
        )

    args, unknown = parser.parse_known_args()
    run_experiment(args.config, args.n_jobs)
    

