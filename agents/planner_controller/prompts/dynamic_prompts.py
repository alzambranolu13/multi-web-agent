
from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.generic_agent.generic_agent_prompt import MainPrompt, GenericPromptFlags
from agentlab.agents.dynamic_prompting import SystemPrompt, GoalInstructions

           
class MyMainPrompt(MainPrompt):
      def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, goal: str):
        super().__init__(action_set=action_set, obs_history=obs_history,actions=actions,memories=memories,thoughts=thoughts,previous_plan=previous_plan,step=step,flags=flags)    
        goal_object= ({'type': 'text', 'text': goal},)
        self.instructions= GoalInstructions(goal_object=goal_object)
        


     

     
        