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
from experiments.Benchmark import get_webarena_benchmark, get_mini_webarena_benchmark, get_train_webarena_benchmark, get_test_webarena_benchmark, get_valid_webarena_benchmark, get_hard_webarena_benchmark, get_medium_webarena_benchmark, get_easy_webarena_benchmark
from agentlab.agents.generic_agent import (
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
from utils.models import AGENT_41_MINI, AGENT_41, AGENT_QWEN_25, AGENT_41_PLAN, AGENT_QWEN_25_PLAN
#import nltk; nltk.download('punkt');nltk.download('punkt_tab')

logging.getLogger().setLevel(logging.DEBUG)



def run_experiment(config,n_jobs,suffix,relaunch,reproduce, contains=None, strategy="strategy_1", prompt_opt=0, run_set="test", model_backend='4o-mini', ignore_dependencies=False):
    ## select the benchmark to run on
    # benchmark = "miniwob_tiny_test"
    # benchmark = "miniwob"
    # benchmark = "workarena.l1"
    # benchmark = "workarena.l2"
    # benchmark = "workarena.l3"
    # benchmark = "webarena"
    benchmark = None
    if run_set == "train":
        benchmark = get_train_webarena_benchmark()
    elif run_set == "test":
        benchmark = get_test_webarena_benchmark()
    elif run_set == "valid":
        benchmark = get_valid_webarena_benchmark()
    elif run_set == "hard":
        benchmark = get_hard_webarena_benchmark()
    elif run_set == "medium":
        benchmark = get_medium_webarena_benchmark()
    elif run_set == "easy":
        benchmark = get_easy_webarena_benchmark()

    if model_backend == '4o-mini':
        model_backend = AGENT_4o_MINI
    elif model_backend == '41-mini':
        model_backend = AGENT_41_MINI
    elif model_backend == '41-mini-plan':
        model_backend = AGENT_41_PLAN
    elif model_backend == '41':
        model_backend = AGENT_41
    elif model_backend == 'qwen':
        model_backend = AGENT_QWEN_25
    elif model_backend == 'qwen-plan':
        model_backend = AGENT_QWEN_25_PLAN

    # Set reproducibility_mode = True for reproducibility
    # this will "ask" agents to be deterministic. Also, it will prevent you from launching if you have
    # local changes. For your custom agents you need to implement set_reproducibility_mode
    reproducibility_mode = reproduce 

    # Set relaunch = True to relaunch an existing study, this will continue incomplete
    # experiments and relaunch errored experiments
    relaunch = relaunch

    ## Number of parallel jobs
    #n_jobs = 4  # Make sure to use 1 job when debugging in VSCode
    # n_jobs = -1  # to use all available cores
    multi_agent_args = None
    single_agent_args = None
    

    if config == 'generic':
        single_agent_args = model_backend
        #set reproductibility for single agent
        if reproducibility_mode:
            single_agent_args.set_reproducibility_mode()
        else:
            single_agent_args.chat_model_args.temperature = 0.4
    else:
        if suffix is None:
            suffix = f"{strategy}_v{prompt_opt}"
        planner_args = PlannerAgentArg(chat_model_args=AGENT_QWEN_25.chat_model_args)
        controller_args = ControllerAgentArgs(chat_model_args=AGENT_41_MINI.chat_model_args, flags= FLAGS_GPT_4o)
        observer_args = ObserverAgentArgs(chat_model_args=model_backend.chat_model_args)
        if config == 'CP' :
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )
        if config == 'CPFixed':
            planner_args = FixedPlannerAgentArg(chat_model_args=AGENT_QWEN_25.chat_model_args ,strategy=strategy, prompt_opt=prompt_opt, temperature= 0.6)
            controller_args = FixedControllerAgentArg(chat_model_args=AGENT_41_MINI.chat_model_args, flags= FLAGS_GPT_4o_FIXED)
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )
        if config == 'CPO':
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= observer_args )
        #set reproductibility for multi-agent
        if reproducibility_mode:
            multi_agent_args.controller_args.set_reproducibility_mode()

        #multi_agent_args.controller_args.chat_model_args.temperature = 0.4
        #multi_agent_args.planner_args.chat_model_args.temperature = 0.4
            #multi_agent_args.observer_args.chat_model_args.temperature = 0.4
            
    if relaunch:
        #  relaunch an existing study
        study = MyStudy.load_most_recent(contains=contains)
        study.find_incomplete(include_errors=True)   
    else: 
        study =  MyStudy(config=config,multi_agent_args=multi_agent_args, single_agent_args= single_agent_args, suffix= suffix,benchmark=benchmark,logging_level_stdout= logging.DEBUG, ignore_dependencies=ignore_dependencies)

    study.run(n_jobs=n_jobs, parallel_backend="joblib", strict_reproducibility=False, n_relaunch=3)

    # if reproducibility_mode:
    #     study.append_to_journal(strict_reproducibility=True)


if __name__ == "__main__":  # necessary for dask backend

    #TODO MAKE FUNCTION FOR REPRODUCTABILITY

    parser = argparse.ArgumentParser()

    parser.add_argument(
            "--config",
            type=str,
            default="CPFixed",
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
            "--reproduce",
            type=bool,
            default=False,
            help="""Bool for reproducibility mode. Defaults to : False""",
            action=argparse.BooleanOptionalAction
        )
    parser.add_argument(
            "--relaunch",
            type=bool,
            default=False,
            help="""Bool value for relaunch". Defaults to false""",
            action=argparse.BooleanOptionalAction
        )
    parser.add_argument(
            "--ignore_dependencies",
            type=bool,
            default=False,
            help="""Bool value for relaunch". Defaults to false""",
            action=argparse.BooleanOptionalAction
        )
    parser.add_argument(
            "--contains",
            type=str,
            default=None,
            help="""Keyword to find exp dir if relaunch is set to true. Defaults to empty""",
        )
    parser.add_argument(
            "--strategy",
            type=str,
            default="strategy_1",
            help="""Keyword to set the strategy for the planner agent. Defaults to strategy_1""",
        )
    parser.add_argument(
            "--prompt_opt",
            type=int,
            default=0,
            help="""Keyword to set the prompt from list of prompts for the planner agent. Defaults to 0""",
        )
    parser.add_argument(
            "--run_set",
            type=str,
            default="test",
            help="""Keyword to set the prompt from list of prompts for the planner agent. Defaults to 0""",
        )
    parser.add_argument(
            "--backend",
            type=str,
            default="41-m",
            help="""Keyword to set the prompt from list of prompts for the planner agent. Defaults to 0""",
        )
 

    args, unknown = parser.parse_known_args()
    if args.contains !=  None:
        if args.contains == True:
            raise Exception('Value contains is set to not None but relaunch is false')
    
    run_experiment(config=args.config, n_jobs=args.n_jobs,suffix=args.suffix,relaunch=args.relaunch, contains=args.contains, reproduce=args.reproduce, strategy=args.strategy, prompt_opt=args.prompt_opt, run_set=args.run_set, model_backend=args.backend, ignore_dependencies=args.ignore_dependencies)
