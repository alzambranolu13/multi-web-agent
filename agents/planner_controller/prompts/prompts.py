import os
from os import listdir
from os.path import isfile, isdir, join


PROMPT_DIR = os. getcwd()+'/agents/planner_controller/prompts/docs'

#example_types can only be 'webarena', 'open_ended', 'amazon', 'ebay', 'encyclopedia', 'reddit', 'wikipedia'
class PlannerPrompt():
    def __init__(self , example_types:str | list= 'webarena', goal= None, use_previous_plan:bool = False ,use_failed_steps:bool = False, use_completed_steps: bool = True, last_steps=[], steps_failed=[],previous_plan:str= None):
        self.system_prompt= f"""
    You are part of a collection of Web Agents Planner-Controller which goal is to help the user perform tasks using a web browser. The Planner creates a plan to achieve the goal and the Controller interacts with the environment to follow the steps of the plan. 
    Your tasks as the Planner is to figure out the different steps required to complete a certain goal. You are an expert in navigating the internet and any web page possible.
    You have a screenshot of the state of the page as well as the steps executed.
    """
        examples= None
        if isinstance(example_types,str):
            if example_types=='all':
                examples = get_all_examples()
            else:
                examples = get_examples_dir([example_types])
        else:
            examples = get_examples_dir(example_types)


        self.prompt= f"""
Based on the screenshot create a very highlevel plan with intermediate subgoals to achieve the user's final goal. Provide a chain of thought/reasoning of your answer.
Put a high importance on the screenshot, this will help you decide on wether keeping the plan or updating the plan. Avoid any repetition of steps, if the screenshot crearly proves a step being completed don't include it in the plan.

In your thought add the reason of every step and how it relates to the goal.

Remember you are only a planner you don't have to determine wether the goal has been achieved or not, this will be determined by the controller.

Here are some examples of what is your expected behavior, feel free to reuse this plans if you see a similar goal:

""" 
        for example in examples:
            self.prompt+=example

        self.prompt+= f"""End of examples.

Make sure to give your answer in the expected format.

Providing information to the user must always be the last step, this is because we can only provide information to the user one time. So make sure to first gather all the information needed and only include ONE providing step at the end.

Note the Controller Agent can observe the page same as you so avoid steps that include "Identify" if the information is already displayed.
Simple and short plans are rewarded so avoid unrequired steps.

The user's goal is: {goal}

"""
        if use_completed_steps and len(last_steps)!= 0:
            self.prompt+=f"""
This steps have been succesfully executed: {last_steps} 
It's essential to not repeat completed steps. If a step is mentioned here DO NOT included in the plan again
"""
#(disclaimer: even if this is empty it doesn't mean no actions have been succesful)           
        if use_previous_plan and previous_plan!= None:
            self.prompt+=f"""
Your previous plan was {previous_plan}
Only make changes to the original plan if it's completely necessary to achieve goal.
"""
        if (use_failed_steps):
            self.prompt+=f"""
These steps have failed to be exectued: {steps_failed} 
Please adequate your plan to achieve the failed steps
"""        

        self.prompt+="""
If all the steps have been completed succesfully return an empty plan. 
"""

            
#Please create a more decomposed plan in order to complete the failed steps.


def get_all_examples():
    onlydirs = [f for f in listdir(PROMPT_DIR) if isdir(join(PROMPT_DIR, f))]
    examples= []
    for dir in onlydirs:
        examples+=get_examples_dir(dir)

    return examples

def get_examples_dir(example_types, max_examples=5):
    examples=[]
    for example_type in example_types:
        pwd= f'{PROMPT_DIR}/{example_type}/'
        onlyfiles = [f for f in listdir(pwd) if isfile(join(pwd, f))]
        len_mes= max(int((len(onlyfiles))/2), max_examples)

        for i in range(len_mes):
            goal = open(f'{pwd}question{i}.txt', "r").read()  
            steps = open(f'{pwd}answer{i}.txt', "r").read()
            example=f"""Goal: {goal}
Expected answer:
<observation>
Description on what you see in screenshot 
</observation>
<plan>
{steps}
</plan>
<thought>
Reasoning for the plan
</thought>

"""
            examples.append(example)
    return examples



     
        
        

        
    