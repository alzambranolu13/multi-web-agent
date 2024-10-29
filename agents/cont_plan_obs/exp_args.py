import json
import logging
import time

from browsergym.experiments.loop import DataclassJSONEncoder
from browsergym.experiments.loop import _send_chat_info, DataclassJSONEncoder,logger, StepInfo
from browsergym.experiments.loop import EnvArgs

from base.exp_args import MultiAgentExpArgsBase

class MultiAgentExpArgsCPO(MultiAgentExpArgsBase):
    def __init__(self,agents_dict:dict,  env_args: EnvArgs ,logging_level= logging.INFO ):
        super().__init__(agent_args=agents_dict['CONTROLLER'], env_args=env_args, logging_level= logging_level)
        self.agents_dict = agents_dict
        self.planner = None
        self.controller = None
        self.observer = None

    def _makes_agents(self):
        agents= self.agents_dict
        self.planner = agents['PLANNER'].make_agent()
        self.controller = agents['CONTROLLER'].make_agent()
        self.observer =  agents['OBSERVER'].make_agent()

        return self.controller   

    def _multi_agent_step(self, step_info, env, episode_info):  
        last_action = None
        previous_plan = None
        while not step_info.is_done:  # set a limit
            logger.debug(f"Starting step {step_info.step}.")                
            #action_planner = planner.get_action(PlanSystemPrompt,step_info.obs.copy())
            goal = step_info.obs["goal"]
            elements = self.observer.get_action(step_info.obs.copy())
            plan = self.planner.get_action(elements,goal,last_action,previous_plan)
            previous_plan = plan
            last_action = plan[0]
            #goal = step_info.obs['goal']
            action, agent_info = self.controller.get_action(last_action)
            step_info.profiling.agent_start = time.time()
            #action, agent_info = agent.get_action(step_info.obs.copy(),elements)
            step_info.action, step_info.agent_info = action,agent_info
            step_info.profiling.agent_stop = time.time()

            step_info.make_stats()

            #action = step_info.from_action(agent,elements)
            logger.debug(f"Agent chose action:\n {action}")

            if action is None:
                step_info.truncated = True

            step_info.save_step_info(self.exp_dir)
            logger.debug(f"Step info saved.")

            _send_chat_info(env.unwrapped.chat, action, step_info.agent_info)
            logger.debug(f"Chat info sent.")
            step_info = StepInfo(step=step_info.step + 1)
            episode_info.append(step_info)

            if action is None:
                logger.debug(f"Agent returned None action. Ending episode.")
                break

            logger.debug(f"Sending action to environment.")
            step_info.from_step(env, action, obs_preprocessor=self.controller.obs_preprocessor)
            logger.debug(f"Environment stepped.")
