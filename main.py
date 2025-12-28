"""
Main entry point for running multi-agent web automation experiments.

This script provides a command-line interface to launch experiments with various
agent configurations on WebArena benchmarks. It supports single-agent and multi-agent
configurations including Planner-Controller (CP), Planner-Controller-Fixed (CPFixed),
and Planner-Controller-Observer (CPO) setups.
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
from utils.models import AGENT_41_MINI, AGENT_41, AGENT_QWEN_25, AGENT_41_PLAN, AGENT_QWEN_25_PLAN, AGENT_GEMINI_25FLASH, AGENT_GEMINI_25FLASH_PLAN

logging.getLogger().setLevel(logging.DEBUG)


def select_model(model_name):
    """
    Select a model backend based on the model name string.
    
    Args:
        model_name: String identifier for the model (e.g., '4o-mini', '41-mini', etc.)
        
    Returns:
        Model backend configuration object
        
    Raises:
        ValueError: If the model name is not recognized
    """
    if model_name is None:
        return None

    model_backend = None
    if model_name == '4o-mini':
        model_backend = AGENT_4o_MINI
    elif model_name == '41-mini':
        model_backend = AGENT_41_MINI
    elif model_name == '41-mini-plan':
        model_backend = AGENT_41_PLAN
    elif model_name == '41':
        model_backend = AGENT_41
    elif model_name == 'qwen':
        model_backend = AGENT_QWEN_25
    elif model_name == 'gemini':
        model_backend = AGENT_GEMINI_25FLASH
    elif model_name == 'gemini-plan':
        model_backend = AGENT_GEMINI_25FLASH_PLAN
    elif model_name == 'qwen-plan':
        model_backend = AGENT_QWEN_25_PLAN

    if model_backend is None:
        raise ValueError(f"Model {model_name} not recognized.")
    
    return model_backend

def run_experiment(config, n_jobs, suffix, relaunch, reproduce, contains=None, strategy="strategy_1", 
                   prompt_opt=0, run_set="test", model_backend='4o-mini', model_planner='4o-mini', 
                   model_controller='4o-mini', ignore_dependencies=False):
    """
    Run an experiment with the specified configuration.
    
    Args:
        config: Agent configuration type ('generic', 'CP', 'CPFixed', or 'CPO')
        n_jobs: Number of parallel jobs to run
        suffix: Suffix for experiment name
        relaunch: Whether to relaunch an existing study
        reproduce: Whether to enable reproducibility mode
        contains: Keyword to find experiment directory if relaunch is True
        strategy: Strategy identifier for the planner agent
        prompt_opt: Prompt option index for the planner agent
        run_set: Dataset split to run on ('train', 'test', 'valid', 'hard', 'medium', 'easy')
        model_backend: Model backend for single-agent or generic config
        model_planner: Model backend for planner agent
        model_controller: Model backend for controller agent
        ignore_dependencies: Whether to ignore task dependencies
    """
    
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

    model_backend = select_model(model_backend)
    model_planner = select_model(model_planner)
    model_controller = select_model(model_controller)

    reproducibility_mode = reproduce
    relaunch = relaunch
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
        planner_args = PlannerAgentArg(chat_model_args=model_planner.chat_model_args)
        controller_args = ControllerAgentArgs(chat_model_args=model_controller.chat_model_args, flags= FLAGS_GPT_4o)
        observer_args = ObserverAgentArgs(chat_model_args=model_controller.chat_model_args)
        if config == 'CP' :
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )
        if config == 'CPFixed':
            planner_args = FixedPlannerAgentArg(chat_model_args=model_planner.chat_model_args ,strategy=strategy, prompt_opt=prompt_opt, temperature= 0.6)
            controller_args = FixedControllerAgentArg(chat_model_args=model_controller.chat_model_args, flags= FLAGS_GPT_4o_FIXED)
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )
        if config == 'CPO':
            multi_agent_args = MultiAgentArgs(planner_args=planner_args, controller_args=controller_args, observer_args=observer_args)
        
        if reproducibility_mode:
            multi_agent_args.controller_args.set_reproducibility_mode()
            
    if relaunch:
        study = MyStudy.load_most_recent(contains=contains)
        study.find_incomplete(include_errors=True)   
    else: 
        study = MyStudy(
            config=config,
            multi_agent_args=multi_agent_args,
            single_agent_args=single_agent_args,
            suffix=suffix,
            benchmark=benchmark,
            logging_level_stdout=logging.DEBUG,
            ignore_dependencies=ignore_dependencies
        )

    study.run(n_jobs=n_jobs, parallel_backend="joblib", strict_reproducibility=False, n_relaunch=3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run multi-agent web automation experiments on WebArena benchmarks"
    )

    parser.add_argument(
            "--config",
            type=str,
            default="CPFixed",
            help="Agent configuration type: 'generic', 'CP', 'CPFixed', or 'CPO'. Defaults to 'CPFixed'.",
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
            help="Enable reproducibility mode (makes agents deterministic). Defaults to False.",
            action=argparse.BooleanOptionalAction
        )
    parser.add_argument(
            "--relaunch",
            type=bool,
            default=False,
            help="Relaunch an existing study (continues incomplete experiments). Defaults to False.",
            action=argparse.BooleanOptionalAction
        )
    parser.add_argument(
            "--ignore_dependencies",
            type=bool,
            default=False,
            help="Ignore task dependencies in the benchmark. Defaults to False.",
            action=argparse.BooleanOptionalAction
        )
    parser.add_argument(
            "--contains",
            type=str,
            default=None,
            help="Keyword to find experiment directory if relaunch is set to True. Defaults to None.",
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
            help="Prompt option index for the planner agent. Defaults to 0.",
        )
    parser.add_argument(
            "--run_set",
            type=str,
            default="test",
            help="Dataset split to run on: 'train', 'test', 'valid', 'hard', 'medium', or 'easy'. Defaults to 'test'.",
        )
    parser.add_argument(
            "--backend",
            type=str,
            default=None,
            help="Model backend for single-agent or generic config (e.g., '4o-mini', '41-mini'). Defaults to None.",
        )
    parser.add_argument(
            "--planner",
            type=str,
            default='41-mini',
            help="Model backend for planner agent (e.g., '4o-mini', '41-mini'). Defaults to '41-mini'.",
        )
    parser.add_argument(
            "--controller",
            type=str,
            default='41-mini',
            help="Model backend for controller agent (e.g., '4o-mini', '41-mini'). Defaults to '41-mini'.",
        )
    
 

    args, unknown = parser.parse_known_args()
    if args.contains is not None and not args.relaunch:
        raise ValueError('The --contains argument requires --relaunch to be True.')
    
    run_experiment(
        config=args.config,
        n_jobs=args.n_jobs,
        suffix=args.suffix,
        relaunch=args.relaunch,
        contains=args.contains,
        reproduce=args.reproduce,
        strategy=args.strategy,
        prompt_opt=args.prompt_opt,
        run_set=args.run_set,
        model_backend=args.backend,
        model_planner=args.planner,
        model_controller=args.controller,
        ignore_dependencies=args.ignore_dependencies
    )
