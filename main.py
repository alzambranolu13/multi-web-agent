import argparse

from browsergym.experiments.loop import EnvArgs
from utils.experiment_args import MyExpArgs

from agentlab.agents.agent_args import AgentArgs
from agentlab.experiments.exp_utils import RESULTS_DIR
from agentlab.experiments.launch_exp import import_object

from agents.basic_agents import ObserverAgentArgs




def make_exp_args(obs_args: AgentArgs, plan_args: AgentArgs,des_args: AgentArgs,agent_args: AgentArgs, start_url="https://www.google.com"):

    try:
        agent_args.flags.action.demo_mode = "default"
    except AttributeError:
        pass

    exp_args = MyExpArgs(
        obs_args= obs_args,
        plan_args= plan_args,
        des_args= des_args,
        agent_args= agent_args,
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
        ),
    )

    return exp_args


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--agent_config",
        type=str,
        default="agents.available_agents.CONT_AGENT",
        help="""Python path to the agent config. Defaults to : "agents.generic_agent.AGENT_4o".""",
    )
    parser.add_argument(
        "--start_url",
        type=str,
        default="https://www.google.com",
        help="The start page of the agent. Defaults to https://www.google.com",
    )

    args, unknown = parser.parse_known_args()
    obs_args = import_object('agents.available_agents.OBS_AGENT')
    #MostBasicAgentArgs(chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"])
    #obs_args = ObserverAgentArgs()
    plan_args = import_object('agents.available_agents.PLAN_AGENT')
    #des_args = import_object('agents.available_agents.DESC_AGENT')
    cont_args = import_object(args.agent_config)
    exp_args = make_exp_args(obs_args, plan_args,None, cont_args, args.start_url)
    exp_args.prepare(RESULTS_DIR / "ui_assistant_logs")
    
    exp_args.run()


if __name__ == "__main__":
    main()
