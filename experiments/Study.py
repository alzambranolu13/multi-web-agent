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
    """
    Custom Study class for multi-agent web automation experiments.
    
    Extends the base Study class to support multi-agent configurations
    including Planner-Controller (CP), Planner-Controller-Fixed (CPFixed),
    and Planner-Controller-Observer (CPO) setups.
    """
    
    def __init__(self, config, multi_agent_args, single_agent_args, suffix, benchmark, 
                 logging_level=logging.DEBUG, logging_level_stdout=logging.WARNING, 
                 ignore_dependencies=False):
        """
        Initialize a multi-agent study.
        
        Args:
            config: Agent configuration type ('generic', 'CP', 'CPFixed', or 'CPO')
            multi_agent_args: Multi-agent arguments (None for generic config)
            single_agent_args: Single agent arguments (for generic config)
            suffix: Suffix for experiment name
            benchmark: Benchmark to run experiments on
            logging_level: Logging level for file output
            logging_level_stdout: Logging level for stdout
            ignore_dependencies: Whether to ignore task dependencies
        """
        self.config = config
        self.multi_agent_args = multi_agent_args
        if suffix is None:
            suffix = config
        super().__init__(
            agent_args=single_agent_args,
            benchmark=benchmark,
            suffix=suffix,
            logging_level=logging_level,
            logging_level_stdout=logging_level_stdout,
            ignore_dependencies=ignore_dependencies
        )
        
    @property
    def name(self):
        """Generate a unique study name based on configuration and benchmark."""
        if self.config == 'CP' or self.config == 'CPFixed':
            agent_name = self.multi_agent_args.controller_args.agent_name
        else:
            agent_name = self.agent_args.agent_name
        agent_names = [self.config + "_" + agent_name]
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
        """
        Load a study from a directory.
        
        Args:
            dir: Directory containing the study.pkl.gz file
            
        Returns:
            Loaded MyStudy instance
            
        Raises:
            Exception: If study.pkl.gz is not found
        """
        dir = Path(dir)
        study_path = dir / "study.pkl.gz"
        if not study_path.exists() and dir.is_dir():
            raise Exception('No study.pkl.gz found. Please make sure it exists for relaunch.')
        else:
            with gzip.open(dir / "study.pkl.gz", "rb") as f:
                study = pickle.load(f)  # type: Study
            study.dir = dir

        return study
    def make_exp_args_list(self):
        """Generate the list of experiment arguments for the benchmark."""
        self.exp_args_list = _multiagent_on_benchmark_(
            multi_agent_args=self.multi_agent_args,
            single_agent_args=self.agent_args,
            config=self.config,
            benchmark=self.benchmark,
            logging_level=self.logging_level,
            logging_level_stdout=self.logging_level_stdout,
            ignore_dependencies=self.ignore_dependencies
        )
        
    def set_reproducibility_info(self, strict_reproducibility=False, comment=None):
        """
        Gather relevant information that may affect the reproducibility of the experiment.
        
        Collects versions of BrowserGym, benchmark, AgentLab, and other dependencies.
        
        Args:
            strict_reproducibility: If True, raises error on incompatibility
            comment: Optional comment to include in reproducibility info
        """
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
    logging_level: int = logging.DEBUG,
    logging_level_stdout: int = logging.DEBUG,
    ignore_dependencies=False,
):
    """
    Create experiment arguments for running multi-agent or single-agent experiments on a benchmark.
    
    Args:
        multi_agent_args: Multi-agent configuration arguments
        config: Agent configuration type ('generic', 'CP', 'CPFixed', or 'CPO')
        benchmark: Benchmark to run experiments on
        single_agent_args: Single agent arguments (for generic config)
        demo_mode: Whether to run in demo mode
        logging_level: Logging level for file output
        logging_level_stdout: Logging level for stdout
        ignore_dependencies: Whether to ignore task dependencies
        
    Returns:
        List of experiment arguments for each task in the benchmark
    """
    env_args_list = benchmark.env_args_list
    exp_args_list = []

    for env_args in env_args_list: 
            exp_args = None
            if config == 'CP':
                multi_agent_args.controller_args.set_benchmark(benchmark, demo_mode)
                exp_args = MultiAgentExpArgsCP(
                    agents_dict={
                        'PLANNER': multi_agent_args.planner_args,
                        'CONTROLLER': multi_agent_args.controller_args
                    },
                    env_args=env_args,
                    logging_level=logging_level
                )

            elif config == 'CPFixed':
                multi_agent_args.controller_args.set_benchmark(benchmark, demo_mode)
                exp_args = MultiAgentExpArgsCPfixed(
                    agents_dict={
                        'PLANNER': multi_agent_args.planner_args,
                        'CONTROLLER': multi_agent_args.controller_args
                    },
                    env_args=env_args,
                    logging_level=logging_level
                )
                
            elif config == 'CPO':
                multi_agent_args.controller_args.set_benchmark(benchmark, demo_mode)
                exp_args = MultiAgentExpArgsCPO(
                    agents_dict={
                        'OBSERVER': multi_agent_args.observer_args,
                        'PLANNER': multi_agent_args.planner_args,
                        'CONTROLLER': multi_agent_args.controller_args
                    },
                    env_args=env_args,
                    logging_level=logging_level
                )

            else:
                single_agent_args.set_benchmark(benchmark, demo_mode)
                exp_args = ExpArgs(
                    agent_args=single_agent_args,
                    env_args=env_args,
                    logging_level=logging_level,
                )      

            exp_args_list.append(exp_args)

    for i, exp_args in enumerate(exp_args_list):
        exp_args.order = i

    if not ignore_dependencies:
        # Populate the depends_on field based on the task dependencies in the benchmark
        exp_args_list = add_dependencies(exp_args_list, benchmark.dependency_graph_over_tasks())
    else:
        logger.warning(
            f"Ignoring dependencies for benchmark {benchmark.name}. This could lead to different results."
        )
    
    return exp_args_list
    


        
