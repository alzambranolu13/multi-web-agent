from dataclasses import dataclass
import logging
import bgym
from bgym import Benchmark, EnvArgs, ExpArgs
from slugify import slugify
from pathlib import Path
import gzip
import pickle

from browsergym.experiments.loop import ExpArgs
from agentlab.experiments.study import Study, logger,inspect_results
from agentlab.experiments.launch_exp import import_object
from agentlab.experiments.exp_utils import add_dependencies
from agentlab.experiments import reproducibility_util as repro
from agentlab.agents.agent_args import AgentArgs

import agents
from agents.cont_plan_obs.exp_args import MultiAgentExpArgsCPO
from agents.planner_controller.exp_args import MultiAgentExpArgsCP
from agents.planner_controller_fixedPlan.exp_args import MultiAgentExpArgsCPfixed
import agents.planner_controller
from agents import MultiAgentArgs


class MyStudy(Study):
    def __init__(self, config , multi_agent_args, single_agent_args, suffix, benchmark, logging_level_stdout=logging.WARNING):
        self.config = config
        self.multi_agent_args = multi_agent_args
        if suffix == None:
            suffix= config
        super().__init__(agent_args= single_agent_args, benchmark=benchmark, suffix= suffix ,logging_level_stdout=logging_level_stdout)
        
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
    
    @staticmethod
    def load(dir: Path) -> "MyStudy":
        dir = Path(dir)
        study_path = dir / "study.pkl.gz"
        if not study_path.exists() and dir.is_dir():
            # For backward compatibility
            # first_result = next(
            #     inspect_results.yield_all_exp_results(savedir_base=dir, progress_fn=None)
            # )
            # benchmark_name = first_result.exp_args.env_args.task_name.split(".")[0]
            # agent_args = first_result.exp_args.agent_args
            # study = MyStudy(agent_args=agent_args, benchmark=benchmark_name, dir=dir)
            raise Exception( 'No study.pkl.gz found please make sure it exists for relaunch')
        else:
            with gzip.open(dir / "study.pkl.gz", "rb") as f:
                study = pickle.load(f)  # type: Study
            study.dir = dir

            # # just a check
            # for i, exp_args in enumerate(study.exp_args_list):
            #     if exp_args.order != i:
            #         logging.warning(f"The order of the experiments is not correct. {exp_args.order} != {i}")

        return study
    def make_exp_args_list(self):
        self.exp_args_list = _multiagent_on_benchmark_(
            multi_agent_args= self.multi_agent_args,
            single_agent_args= self.agent_args,
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
    multi_agent_args: MultiAgentArgs,
    config: str,
    benchmark: bgym.Benchmark,
    single_agent_args: AgentArgs = None,
    demo_mode=False,
    logging_level: int = logging.INFO,
    logging_level_stdout: int = logging.INFO,
    ignore_dependencies=False,
):
    
    #MULTIAGENT BY DEFAULT OS JUST ONE CONFIGURATION AT TIME OF EXPERIMENT 

    env_args_list = benchmark.env_args_list


    exp_args_list = []

    for env_args in env_args_list: 
            exp_args = None
            if config == 'CP':
                multi_agent_args.controller_args.set_benchmark(benchmark, demo_mode)
                exp_args = MultiAgentExpArgsCP(
                    agents_dict= {
                        'PLANNER': multi_agent_args.planner_args,
                        'CONTROLLER': multi_agent_args.controller_args
                    },
                    env_args= env_args,
                    logging_level=logging_level
                )

            elif config == 'CPFixed':
                multi_agent_args.controller_args.set_benchmark(benchmark, demo_mode)
                exp_args = MultiAgentExpArgsCPfixed(
                    agents_dict= {
                        'PLANNER': multi_agent_args.planner_args,
                        'CONTROLLER': multi_agent_args.controller_args
                    },
                    env_args= env_args,
                    logging_level=logging_level
                )
                
            elif config == 'CPO':
                multi_agent_args.controller_args.set_benchmark(benchmark, demo_mode)
                exp_args = MultiAgentExpArgsCPO(  
                    agents_dict= {
                        'OBSERVER': multi_agent_args.observer_args,
                        'PLANNER': multi_agent_args.planner_args,
                        'CONTROLLER': multi_agent_args.controller_args
                    },
                    env_args= env_args,
                    logging_level=logging_level
                )

            else:
                single_agent_args.set_benchmark(benchmark, demo_mode)
                exp_args = ExpArgs(
                    agent_args= single_agent_args,
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
    


        