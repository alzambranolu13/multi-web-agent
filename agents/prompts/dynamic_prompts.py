
from browsergym.core.action.base import AbstractActionSet
from agentlab.agents.generic_agent.generic_agent_prompt import MainPrompt, GenericPromptFlags
from agents.prompts.prompts import UniversalGoalInstructions
from agentlab.agents.dynamic_prompting import SystemPrompt, GoalInstructions


class ObserverPrompt():
    def __init__(self, obs: str) -> None:
        self.prompt= f"""
#The Observer agent found this list  of elements the  most relevant to achieve the user's goal
{obs}
"""


           
class MyMainPrompt(MainPrompt):
      def __init__(self, action_set: AbstractActionSet, obs_history: list[dict], actions: list[str], memories: list[str], thoughts: list[str], previous_plan: str, step: int, flags: GenericPromptFlags, goal: str):
        super().__init__(action_set, obs_history,actions,memories,thoughts,previous_plan,step,flags)
        self.instructions = GoalInstructions(goal, extra_instructions=flags.extra_instructions)

      @property
      def _prompt(self) -> str:
        prompt = f"""\
{self.instructions.prompt}\
{self.obs.prompt}\
{self.history.prompt}\
{self.action_prompt.prompt}\
{self.hints.prompt}\
{self.be_cautious.prompt}\
{self.think.prompt}\
{self.plan.prompt}\
{self.memory.prompt}\
{self.criticise.prompt}\
"""

        if self.flags.use_abstract_example:
            prompt += f"""
# Abstract Example

Here is an abstract version of the answer with description of the content of
each tag. Make sure you follow this structure, but replace the content with your
answer:
{self.think.abstract_ex}\
{self.plan.abstract_ex}\
{self.memory.abstract_ex}\
{self.criticise.abstract_ex}\
{self.action_prompt.abstract_ex}\
"""

        if self.flags.use_concrete_example:
            prompt += f"""
# Concrete Example

Here is a concrete example of how to format your answer.
Make sure to follow the template with proper tags:
{self.think.concrete_ex}\
{self.plan.concrete_ex}\
{self.memory.concrete_ex}\
{self.criticise.concrete_ex}\
{self.action_prompt.concrete_ex}\
"""
        return prompt
      


     
        