import bgym

from agentlab.agents import dynamic_prompting as dp
from agentlab.llm.llm_configs import CHAT_MODEL_ARGS_DICT

from agentlab.agents.generic_agent.generic_agent_prompt import GenericPromptFlags

from .agent_args import ControllerAgentArgs,PlannerAgentArg

def get_cp_planner_args(generic_agent_args):
    return PlannerAgentArg(chat_model_args=generic_agent_args.chat_model_args)

PLAN_AGENT_CP = PlannerAgentArg(chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"], strategy="strategy_1", prompt_opt=1, temperature= 0.4)

FLAGS_GPT_4o = GenericPromptFlags(
    obs=dp.ObsFlags(
        use_html=False,
        use_ax_tree=True,
        use_focused_element=True,
        use_error_logs=True,
        use_history=True,
        use_past_error_logs=False,
        use_action_history=True,
        use_think_history=False,
        use_diff=False,
        html_type="pruned_html",
        use_screenshot=True,
        use_som=False,
        extract_visible_tag=True,
        extract_clickable_tag=True,
        extract_coords="False",
        filter_visible_elements_only=False,
    ),
    action=dp.ActionFlags(
        action_set=bgym.HighLevelActionSetArgs(
            subsets=["bid"],
            multiaction=False,
        ),
        long_description=False,
        individual_examples=False,
    ),
    use_plan=False,
    use_criticise=False,
    use_thinking=True,
    use_memory=False,
    use_concrete_example=True,
    use_abstract_example=True,
    use_hints=True,
    enable_chat=False,
    max_prompt_tokens=12_288,
    be_cautious=True,
    extra_instructions= """
It's a priority to follow the Global Plan. 
In your thought process, explicitly reflect on how the plan is being followed by your actions and the current step.
"""
)


CONTROLLER_AGENT_CP = ControllerAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"],
    flags=FLAGS_GPT_4o,
)