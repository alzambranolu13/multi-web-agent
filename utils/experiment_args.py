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

from agents.prompts.prompts import ObsSystemPrompt,PlanSystemPrompt,DescSystemPrompt,ObsGoalInstructions, ContGoalInstructions


@dataclass
class MyExpArgs(loop.ExpArgs):
    def __init__(self, obs_args: AgentArgs, plan_args: AgentArgs,des_args: AgentArgs, agent_args:AgentArgs, env_args: EnvArgs ):
        super().__init__(agent_args=agent_args, env_args=env_args)
        self.obs_args= obs_args
        self.plan_arg= plan_args
        self.des_args= des_args

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
            #agent = self.agent_args.make_agent(DescSystemPrompt(),ContGoalInstructions())
            observer = self.obs_args.make_agent()
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
            last_action = None
            previous_plan = None
            while not step_info.is_done:  # set a limit
                logger.debug(f"Starting step {step_info.step}.")                
                #action_planner = planner.get_action(PlanSystemPrompt,step_info.obs.copy())
                goal = step_info.obs["goal"]
                elements = observer.get_action(step_info.obs.copy())
                plan = planner.get_action(elements,goal,last_action,previous_plan)
                previous_plan = plan
                last_action = plan[0]
                #goal = step_info.obs['goal']
                action, agent_info = agent.get_action(last_action)
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
                step_info.from_step(env, action, obs_preprocessor=agent.obs_preprocessor)
                logger.debug(f"Environment stepped.")

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



        





