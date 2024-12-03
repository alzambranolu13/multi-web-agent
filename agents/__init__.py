from dataclasses import dataclass
from agentlab.agents.agent_args import AgentArgs

@dataclass
class MultiAgentArgs:
    planner_args: AgentArgs
    controller_args: AgentArgs
    observer_args: AgentArgs = None