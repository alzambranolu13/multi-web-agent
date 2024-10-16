from agentlab.agents.most_basic_agent.most_basic_agent import MostBasicAgent, MostBasicAgentArgs
from browsergym.experiments.agent import Agent, AgentInfo
from typing import TYPE_CHECKING, Any
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from agentlab.llm.llm_utils import ParseError, extract_code_blocks, retry_raise
from dataclasses import asdict, dataclass
from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.dynamic_prompting import ActionFlags, ActionPrompt, Observation, ObsFlags, fit_tokens
import re

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

    def prepare(self):
        return self.chat_model_args.prepare_server()

    def close(self):
        return self.chat_model_args.close_server()

class ObserverAgent(MostBasicAgent):
    def __init__(self, temperature: float, use_chain_of_thought: bool, chat_model_args: "BaseModelArgs"):
        super().__init__(temperature, use_chain_of_thought, chat_model_args)

    def get_action(self, obs: Any) -> tuple[str, dict]:
        #obs.shrink()
        obs = Observation(obs,ObsFlags())
        obs_prompt = fit_tokens(obs,100000)
        system_prompt = f"""
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. 
Your task as the Observer Agent is to provide the relevant elements presented in the current page to our Planner Agent.
"""
        prompt = f"""
Review the current state of the page and retrieve the top elements sorted by relevance.
You will return the important elements found in the page as a list of elements separated by ``` each element has the format '[bid] type "value", clickable, visible'. Here is an example of the format:

```
[bid] link 'About', clickable, visible
```
[bid] combobox 'Search', visible, autocomplete='both', hasPopup='listbox', expanded=False, controls='Alh6id'
```
and so on.

Your answer will be interpreted and executed by a program, MAKE SURE to follow the formatting instructions. 

The user's goal is: {obs.obs['goal']}

{obs_prompt}

"""

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]

        def parser(response: str) -> tuple[dict, bool, str]:
            blocks = extract_code_blocks(response)
            if len(blocks) == 0:
                raise ParseError("No code block found in the response")
            elements = [block[1] for block in blocks]
            return {"elements": elements}

        ans_dict = retry_raise(self.chat, messages, n_retry=3, parser=parser)

        elements = ans_dict.get("elements", None)

        return elements
        
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

    def prepare(self):
        return self.chat_model_args.prepare_server()

    def close(self):
        return self.chat_model_args.close_server()
            
class PlannerAgent(MostBasicAgent):
    def __init__(self, temperature: float, use_chain_of_thought: bool, chat_model_args: "BaseModelArgs"):
        super().__init__(temperature, use_chain_of_thought, chat_model_args)

    def get_action(self, elements:str, goal:str, last_step: str, previous_plan:str) -> tuple[str, dict]:

        system_prompt = f"""
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
as the Planner is to figure out the different steps required to complete a certain goal. You have information about the observed elements 
in the page, given to you by the Observer (which is another agent of the collection),past actions, chat messages and feedback from 
the Controller agent (which is another agent of the collection). 
"""
        


        prompt = f"""
Based on the elements provided by the pbserver provide a multi step plan that will guide you to accomplish the goal. There
should always be steps to verify if the previous action had an effect. The plan
can be revisited at each steps. Specifically, if there was something unexpected.
The plan should be cautious and favor exploring befor submitting.

Your answer have to follow a list format like the following "step_number. instruction, bid [##]":

1.click search bar, bid [94]
2.type "lorem ipsum", bid [94]
3.click on first link, bid [220]

You just executed step {last_step} of the previously proposed plan:\n{previous_plan}\n
After reviewing the effect of your previous actions, verify if your plan is still
relevant and update it if necessary, make sure to NOT repeat the last action.
If goal has been reached return done.

The user's goal is: {goal}

The Observer agent found this list  of elements the  most relevant to achieve the user's goal, base your actions on these elements:
{elements}
"""   

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]

        def parser(response: str) -> tuple[dict, bool, str]:
            pattern = re.compile(r"[0-9]\..*\n")
            blocks = pattern.findall(response)
            if len(blocks) == 0:
                raise ParseError("No code block found in the response")
            elements= [block.split('. ')[1] for block in blocks]
            return {"elements": elements}

        ans_dict = retry_raise(self.chat, messages, n_retry=3, parser=parser)

        elements = ans_dict.get("elements", None)

        return elements
    
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

    def prepare(self):
        return self.chat_model_args.prepare_server()

    def close(self):
        return self.chat_model_args.close_server()
    
class ControllerAgent(MostBasicAgent):
    def __init__(self, temperature: float, use_chain_of_thought: bool, chat_model_args: "BaseModelArgs"):
        super().__init__(temperature, use_chain_of_thought, chat_model_args)


    def get_action(self, action: str) -> tuple[str, dict]:
        system_prompt = f"""
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
as the Controller is to execute the last order from the planner picking from a set of actions you can execute.
"""
        prompt = f"""
You can interact with the environment using the following actions:
{self.action_set.describe(with_long_description=False)}

You must return which action follows the order given by the Planner, bid will help you keep track of the elemts

The action you provide must be in between triple ticks.
Here is an example of how to use the bid action:

```
click('a314')
```

Here is the order given by the Planner: {action}
"""   

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]

        def parser(response: str) -> tuple[dict, bool, str]:
            blocks = extract_code_blocks(response)
            if len(blocks) == 0:
                raise ParseError("No code block found in the response")
            actions = [block[1] for block in blocks]
            return {"actions": actions}

        ans_dict = retry_raise(self.chat, messages, n_retry=3, parser=parser)

        actions = ans_dict.get("actions", None)

        return (
            actions,
            AgentInfo(
                think=None,
                chat_messages=messages,
                # put any stats that you care about as long as it is a number or a dict of numbers
                stats={"prompt_length": len(prompt), "response_length": 0},
                markup_page="Add any txt information here, including base 64 images, to display in xray",
                extra_info={"chat_model_args": asdict(self.chat_model_args)},
            ),
        )
    