import time

from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.generic_agent.generic_agent_prompt import MainPrompt, GenericPromptFlags
from agentlab.agents import dynamic_prompting as dp


           
# class MyMainPrompt(MainPrompt):
#       def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, goal: str):
#         super().__init__(action_set=action_set, obs_history=obs_history,actions=actions,memories=memories,thoughts=thoughts,previous_plan=previous_plan,step=step,flags=flags)    
#         goal_object= ({'type': 'text', 'text': goal},)
#         self.instructions= GoalInstructions(goal_object=goal_object, extra_instructions=flags.extra_instructions)
        


     
class MyMainPrompt(MainPrompt):
      def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, plan: str):
        extra_instructions = f"""    
## Global Plan
The Global Plan is a structured, step-by-step plan that provides you with a
roadmap to complete the web task. Each step in the Global Plan contains a 
high-level action that you need to take. Since this Global Plan
encapsulates the entire task flow, you should identify where you are in the
plan by referring to the previous action trajectory and the current
observation, and then decide on the next action to take, please make sure to add this in your thought. Here is the Global
Plan for the task:
{plan}

## Extra Instruction
{flags.extra_instructions}
"""
        super().__init__(action_set=action_set, obs_history=obs_history,actions=actions,memories=memories,thoughts=thoughts,previous_plan=previous_plan,step=step,flags=flags)    
        self.think = ControllerThink(visible=lambda: flags.use_thinking)
        self.instructions = ControllerChatInstructions(
            obs_history[-1]["chat_messages"], extra_instructions=extra_instructions)




class ControllerSystemPrompt(dp.PromptElement):
    _prompt = """\
Review the current state of the page and all other information to find the best possible next action to accomplish your goal. 
Your answer will be interpreted and executed by a program, so make sure to follow the formatting instructions. 
Throughout execution, reflect on your state with reference to the Global Plan before determining your next action."""


class ControllerThink(dp.PromptElement):
    _prompt = ""

    _abstract_ex = """
<think>
Think step by step. Consider where you are in the provided global plan. If you need to make calculations such as coordinates, write them here. Describe the effect 
that your previous action had on the current content of the page.
</think>
"""
    _concrete_ex = """
<think>
Following the global plan, I need to ensure that I have the correct year selected. 
In my previous action, I tried to set the value of year to "2022", using select_option, but it doesn't appear to be in the form. It may be a
dynamic dropdown, I will try using click with the bid "a324" and look at the response from the page.
</think>
"""


class ControllerChatInstructions(dp.PromptElement):
    def __init__(self, chat_messages, visible: bool = True, extra_instructions=None) -> None:
        super().__init__(visible)
        self._prompt = f"""\
# Instructions

You are a UI Assistant, your goal is to help the user perform tasks using a web browser. You can
communicate with the user via a chat, in which the user gives you instructions and in which you
can send back messages. You have access to a web browser that both you and the user can see,
and with which only you can interact via specific commands.

Review the instructions from the user, the current state of the page and all other information
to find the best possible next action to accomplish your goal. Your answer will be interpreted
and executed by a program, make sure to follow the formatting instructions.

## Chat messages:

"""
        self._prompt += "\n".join(
            [
                f"""\
 - [{msg['role']}] UTC Time: {time.asctime(time.gmtime(msg['timestamp']))} - Local Time: {time.asctime(time.localtime(msg['timestamp']))} - {msg['message']}"""
                for msg in chat_messages
            ]
        )

        if extra_instructions:
            self._prompt += f"""

{extra_instructions}
"""



     
        