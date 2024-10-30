"""
Note: This script is a convenience script to launch experiments instead of using
the command line.

Don't push your changes to this file to git unless you are making structural changes.
"""

import logging

from agentlab.agents.generic_agent import AGENT_CUSTOM, RANDOM_SEARCH_AGENT, AGENT_4o, AGENT_4o_MINI
from agentlab.analyze.inspect_results import get_most_recent_folder
from agentlab.experiments import study_generators
from agentlab.experiments.exp_utils import RESULTS_DIR
from agentlab.experiments.launch_exp import make_study_dir, relaunch_study, run_experiments
from agentlab.experiments import task_collections as tasks
from agentlab.experiments.launch_exp import import_object
from browsergym.experiments.loop import EnvArgs, ExpArgs
from agentlab.experiments import args

import agents
from agents.cont_plan_obs.exp_args import MultiAgentExpArgsCPO
from agents.planner_controller.exp_args import MultiAgentExpArgsCP

import nltk; nltk.download('punkt')

logging.getLogger().setLevel(logging.INFO)

config='CP'

## select the benchmark to run on
#benchmark = "miniwob_tiny_test"
# benchmark = "miniwob"
# benchmark = "workarena.l1"
# benchmark = "workarena.l2"
# benchmark = "workarena.l3"
benchmark = "webarena"

study_name= ""
env_args_list = args.CrossProd(tasks.get_benchmark_env_args(
        benchmark, meta_seed=43, max_steps=None, n_repeat=None
    ))
exp_args = None
if  config == 'CP':
        study_name= 'multiagent_CP',
        exp_args = args.expand_cross_product(
            MultiAgentExpArgsCP(
                agents_dict= {
                    'PLANNER':agents.planner_controller.PLAN_AGENT,
                    'CONTROLLER': agents.planner_controller.CONTROLLER_AGENT
                },
                env_args= env_args_list,
                logging_level=logging.DEBUG,
            )
        )

if config == 'CPO':
        study_name= 'multiagent_CPO'
        exp_args = args.expand_cross_product(
                MultiAgentExpArgsCPO(  
                agents_dict= {
                    'OBSERVER': agents.cont_plan_obs.OBSERVER_AGENT,
                    'PLANNER':agents.cont_plan_obs.PLAN_AGENT,
                    'CONTROLLER': agents.cont_plan_obs.CONTROLLER_AGENT,
                },
                env_args= env_args_list,
                logging_level=logging.DEBUG,
            )
        )
if config == 'generic':
        study_name= 'generic_agent_4o_mini'
        agent_args = import_object('agentlab.agents.generic_agent.AGENT_4o_MINI')
        exp_args = args.expand_cross_product(
               ExpArgs(
                      agent_args=agent_args, 
                      env_args= env_args_list, 
                      logging_level=logging.DEBUG
                      )
                )





## select the kind of experiment (study)
## Or define new studies, you only have to return list of ExpArgs to run and a name for the study
#study_name, exp_args_list = study_generators.run_agents_on_benchmark(agent_args, benchmark)
# study_name, exp_args_list = study_generators.ablation_study(agent, benchmark)
# study_name, exp_args_list = study_generators.random_search(agent, benchmark, n_samples=20)

study_dir = make_study_dir(RESULTS_DIR, study_name)


## alternatively, relaunch an existing study
# study_dir = get_most_recent_folder(RESULTS_DIR, contains=None)
exp_args_list, study_dir = relaunch_study(study_dir, relaunch_mode="incomplete_or_error")


## Number of parallel jobs
n_jobs = 4  # Make sure to use 1 job when debugging in VSCode
# n_jobs = -1  # to use all available cores

# run the experiments
if __name__ == "__main__":
    run_experiments(n_jobs, exp_args, study_dir)
