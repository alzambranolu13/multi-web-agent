"""
Note: This script is a convenience script to launch experiments instead of using
the command line.

Don't push your changes to this file to git unless you are making structural changes.
"""

import logging
import argparse

from agentlab.agents.generic_agent import AGENT_CUSTOM, RANDOM_SEARCH_AGENT, AGENT_4o, AGENT_4o_MINI
from agentlab.analyze.inspect_results import get_most_recent_folder
from agentlab.experiments import study_generators
from agentlab.experiments.exp_utils import RESULTS_DIR
from agentlab.experiments.launch_exp import  relaunch_study, run_experiments
from agentlab.analyze.inspect_results import get_most_recent_folder
from agentlab.experiments.study_generators import run_agents_on_benchmark, Study
from agentlab.experiments import task_collections as tasks
from agentlab.experiments.launch_exp import import_object
from browsergym.experiments.loop import EnvArgs, ExpArgs
from agentlab.experiments import args as args_exp

import agents
from agents.cont_plan_obs.exp_args import MultiAgentExpArgsCPO
from agents.planner_controller.exp_args import MultiAgentExpArgsCP

#import nltk; nltk.download('punkt');nltk.download('punkt_tab')

logging.getLogger().setLevel(logging.INFO)

def run_experiment(config,n_jobs):

    #config='generic'

    ## select the benchmark to run on
    #benchmark = "miniwob_tiny_test"
    # benchmark = "miniwob"
    # benchmark = "workarena.l1"
    # benchmark = "workarena.l2"
    # benchmark = "workarena.l3"
    benchmark = "webarena"

    log_level=logging.DEBUG

    study_name= ""
    env_args_list = args_exp.CrossProd(tasks.get_benchmark_env_args(
            benchmark, meta_seed=43, max_steps=None, n_repeat=None
        ))
    study = None
    if  config == 'CP':
        study = Study(
            benchmark_name = benchmark,
            agent_names = 'multiagent_CP',
            suffix = 'multiagent_CP',
            exp_args_list = args.expand_cross_product(
                MultiAgentExpArgsCP(
                    agents_dict= {
                        'PLANNER':agents.planner_controller.PLAN_AGENT,
                        'CONTROLLER': agents.planner_controller.CONTROLLER_AGENT
                    },
                    env_args= env_args_list,
                    logging_level=log_level
                )
            ),
            
        )

    if config == 'CPO':
        study = Study(    
            benchmark_name = benchmark,
            agent_names = 'multiagent_CPO',
            suffix = 'multiagent_CPO',
            exp_exp_args_lists = args_exp.expand_cross_product(
                    MultiAgentExpArgsCPO(  
                    agents_dict= {
                        'OBSERVER': agents.cont_plan_obs.OBSERVER_AGENT,
                        'PLANNER':agents.cont_plan_obs.PLAN_AGENT,
                        'CONTROLLER': agents.cont_plan_obs.CONTROLLER_AGENT,
                    },
                    env_args= env_args_list,
                    logging_level=log_level
                )          
            ),
        )

    if config == 'generic':
        study = Study( 
            benchmark_name = benchmark,
            agent_names= 'generic_agent_4o_mini',
            suffix= 'generic_agent_4o_mini',  
            exp_args_list = args_exp.expand_cross_product(
                ExpArgs(
                        agent_args= import_object('agentlab.agents.generic_agent.AGENT_4o_MINI') ,
                        env_args= env_args_list, 
                        logging_level=log_level,
                        )
                    ),     
        )


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
        study_dir = get_most_recent_folder()
        study = study_generators.make_relaunch_study(study_dir, relaunch_mode="incomplete_or_error")

    study.run(n_jobs=n_jobs, parallel_backend="joblib", strict_reproducibility=reproducibility_mode)

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
            default="4",
            help="""Python path to the agent config. Defaults to : "agents.generic_agent.AGENT_4o".""",
        )

    args, unknown = parser.parse_known_args()
    run_experiment(args.config, args.n_jobs)
    

