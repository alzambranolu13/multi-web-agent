
from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.generic_agent.generic_agent_prompt import MainPrompt, GenericPromptFlags
from agentlab.agents.dynamic_prompting import SystemPrompt, GoalInstructions

           
# class MyMainPrompt(MainPrompt):
#       def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, goal: str):
#         super().__init__(action_set=action_set, obs_history=obs_history,actions=actions,memories=memories,thoughts=thoughts,previous_plan=previous_plan,step=step,flags=flags)    
#         goal_object= ({'type': 'text', 'text': goal},)
#         self.instructions= GoalInstructions(goal_object=goal_object, extra_instructions=flags.extra_instructions)
        


     
class MyMainPrompt(MainPrompt):
      def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, plan: str):
        flags.extra_instructions = f"""    
## Global Plan
The Global Plan is a structured, step-by-step plan that provides you with a
roadmap to complete the web task. Each step in the Global Plan contains a 
high-level action that you need to take. Since this Global Plan
encapsulates the entire task flow, you should identify where you are in the
plan by referring to the previous action trajectory and the current
observation, and then decide on the next action to take, please make sure to add this in your thought. Here is the Global
Plan for the task:
{plan}
"""
        super().__init__(action_set=action_set, obs_history=obs_history,actions=actions,memories=memories,thoughts=thoughts,previous_plan=previous_plan,step=step,flags=flags)    




     
        