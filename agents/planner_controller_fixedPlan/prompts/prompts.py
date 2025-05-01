import os
import json



PROMPT_DIR = os. getcwd()+'/agents/planner_controller_fixedPlan/prompts/strategies'

#strategies can only be 
class PlannerPrompt():
    def __init__(self ,goal= None, strategy : str = "strategy_1", prompt_opt : int = 0):
        with open(os.path.join(PROMPT_DIR, 'prompts.json'), 'r') as file:
            strategies_prompts = json.load(file)
        
        self.system_prompt= strategies_prompts[strategy][prompt_opt]['system']


        self.prompt= f"""
Create a plan to achieve the goal: {goal}.
""" 



     
        
        

        
    