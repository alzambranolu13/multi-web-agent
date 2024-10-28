import json
import time

from base.exp_args import MultiAgentExpArgsBase
from browsergym.experiments.loop import DataclassJSONEncoder
from browsergym.experiments.loop import _send_chat_info, DataclassJSONEncoder,logger, StepInfo

from browsergym.experiments.loop import EnvArgs

class MultiAgentExpArgsCP(MultiAgentExpArgsBase):
    def __init__(self,agents_dict:dict,  env_args: EnvArgs ):
        super().__init__(agent_args=agents_dict['CONTROLLER'], env_args=env_args)
        self.agents_dict = agents_dict
        self.planner = None
        self.controller = None

    def _makes_agents(self):
        agents= self.agents_dict
        self.planner = agents['PLANNER'].make_agent()
        self.controller = agents['CONTROLLER'].make_agent()

        return self.controller   


    def _multi_agent_step(self, step_info, steps_completed,steps_failed):  

        logger.debug(f"Starting step {step_info.step}.")

        step_info.profiling.agent_start = time.time()
        planner_ans_dict = self.planner.get_action(step_info.obs.copy(),steps_completed,steps_failed)
        plan = planner_ans_dict['steps']

        with open(self.exp_dir / "planner_answer.json", "w") as f:
            json.dump(plan, f, indent=4, cls=DataclassJSONEncoder)
        
        return plan[0]



            

                

  
        





