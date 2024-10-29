import argparse

from browsergym.experiments.loop import EnvArgs
import agents.cont_plan_obs
from agents.cont_plan_obs.exp_args import MultiAgentExpArgsCPO
import agents.planner_controller
from agents.planner_controller.exp_args import MultiAgentExpArgsCP
from base.exp_args import MultiAgentExpArgsBase

from agentlab.agents.agent_args import AgentArgs
from agentlab.experiments.exp_utils import RESULTS_DIR
from agentlab.experiments.launch_exp import import_object

from browsergym.experiments.loop import EnvArgs, ExpArgs

import agents


def make_exp_args(config: str, start_url="https://www.google.com"):

    
    env_args=EnvArgs(
            max_steps=1000,
            task_seed=None,
            task_name="openended",
            task_kwargs={
                "start_url": start_url,
            },
            headless=False,
            record_video=True,
            wait_for_user_message=True,
            viewport={"width": 1500, "height": 1280},
            slow_mo=1000,
        )

    if  config == 'CP':
        exp_args = MultiAgentExpArgsCP(
            agents_dict= {
                'PLANNER':agents.planner_controller.PLAN_AGENT,
                'CONTROLLER': agents.planner_controller.CONTROLLER_AGENT
            },
            env_args= env_args            
        )

    if config == 'CPO':
        exp_args = MultiAgentExpArgsCPO(
            agents_dict= {
                'OBSERVER': agents.cont_plan_obs.OBSERVER_AGENT,
                'PLANNER':agents.cont_plan_obs.PLAN_AGENT,
                'CONTROLLER': agents.cont_plan_obs.CONTROLLER_AGENT,
            },
            env_args= env_args
            
        )

    if config == 'generic':
        agent_args = import_object('agentlab.agents.generic_agent.AGENT_4o_MINI')
        agent_args.flags.action.demo_mode = "default"
        exp_args = ExpArgs(agent_args=agent_args, env_args= env_args)

        
    return exp_args


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--agent_config",
        type=str,
        default="CP",
        help="""Python path to the agent config. Defaults to : "agents.generic_agent.AGENT_4o".""",
    )
    parser.add_argument(
        "--start_url",
        type=str,
        default="http://ec2-3-131-244-37.us-east-2.compute.amazonaws.com:7780/admin",
        help="The start page of the agent. Defaults to https://www.google.com",
    )

    args, unknown = parser.parse_known_args()
    exp_args = make_exp_args (args.agent_config, args.start_url)   
    exp_args.prepare(RESULTS_DIR / "ui_assistant_logs") 
    exp_args.run()


if __name__ == "__main__":
    main()
