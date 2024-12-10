import argparse

from agents import MultiAgentArgs
from agentlab.agents.agent_args import AgentArgs
from browsergym.experiments.loop import EnvArgs
import agents.cont_plan_obs
from agents.cont_plan_obs.exp_args import MultiAgentExpArgsCPO
import agents.planner_controller
from agents.planner_controller.exp_args import MultiAgentExpArgsCP
from agentlab.agents.generic_agent import (
    AGENT_LLAMA3_70B,
    AGENT_LLAMA31_70B,
    RANDOM_SEARCH_AGENT,
    AGENT_4o,
    AGENT_4o_MINI,
)
from agents.planner_controller import (
    FLAGS_GPT_4o
)

from agents.planner_controller.agent_args import (
    PlannerAgentArg,
    ControllerAgentArgs
)

from agents.cont_plan_obs.agent_args import (
    ObserverAgentArgs,
)


from agentlab.experiments.exp_utils import RESULTS_DIR
from agentlab.experiments.launch_exp import import_object

from browsergym.experiments.loop import EnvArgs, ExpArgs

import agents


def make_exp_args(config: str, start_url="https://www.google.com", multiAgentArgs: agents.MultiAgentArgs= None, singleAgentArgs: AgentArgs= None ):

    
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
                'PLANNER': multiAgentArgs.planner_args,
                'CONTROLLER': multiAgentArgs.controller_args
            },
            env_args= env_args            
        )

    if config == 'CPO':
        exp_args = MultiAgentExpArgsCPO(
            agents_dict= {
                'OBSERVER': multiAgentArgs.observer_args,
                'PLANNER': multiAgentArgs.planner_args,
                'CONTROLLER': multiAgentArgs.controller_args
            },
            env_args= env_args
            
        )

    if config == 'generic':
        agent_args = singleAgentArgs
        agent_args.flags.action.demo_mode = "default"
        exp_args = ExpArgs(agent_args=agent_args, env_args= env_args)

        
    return exp_args


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=str,
        default="CP",
        help="""Python path to the agent config. Defaults to : "agents.generic_agent.AGENT_4o".""",
    )
    parser.add_argument(
        "--start_url",
        type=str,
        default="https://www.google.com",
        help="The start page of the agent. Defaults to https://www.google.com",
    )

    args, unknown = parser.parse_known_args()
    config = args.config
    single_agent_args = None
    multi_agent_args = None
    if config == 'generic':
        single_agent_args = AGENT_4o_MINI
    else:
        planner_args = PlannerAgentArg(chat_model_args=AGENT_4o_MINI.chat_model_args)
        controller_args = ControllerAgentArgs(chat_model_args=AGENT_4o_MINI.chat_model_args, flags= FLAGS_GPT_4o)
        observer_args = ObserverAgentArgs(chat_model_args=AGENT_4o_MINI.chat_model_args)
        if config == 'CP':
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= None )

        if config == 'CPO':
            multi_agent_args = MultiAgentArgs(planner_args= planner_args, controller_args= controller_args, observer_args= observer_args )
    exp_args = make_exp_args (config, args.start_url, multi_agent_args,single_agent_args)   
    exp_args.prepare(RESULTS_DIR / "ui_assistant_logs") 
    exp_args.run()


if __name__ == "__main__":
    main()