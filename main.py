"""
Note: This script is a convenience script to launch experiments instead of using
the command line.

Don't push your changes to this file to git unless you are making structural changes.
"""

import logging
import argparse

from agentlab.agents.agent_args import AgentArgs

from agents import MultiAgentArgs
from experiments.Study import MyStudy
from experiments.Benchmark import get_webarena_benchmark, get_mini_webarena_benchmark, get_webarena_benchmark_split
from agentlab.agents.generic_agent import (
    AGENT_LLAMA3_70B,
    AGENT_LLAMA31_70B,
    RANDOM_SEARCH_AGENT,
    AGENT_4o,
    AGENT_4o_MINI,
)
from agents.planner_controller import (
    FLAGS_GPT_4o
)


from agents.planner_controller.agent_args import (
    PlannerAgentArg,
    ControllerAgentArgs
)

from agents.cont_plan_obs.agent_args import (
    ObserverAgentArgs,
)

from agents.planner_controller_fixedPlan.agent_args import PlannerAgentArg as FixedPlannerAgentArg
from agents.planner_controller_fixedPlan.agent_args import ControllerAgentArgs as FixedControllerAgentArg
from agents.planner_controller_fixedPlan import  FLAGS_GPT_4o as FLAGS_GPT_4o_FIXED

#import nltk; nltk.download('punkt');nltk.download('punkt_tab')

logging.getLogger().setLevel(logging.INFO)



def run_experiment(config,n_jobs,suffix,relaunch,contains=None):
    ## select the benchmark to run on
    #benchmark = "miniwob_tiny_test"
    # benchmark = "miniwob"
    # benchmark = "workarena.l1"
    # benchmark = "workarena.l2"
    # benchmark = "workarena.l3"
    #benchmark = "webarena"
    benchmark = get_webarena_benchmark_split()


    # Set reproducibility_mode = True for reproducibility
    # this will "ask" agents to be deterministic. Also, it will prevent you from launching if you have
    # local changes. For your custom agents you need to implement set_reproducibility_mode
    reproducibility_mode = False 

    # Set relaunch = True to relaunch an existing study, this will continue incomplete
    # experiments and relaunch errored experiments
    relaunch = relaunch

    ## Number of parallel jobs
    #n_jobs = 4  # Make sure to use 1 job when debugging in VSCode
    # n_jobs = -1  # to use all available cores
    multi_agent_args = None
    single_agent_args = None

    if config == 'generic':
        single_agent_args = AGENT_4o_MINI
    else:
        planner_args = PlannerAgentArg(chat_model_args=AGENT_4o_MINI.chat_model_args)
        controller_args = ControllerAgentArgs(chat_model_args=AGENT_4o_MINI.chat_model_args, flags= FLAGS_GPT_4o)
        observer_args = ObserverAgentArgs(chat_model_args=AGENT_4o_MINI.chat_model_args)
        if config == 'CP' :
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )
        if config == 'CPFixed':
            planner_args = FixedPlannerAgentArg(chat_model_args=AGENT_4o_MINI.chat_model_args)
            controller_args = FixedControllerAgentArg(chat_model_args=AGENT_4o_MINI.chat_model_args, flags= FLAGS_GPT_4o_FIXED)
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )
        if config == 'CPO':
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= observer_args )
            
    if relaunch:
        #  relaunch an existing study
        study = MyStudy.load_most_recent(contains=contains)
        study.find_incomplete(include_errors=True)   
    else: 
        study =  MyStudy(config=config,multi_agent_args=multi_agent_args, single_agent_args= single_agent_args, suffix= suffix,benchmark=benchmark,logging_level_stdout= logging.DEBUG)

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
            help="""Python path to the agent config. Defaults to : "Planner-Controller configuration.""",
        )
    parser.add_argument(
            "--n_jobs",
            type=int,
            default=1,
            help="""Number of jobs to run experiments. Defaults to : 1.""",
        )
    parser.add_argument(
            "--suffix",
            type=str,
            default=None,
            help="""Suffix for experiment name. Defaults to : None.""",
        )
    parser.add_argument(
            "--relaunch",
            type=bool,
            default=False,
            help="""Bool value for relaunch". Defaults to false""",
        )
    parser.add_argument(
            "--contains",
            type=str,
            default=None,
            help="""Keyword to find exp dir if relaunch is set to true. Defaults to empty""",
        )

    args, unknown = parser.parse_known_args()
    if args.contains !=  None:
        if args.contains == True:
            raise Exception('Value contains is set to not None but relaunch is false')
    
    run_experiment(args.config, args.n_jobs,args.suffix,args.relaunch, args.contains)
