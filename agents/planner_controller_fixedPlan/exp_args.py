import json
import logging
import time
import traceback

from base.exp_args import MultiAgentExpArgsBase
from browsergym.experiments.loop import DataclassJSONEncoder
from browsergym.experiments.loop import _send_chat_info, DataclassJSONEncoder,logger, StepInfo, _is_debugging, _save_summary_info, _send_chat_info, save_package_versions,logger, StepInfo

from browsergym.experiments.loop import EnvArgs

class MultiAgentExpArgsCPfixed(MultiAgentExpArgsBase):
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


    def _multi_agent_step(self, step_info: StepInfo):  

        logger.debug(f"Starting step {step_info.step}.")

        step_info.profiling.agent_start = time.time()
        planner_ans_dict,agent_info = self.planner.get_action(step_info.obs.copy())
        plan = planner_ans_dict['steps']

        with open(self.exp_dir/f"planner_answer_step_{step_info.step}.json", "w") as f:
            json.dump(planner_ans_dict, f, indent=4, cls=DataclassJSONEncoder)
        
        if len(plan)!= 0:
            return plan
        else:
            return None 
        

        
   
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
            agent = self._makes_agents()
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

            plan = self._multi_agent_step(step_info)

            while not step_info.is_done: 
                if len(plan)==0:
                    logger.debug(f"Empty plan received")
                    step_info.truncated = True
                    break
                agent.set_goal(plan[0])
                action = step_info.from_action(agent)
                logger.debug(f"Agent chose action:\n {action}")

                if action is None:
                    # will end the episode after saving the step info.
                    step_info.truncated = True
                    
                elif "noop" in action:
                    plan.pop(0)


                step_info.save_step_info(self.exp_dir)
                logger.debug(f"Step info saved.")

                _send_chat_info(env.unwrapped.chat, action, step_info.agent_info)
                logger.debug(f"Chat info sent.")

                if action is None:
                    logger.debug(f"Agent returned None action. Ending episode.")
                    break

                step_info = StepInfo(step=step_info.step + 1)
                episode_info.append(step_info)

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


                

  
        





