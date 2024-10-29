
from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.generic_agent.generic_agent_prompt import MainPrompt, GenericPromptFlags
from agentlab.agents.dynamic_prompting import SystemPrompt, GoalInstructions

           
class MyMainPrompt(MainPrompt):
      def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, goal: str):
        super().__init__(action_set, obs_history,actions,memories,thoughts,previous_plan,step,flags)
        self.instructions = GoalInstructions(goal, extra_instructions=flags.extra_instructions)

     

     
        