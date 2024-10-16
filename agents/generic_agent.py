from dataclasses import asdict, dataclass
from functools import partial
from warnings import warn

from browsergym.experiments.agent import Agent
from langchain.schema import HumanMessage, SystemMessage

from agentlab.agents import dynamic_prompting as dp
from agentlab.agents.agent_args import AgentArgs
from agentlab.agents.utils import openai_monitored_agent
from agentlab.llm.chat_api import BaseModelArgs
from agentlab.llm.llm_utils import RetryError, retry_raise
from agentlab.llm.tracking import cost_tracker_decorator
from agentlab.experiments.launch_exp import import_object

from agentlab.agents.generic_agent.generic_agent_prompt import GenericPromptFlags, MainPrompt
from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs, GenericAgent
import agents.agent_config as agent_config
from agents.prompts.dynamic_prompts import MyMainPrompt
from agents.prompts.prompts import ObsGoalInstructions
from agentlab.agents.dynamic_prompting import  GoalInstructions



@dataclass
class MyGenericAgentArgs(GenericAgentArgs):
    def __init__(self, chat_model_args, flags ):
        super().__init__(chat_model_args=chat_model_args, flags=flags)
        max_retry: int = 4
    
    def make_agent(self,system_prompt: dp.SystemPrompt, goal_prompt: GoalInstructions):
        return MyGenericAgent(
            chat_model_args=self.chat_model_args, flags=self.flags, max_retry=self.max_retry,system_prompt= system_prompt,goal_prompt=goal_prompt
        )


class MyGenericAgent(GenericAgent):
    def __init__(self,chat_model_args, flags, max_retry , system_prompt: dp.SystemPrompt, goal_prompt: GoalInstructions ):
        super().__init__(chat_model_args=chat_model_args, flags=flags, max_retry=max_retry )
        self.system_prompt = system_prompt
        self.goal_prompt = goal_prompt
    
    def set_goal(self,goal: str):
        self.goal_prompt.add_goal(goal)
 
    def get_action(self,obs, elements:str):
        self.obs_history.append(obs)
        goal = self.obs_history[-1]["goal"]   
        self.set_goal(goal) 
        main_prompt = MyMainPrompt(
            action_set=self.action_set,
            obs_history=self.obs_history,
            actions=self.actions,
            memories=self.memories,
            thoughts=self.thoughts,
            previous_plan=self.plan,
            step=self.plan_step,
            flags=self.flags,
            instructions= self.goal_prompt,
            elements= elements   
        )
        # main_prompt = MainPrompt(
        #     action_set=self.action_set,
        #     obs_history=self.obs_history,
        #     actions=self.actions,
        #     memories=self.memories,
        #     thoughts=self.thoughts,
        #     previous_plan=self.plan,
        #     step=self.plan_step,
        #     flags=self.flags,
        # )

        max_prompt_tokens, max_trunc_itr = self._get_maxes()

        system_prompt = self.system_prompt._prompt

        prompt = dp.fit_tokens(
            shrinkable=main_prompt,
            max_prompt_tokens=max_prompt_tokens,
            model_name=self.chat_model_args.model_name,
            max_iterations=max_trunc_itr,
            additional_prompts=system_prompt,
        )

        stats = {}
        try:
            # TODO, we would need to further shrink the prompt if the retry
            # cause it to be too long

            chat_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ]
            ans_dict = retry_raise(
                self.chat_llm,
                chat_messages,
                n_retry=self.max_retry,
                parser=main_prompt._parse_answer,
            )
            # inferring the number of retries, TODO: make this less hacky
            stats["n_retry"] = (len(chat_messages) - 3) / 2
            stats["busted_retry"] = 0
        except RetryError as e:
            ans_dict = {"action": None}
            stats["busted_retry"] = 1

            stats["n_retry"] = self.max_retry + 1

        self.plan = ans_dict.get("plan", self.plan)
        self.plan_step = ans_dict.get("step", self.plan_step)
        self.actions.append(ans_dict["action"])
        self.memories.append(ans_dict.get("memory", None))
        self.thoughts.append(ans_dict.get("think", None))

        agent_info = dict(
            think=ans_dict.get("think", None),
            chat_messages=chat_messages,
            stats=stats,
            extra_info={"chat_model_args": asdict(self.chat_model_args)},
        )
        return ans_dict["action"], agent_info
  

        

