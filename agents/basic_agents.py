from agentlab.agents.most_basic_agent.most_basic_agent import MostBasicAgent, MostBasicAgentArgs
from browsergym.experiments.agent import Agent, AgentInfo
from typing import TYPE_CHECKING, Any
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from agentlab.llm.llm_utils import ParseError, extract_code_blocks, retry_raise
from dataclasses import asdict, dataclass
from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.dynamic_prompting import ActionFlags, ActionPrompt, Observation, ObsFlags, fit_tokens
import re
from agentlab.llm.llm_utils import parse_html_tags_raise, image_to_jpg_base64_url

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

    def get_action(self, obs: Any, feedback) -> tuple[str, dict]:
        #obs.shrink()
        obs = Observation(obs,ObsFlags())
        obs_prompt = fit_tokens(obs,100000)
        system_prompt = f"""
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. 
Your task as the Observer Agent is to provide the relevant elements presented in the current page to our Planner Agent. 
There's a Big Brother agent which will supervise your answers please take into account it's feedback.
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

    def add_screenshot(self, prompt, screenshot):
        if isinstance(prompt, str):
            prompt = [{"type": "text", "text": prompt}]

        img_url = image_to_jpg_base64_url(screenshot)
        prompt.append(
            {
                "type": "image_url",
                "image_url": {"url": img_url, "detail": "auto"},
            }
        )
        return prompt

    def get_action(self, obs: dict, last_steps: str) -> tuple[str, dict]:

        system_prompt = f"""
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
as the Planner is to figure out the different steps required to complete a certain goal. You have a screenshot of the state of the page as well as the steps executed and feedback from the Controller agent (which executes the actions).
"""
#There's a Big Brother agent which will supervise your answers please take into account it's feedback.        
        


        prompt = f"""
Based on the screenshot create a very highlevel plan with intermediate subgoals to achieve the user's goal. Provide a chain of thought/reasoning to your answer.

Here are some examples of what is your expected behavior:

-Example 0
If the goal is "Open New York Times page" \n

Your answer should be:
<plan>
1. Open New York Times page
</plan>
<thought>
Reasoning for the plan
</thought>

-Example 1

If the goal is "Find a silver Rolex for men priced between $13,000 and $15,000 on eBay"

Your answer should be:
<plan>
1. Open the eBay website.
2. Search for men’s watches.
3. Filter results by the Rolex brand.
4. Apply color filter to grey
5. Apply price filter from 13,000 to 15,000
6. Pick first watch that appears after filtering 
5. Provide the results to the user
</plan>
<thought>
Reasoning for the plan
</thought>

-Example 2

If the goal is "Retrieve the second section of the first article related to 'Trading for beginners' on Investopedia"

Your answer should be:
<plan>
1. Open the Investopedia website.
2. Search for articles on ”Trading for beginners.”
3. Review the first three articles.
4. Open the first article.
5. Retrieve and provide the content of the second section to user.
</plan>
<thought>
Reasoning for the plan
</thought>


-Example 3
If the goal is "Get me the amount of views in the most trending video right now on Youtube"

Your answer should be:
<plan>
1. Open Youtube
2. Click on Trending
3. Rertrieve the total number of views in the first video
</plan>
<thought>
Reasoning for the plan
</thought>


End of examples.

The user's goal is: {obs['goal']}

You have executed succesfully the following actions: {last_steps}

And you hou have the screenshot of the current state of the page. Provide the plan

If the goal is complete please return an empty plan.

"""   
        prompt = self.add_screenshot(prompt, obs['screenshot'])

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]

        def parser(response: str) -> tuple[dict, bool, str]:
            blocks= parse_html_tags_raise(response, keys=('plan','thought'))
            if len(blocks) == 0:
                raise ParseError("No code block found in the response")
            pattern = re.compile(r"[0-9]\..*\n")
            steps = pattern.findall(blocks['plan'])
            if len(steps)== 0:
                pattern = re.compile(r"[0-9]\..*.")
                steps = pattern.findall(blocks['plan'])
            steps = [step.split('.')[1] for step in steps]
            answer= {'steps':steps, 'thought': blocks['thought']}
            return answer

        ans_dict = retry_raise(self.chat, messages, n_retry=3, parser=parser)

        return ans_dict.get('steps',0)
    
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
There's a Big Brother agent which will supervise your answers please take into account it's feedback.
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
    

class BrotherAgentArg(MostBasicAgentArgs):
    agent_name: str = "BasicAgent"
    temperature: float = 0.1
    use_chain_of_thought: bool = True
    chat_model_args: "BaseModelArgs" = None

    def make_agent(self) -> Agent:
        return BrotherAgent(
            temperature=self.temperature,
            use_chain_of_thought=self.use_chain_of_thought,
            chat_model_args=self.chat_model_args,
        )

    def prepare(self):
        return self.chat_model_args.prepare_server()

    def close(self):
        return self.chat_model_args.close_server()
    
class BrotherAgent(MostBasicAgent):
    def __init__(self, temperature: float, use_chain_of_thought: bool, chat_model_args: "BaseModelArgs"):
        super().__init__(temperature, use_chain_of_thought, chat_model_args)

    def add_screenshot(self, prompt, screenshot):
        if isinstance(prompt, str):
            prompt = [{"type": "text", "text": prompt}]

        img_url = image_to_jpg_base64_url(screenshot)
        prompt.append(
            {
                "type": "image_url",
                "image_url": {"url": img_url, "detail": "auto"},
            }
        )
        return prompt

    def get_action(self, obs_before, obs_after, action) -> tuple[str, dict]:
        #observation = Observation(obs,ObsFlags())
        #obs_prompt = fit_tokens(observation,100000)
        system_prompt = f"""
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your task
as the Big Brother Agent is to supervise that the actions taken are correct and that they contribute in achieving the goal.
"""
            
        prompt1 = f"""
Compare the before and after state of the page to ensure if the action expected was executed correctly. Give a chain of thought of your judgement.
"""   

        prompt2 = self.add_screenshot("This screenshot is before the action was executed",obs_before['screenshot'])

        prompt3 =self.add_screenshot("This screenshot is after the action was executed",obs_after['screenshot'])
        #prompt.append(self.add_screenshot("This screenshot is after the actions",obs_after['screenshot']))

        prompt4=f"""
The action taken by the Controller was {action}

Give your answer in the following format:
<feedback>
Feedback about the action taken by the controller
</feedback>

<thought>
Your chain of thought or reasoning
</thought>

"""  

        

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt1), HumanMessage(content=prompt2),HumanMessage(content=prompt3), HumanMessage(content=prompt4) ]

        #messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt2) ]

        def parser(response: str) -> tuple[dict, bool, str]:
            blocks= parse_html_tags_raise(response, keys=('feedback','thought'))
            if len(blocks) == 0:
                raise ParseError("No code block found in the response")
            return blocks

        ans_dict = retry_raise(self.chat, messages, n_retry=3, parser=parser)

        return ans_dict

        
    