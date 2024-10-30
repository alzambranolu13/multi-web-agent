import json
import logging
import time

from base.exp_args import MultiAgentExpArgsBase
from browsergym.experiments.loop import DataclassJSONEncoder
from browsergym.experiments.loop import _send_chat_info, DataclassJSONEncoder,logger, StepInfo

from browsergym.experiments.loop import EnvArgs

class MultiAgentExpArgsCP(MultiAgentExpArgsBase):
    def __init__(self,agents_dict:dict,  env_args: EnvArgs , logging_level= logging.INFO ):
        super().__init__(agent_args=agents_dict['CONTROLLER'], env_args=env_args, logging_level= logging_level)
        self.agents_dict = agents_dict
        self.planner = None
        self.controller = None

    def _makes_agents(self):
        agents= self.agents_dict
        self.planner = agents['PLANNER'].make_agent()
        self.controller = agents['CONTROLLER'].make_agent()

        return self.controller   


    def _multi_agent_step(self, step_info: StepInfo, steps_completed,steps_failed):  

        logger.debug(f"Starting step {step_info.step}.")

        step_info.profiling.agent_start = time.time()
        planner_ans_dict = self.planner.get_action(step_info.obs.copy(),steps_completed,steps_failed)
        plan = planner_ans_dict['steps']

        with open(self.exp_dir / f"planner_answer_step_{step_info.step}.json", "w") as f:
            json.dump(planner_ans_dict, f, indent=4, cls=DataclassJSONEncoder)
        
        if len(plan)!= 0:
            return plan[0]
        else:
            return None 



            

                

  
        





