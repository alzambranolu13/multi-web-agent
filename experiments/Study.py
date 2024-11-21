import logging
import bgym
from bgym import Benchmark, EnvArgs, ExpArgs
from slugify import slugify

from browsergym.experiments.loop import ExpArgs
from agentlab.experiments.study import Study, logger
from agentlab.experiments.launch_exp import import_object
from agentlab.experiments.exp_utils import add_dependencies
from agentlab.experiments import reproducibility_util as repro

import agents
from agents.cont_plan_obs.exp_args import MultiAgentExpArgsCPO
from agents.planner_controller.exp_args import MultiAgentExpArgsCP

class MyStudy(Study):
    def __init__(self, config , agent_args, benchmark, logging_level_stdout=logging.WARNING):
        self.config = config
        super().__init__(agent_args= agent_args, benchmark=benchmark, suffix= config ,logging_level_stdout=logging_level_stdout)
        
    @property
    def name(self):
        agent_names = [self.config]
        if len(agent_names) == 1:
            study_name = f"{agent_names[0]}_on_{self.benchmark.name}"
        else:
            study_name = f"{len(agent_names)}_agents_on_{self.benchmark.name}"

        study_name = slugify(study_name, max_length=100, allow_unicode=True)

        if self.suffix:
            study_name += f"_{self.suffix}"
        return study_name
    
    def make_exp_args_list(self):
        self.exp_args_list = _multiagent_on_benchmark_(
            config = self.config,
            benchmark = self.benchmark, 
            logging_level=self.logging_level,
            logging_level_stdout=self.logging_level_stdout,
            ignore_dependencies=self.ignore_dependencies)
        
    def set_reproducibility_info(self, strict_reproducibility=False, comment=None):
        """Gather relevant information that may affect the reproducibility of the experiment

        e.g.: versions of BrowserGym, benchmark, AgentLab..."""
        agent_names = [self.config]
        info = repro.get_reproducibility_info(
            agent_names,
            self.benchmark,
            self.uuid,
            ignore_changes=not strict_reproducibility,
            comment=comment,
        )
        if self.reproducibility_info is not None:
            repro.assert_compatible(
                self.reproducibility_info, info, raise_if_incompatible=strict_reproducibility
            )
        self.reproducibility_info = info
        
def _multiagent_on_benchmark_(
        config: str,
        benchmark: bgym.Benchmark,
        demo_mode=False,
        logging_level: int = logging.INFO,
        logging_level_stdout: int = logging.INFO,
        ignore_dependencies=False,
    ):
    
    #MULTIAGENT BY DEFAULT OS JUST ONE CONFIGURATION AT TIME OF EXPERIMENT 

    env_args_list = benchmark.env_args_list


    configurations_exp={
        'CP': MultiAgentExpArgsCP(
                agents_dict= {
                    'PLANNER':agents.planner_controller.PLAN_AGENT,
                    'CONTROLLER': agents.planner_controller.CONTROLLER_AGENT
                },
                env_args= env_args_list,
                logging_level=logging_level
        ),  
        'CPO': MultiAgentExpArgsCPO(  
                agents_dict= {
                    'OBSERVER': agents.cont_plan_obs.OBSERVER_AGENT,
                    'PLANNER':agents.cont_plan_obs.PLAN_AGENT,
                    'CONTROLLER': agents.cont_plan_obs.CONTROLLER_AGENT,
                },
                env_args= env_args_list,
                logging_level=logging_level
        ), 
        'generic': ExpArgs(
                    agent_args= import_object('agentlab.agents.generic_agent.AGENT_4o_MINI') ,
                    env_args= env_args_list, 
                    logging_level=logging_level,
                    )         
    }


    exp_args_list = []

    for env_args in env_args_list: 
            exp_args = None
            if config == 'CP':
                exp_args = MultiAgentExpArgsCP(
                agents_dict= {
                    'PLANNER':agents.planner_controller.PLAN_AGENT,
                    'CONTROLLER': agents.planner_controller.CONTROLLER_AGENT
                },
                env_args= env_args,
                logging_level=logging_level
            )
                
            if config == 'CPO':
                exp_args = MultiAgentExpArgsCPO(  
                agents_dict= {
                    'OBSERVER': agents.cont_plan_obs.OBSERVER_AGENT,
                    'PLANNER':agents.cont_plan_obs.PLAN_AGENT,
                    'CONTROLLER': agents.cont_plan_obs.CONTROLLER_AGENT,
                },
                env_args= env_args,
                logging_level=logging_level
            )

            else:
                exp_args = ExpArgs(
                    agent_args= import_object('agentlab.agents.generic_agent.AGENT_4o_MINI') ,
                    env_args= env_args, 
                    logging_level=logging_level,
                )      

            exp_args_list.append(exp_args)

    for i, exp_args in enumerate(exp_args_list):
        exp_args.order = i

    # not required with ray, but keeping around if we would need it for visualwebareana on joblib
    # _flag_sequential_exp(exp_args_list, benchmark)

    if not ignore_dependencies:
        # populate the depends_on field based on the task dependencies in the benchmark
        exp_args_list = add_dependencies(exp_args_list, benchmark.dependency_graph_over_tasks())
    else:
        logger.warning(
            f"Ignoring dependencies for benchmark {benchmark.name}. This could lead to different results."
        )
    
    return exp_args_list
    


        