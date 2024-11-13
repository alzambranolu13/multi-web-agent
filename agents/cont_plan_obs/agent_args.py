from typing import TYPE_CHECKING, Any
from agentlab.agents.most_basic_agent.most_basic_agent import  MostBasicAgentArgs
from browsergym.experiments.agent import Agent 

from .agents import ObserverAgent,PlannerAgent, ControllerAgent

if TYPE_CHECKING:
    from agentlab.llm.chat_api import BaseModelArgs

class ObserverAgentArgs(MostBasicAgentArgs):
    agent_name: str = "BasicAgent"
    temperature: float = 0.2
    use_chain_of_thought: bool = False
    chat_model_args: "BaseModelArgs" = None

    def make_agent(self) -> Agent:
        return ObserverAgent(
            temperature=self.temperature,
            use_chain_of_thought=self.use_chain_of_thought,
            chat_model_args=self.chat_model_args,
        )
    

class PlannerAgentArg(MostBasicAgentArgs):
    agent_name: str = "BasicAgent"
    temperature: float = 0.2
    use_chain_of_thought: bool = False
    chat_model_args: "BaseModelArgs" = None

    def make_agent(self) -> Agent:
        return PlannerAgent(
            temperature=self.temperature,
            use_chain_of_thought=self.use_chain_of_thought,
            chat_model_args=self.chat_model_args,
        )

class ContAgentArg(MostBasicAgentArgs):
    agent_name: str = "BasicAgent"
    temperature: float = 0.1
    use_chain_of_thought: bool = False
    chat_model_args: "BaseModelArgs" = None

    def make_agent(self) -> Agent:
        return ControllerAgent(
            temperature=self.temperature,
            use_chain_of_thought=self.use_chain_of_thought,
            chat_model_args=self.chat_model_args,
        )


