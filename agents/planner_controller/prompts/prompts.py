import os
from os import listdir
from os.path import isfile, isdir, join


PROMPT_DIR = os. getcwd()+'/agents/planner_controller/prompts/docs'

#example_types can only be 'webarena', 'open_ended', 'amazon', 'ebay', 'encyclopedia', 'reddit', 'wikipedia'
class PlannerPrompt():
    def __init__(self , example_types:str | list= 'webarena', goal= None, use_failed_steps:bool = False,last_steps=[], steps_failed=[]):
        self.system_prompt= f"""
    You are part of a collection of Web Agents which goal is to help the user perform tasks using a web browser. Your tasks 
    as the Planner is to figure out the different steps required to complete a certain goal. You are an expert in navigating the internet and any web page possible.
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
Please update your plan depending on the information provided in the Screenshot.

Here are some examples of what is your expected behavior:

""" 
        for example in examples:
            self.prompt+=example

        self.prompt+= f"""End of examples.

Make sure to give your answer in the expected format.

The user's goal is: {goal}

You have executed succesfully the following actions: {last_steps}

If the goal is complete please return an empty plan.
"""
        if (use_failed_steps):
            self.prompt+=f"""
These steps have failed to be exectued: {steps_failed} 
Please adequate your plan to achieve the failed steps
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



if __name__ == '__main__':
    print(os.getcwd())
    test=open(f'docs/amazon/question0.txt', "r").read()  
    #print(test)
    a= PlannerPrompt('webarena','open this')
    print(a.prompt)
     
        
        

        
    