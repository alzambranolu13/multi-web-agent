from agentlab.agents.dynamic_prompting import SystemPrompt, GoalInstructions
import time

class ObsSystemPrompt(SystemPrompt):
    def __init__(self, extra_instructions=None) -> None:
        #super().__init__(chat_messages, visible, extra_instructions)
        self._prompt = f"""\
# Instructions
You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. 
Your task as the Observer Agent is to provide the relevant elements presented in the current page to our Planner Agent.
"""
        
class DescSystemPrompt(SystemPrompt):
    def __init__(self, extra_instructions=None) -> None:
        #super().__init__(chat_messages, visible, extra_instructions)
        self._prompt = f"""\
# Instructions
 You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser.
Your task as the Controller agent is to communicate with the user via a chat, in which the user gives you instructions and in which you
can send back messages. You have access to a web browser that both you and the user can see,
and with which only you can interact via specific commands.

Review the instructions from the user, the current state of the page (which is given to you by the Observer agent) and all other information
to find the best possible next action to accomplish your goal. Your answer will be interpreted
and executed by a program, make sure to follow the formatting instructions.
"""

class PlanSystemPrompt(SystemPrompt):
    def __init__(self, chat_messages, visible: bool = True, extra_instructions=None) -> None:
        super().__init__(chat_messages, visible, extra_instructions)

        self._prompt = f"""\
        # Instructions
  
        You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
        as the Planner is to figure out the different steps required to complete a certain goal. You have information about the observed elements 
        in the page, given to you by the Observer (which is another agent of the collection),past actions, chat messages and feedback from 
        the Controller agent (which is another agent of the collection). 
    

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

        ## Extra instructions:

        {extra_instructions}
        """


class ContSystemPrompt(SystemPrompt): 
    def __init__(self, chat_messages, visible: bool = True, extra_instructions=None) -> None:
        super().__init__(chat_messages, visible, extra_instructions)
        self._prompt = f"""\
        # Instructions

        You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
        as the Controller is to take a step required from the Planner (which is an agent of the connection) and return an action to take in the browser.

        The information provided to you as the controller is a step of the plan and information about the current web page. With this
        information you need to return the action in a specific format, you will also have to give feedback of wether the action taken completed the step
        given by the controller or not.
        ## Chat messages:

        """

        if extra_instructions:
                    self._prompt += f"""

        ## Extra instructions:

        {extra_instructions}
        """


class ObsGoalInstructions(GoalInstructions):
    def __init__(self, visible: bool = True, extra_instructions=None) -> None:
         super().__init__( None,visible, extra_instructions)
         self._prompt = f"""
# Instructions
Review the current state of the page and retrieve the top elements in the page that can contribute in achieving the goal. 
Your answer will be interpreted and executed by a program, make sure to follow the formatting instructions. You will return the important elements
found in the page as a list of "actions" , for example:

<action> button search clickable </action>
<action> link about clickable  </action>
<action> image 1.jpg visible </action>




"""
         
    def add_goal(self,goal: str, extra_instructions= None):
        self._prompt+= f"""
## Goal:
{goal}
"""
        if extra_instructions:
                self._prompt += f"""
## Extra instructions:
{extra_instructions}
"""

      
      
class PlanGoalInstructions(GoalInstructions):
    def __init__(self, goal:str , visible: bool = True, extra_instructions=None) -> None:
         super().__init__(goal, visible, extra_instructions)
         self._prompt = f"""
# Instructions
The goal is for you create a plan, after creating the plan provide the Controller agent with the step required, the controller will give you
feedback on wether the step was accomplished or not successfully, you can decide analyzing the feedback wether is best to continue with the next 
step, rollback to a previous step or decompose the plan even more. Please return the plan as a list separated by the character ``` like the following:

```
click search bar
```
type in ebay
```
click search
```
"""

    def add_goal(self,goal: str, extra_instructions= None):
        self._prompt+= f"""
## Goal:
{goal}
"""
        if extra_instructions:
                self._prompt += f"""
## Extra instructions:
{extra_instructions}
"""
            
class ContGoalInstructions(GoalInstructions):
    def __init__(self, goal:str=None , visible: bool = True, extra_instructions=None) -> None:
         super().__init__(goal, visible, extra_instructions)
#          self._prompt = f"""
# # Instructions
# Review the elements provided by the Observer agent and create a plan to complete the goal.
# Format this as a enumerated list of steps separated with ```, like the following

# ```
# 1. Click on search bar
# ```
# 2. Type "open Youtube"
# ```
# 3. Click on search
# ```
# etc
         self._prompt = f"""         
You are a UI Assistant, your goal is to help the user perform tasks using a web browser. You can
communicate with the user via a chat, in which the user gives you instructions and in which you
can send back messages. You have access to a web browser that both you and the user can see,
and with which only you can interact via specific commands.

Review the instructions from the user, the current state of the page and all other information
to find the best possible next action to accomplish your goal. Your answer will be interpreted
and executed by a program, make sure to follow the formatting instructions.

"""

    def add_goal(self,goal: str, extra_instructions= None):
        self._prompt+= f"""
## The user's goal is:
{goal}
"""
        if extra_instructions:
                self._prompt += f"""
## Extra instructions:
{extra_instructions}
"""

class UniversalGoalInstructions(GoalInstructions):
    def __init__(self, instructions: str, goal:str , visible: bool = True, extra_instructions=None) -> None:
        super().__init__(goal, visible, extra_instructions)
        self._prompt = f"""
# Instructions
{instructions}
## Goal:
{goal}
"""
        if extra_instructions:
            self._prompt += f"""
## Extra instructions:

{extra_instructions}
"""


    