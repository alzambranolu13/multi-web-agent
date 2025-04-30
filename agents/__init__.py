from dataclasses import dataclass
from agentlab.agents.agent_args import AgentArgs
from .cont_plan_obs import *
from .planner_controller import *

@dataclass
class MultiAgentArgs:
    planner_args: AgentArgs
    controller_args: AgentArgs
    observer_args: AgentArgs = None