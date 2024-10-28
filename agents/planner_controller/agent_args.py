from typing import TYPE_CHECKING, Any

from agentlab.agents.most_basic_agent.most_basic_agent import  MostBasicAgentArgs
from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs
from agents.planner_controller.agents import PlannerAgent, ControllerAgent
from browsergym.experiments.agent import Agent 

if TYPE_CHECKING:
    from agentlab.llm.chat_api import BaseModelArgs




class PlannerAgentArg(MostBasicAgentArgs):
    agent_name: str = "PlannerAgent"
    temperature: float = 0.1
    use_chain_of_thought: bool = False
    chat_model_args: "BaseModelArgs" = None

    def make_agent(self) -> Agent:
        return PlannerAgent(
            temperature=self.temperature,
            use_chain_of_thought=self.use_chain_of_thought,
            chat_model_args=self.chat_model_args,
        )

class ControllerAgentArgs(GenericAgentArgs):
    def __init__(self, chat_model_args, flags ):
        super().__init__(chat_model_args=chat_model_args, flags=flags)
        #self.temperature= 0.1
    
    def __post_init__(self):
        self.agent_type = "Planner-Controller" # change to PlannerController, CPO, etc.
        try:  # some attributes might be temporarily args.CrossProd for hyperparameter generation
            self.agent_name = f"{self.agent_type}-{self.chat_model_args.model_name}".replace("/", "_")
        except AttributeError:
            pass
    
    def make_agent(self):
        return ControllerAgent(
            chat_model_args=self.chat_model_args, flags=self.flags, max_retry=self.max_retry
        )

