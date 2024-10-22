import browsergym.experiments.loop as loop

import gzip
import importlib.metadata
import json
import logging
import os
import pickle
import sys
import time
import traceback
import uuid

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import gymnasium as gym
import numpy as np
from browsergym.core.chat import Chat
from PIL import Image
from tqdm import tqdm

from browsergym.experiments.agent import Agent
from browsergym.experiments.loop import EnvArgs
from browsergym.experiments.loop import DataclassJSONEncoder
from browsergym.experiments.loop import _is_debugging, _save_summary_info, _send_chat_info, save_package_versions,logger, StepInfo
from agentlab.agents.agent_args import AgentArgs
from browsergym.experiments.utils import count_messages_token, count_tokens


@dataclass
class MultiAgentExpArgsBase(loop.ExpArgs):
    def __init__(self, plan_args: AgentArgs, agent_args:AgentArgs,  env_args: EnvArgs ):
        super().__init__(agent_args=agent_args, env_args=env_args)
        self.plan_arg= plan_args
        self.step_limit=20
    def _multi_agent_step(self):  # TODO: add relevant args
        pass

    def run(self):
        """Run the experiment and save the results"""

        # start writing logs to run logfile
        self._set_logger()

        # log python environment info
        save_package_versions(self.exp_dir)

        episode_info = []
        env, step_info, err_msg, stack_trace = None, None, None, None
        try:
            logger.info(f"Running experiment {self.exp_name} in:\n  {self.exp_dir}")
            planner = self.plan_arg.make_agent()
            agent = self.agent_args.make_agent()
            logger.debug(f"Agents created.")
            env = self.env_args.make_env(
                action_mapping=agent.action_set.to_python_code, exp_dir=self.exp_dir
            )
            logger.debug(f"Environment created.")

            step_info = StepInfo(step=0)
            episode_info = [step_info]
            step_info.from_reset(
                env, seed=self.env_args.task_seed, obs_preprocessor=agent.obs_preprocessor
            )
            logger.debug(f"Environment reset.")
            steps_completed= []
            goal_reach= False
            while not(goal_reach):
                logger.debug(f"Starting step {step_info.step}.")
                #action = step_info.from_action(agent)
                step_info.profiling.agent_start = time.time()
                planner_ans_dict = planner.get_action(step_info.obs.copy(),steps_completed)
                plan = planner_ans_dict['steps']
                # TODO: save planner_ans_dict as planner_step_answer.json inside self.exp_dir
                with open(self.exp_dir / "planner_answer.json", "w") as f:
                    json.dump(plan, f, indent=4, cls=DataclassJSONEncoder)
                is_done= False
                if len(plan)==0:
                    break
                # change this while loop into a function called self._multi_agent_step()
                num_steps = 0
                while not is_done and len(plan)!=0 :  # set a limit  
                    if num_steps > self.step_limit :
                        break
                    action, agent_info = agent.get_action(step_info.obs.copy(), plan[0])
                    step_info.action, step_info.agent_info = action,agent_info
                    step_info.profiling.agent_stop = time.time()
                    logger.debug(f"Agent chose action:\n {action}")

                    if action is None:
                        step_info.truncated = True

                    step_info.save_step_info(self.exp_dir)
                    logger.debug(f"Step info saved.")
                    if "Done" in action or "done" in action :
                        is_done= True
                        break
                    _send_chat_info(env.unwrapped.chat, action, step_info.agent_info)
                    logger.debug(f"Chat info sent.")

                    step_info = StepInfo(step=step_info.step + 1)
                    episode_info.append(step_info)

                    if action is None:
                        logger.debug(f"Agent returned None action. Ending episode.")
                        break

                    logger.debug(f"Sending action to environment.")
                    step_info.from_step(env, action, obs_preprocessor=agent.obs_preprocessor)
                    logger.debug(f"Environment stepped.")
                    num_steps+=1
                
                
                steps_completed.append(plan[0])

                # _multi_agent_step ends here

        except Exception as e:
            err_msg = f"Exception uncaught by agent or environment in task {self.env_args.task_name}.\n{type(e).__name__}:\n{e}"
            stack_trace = traceback.format_exc()

            self.err_msg = err_msg
            self.stack_trace = stack_trace

            logger.warning(err_msg + "\n" + stack_trace)
            if _is_debugging() and self.enable_debug:
                raise

        finally:
            try:
                if step_info is not None:
                    step_info.save_step_info(self.exp_dir)
            except Exception as e:
                logger.error(f"Error while saving step info in the finally block: {e}")
            try:
                if (
                    not err_msg
                    and len(episode_info) > 0
                    and not (episode_info[-1].terminated or episode_info[-1].truncated)
                ):
                    e = KeyboardInterrupt("Early termination??")
                    err_msg = f"Exception uncaught by agent or environment in task {self.env_args.task_name}.\n{type(e).__name__}:\n{e}"
                _save_summary_info(episode_info, self.exp_dir, err_msg, stack_trace)
            except Exception as e:
                logger.error(f"Error while saving summary info in the finally block: {e}")
            try:
                if env is not None:
                    env.close()
            except Exception as e:
                logger.error(f"Error while closing the environment in the finally block: {e}")
            try:
                self._unset_logger()  # stop writing logs to run logfile
            except Exception as e:
                logger.error(f"Error while unsetting the logger in the finally block: {e}")



        





