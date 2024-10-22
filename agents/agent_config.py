from agentlab.agents import dynamic_prompting as dp
from agentlab.experiments import args
from agentlab.llm.llm_configs import CHAT_MODEL_ARGS_DICT

from agentlab.agents.generic_agent import generic_agent
from agentlab.agents.generic_agent.generic_agent_prompt import GenericPromptFlags

from .generic_agent import MyGenericAgentArgs
from .basic_agents import ObserverAgentArgs, PlannerAgentArg, ContAgentArg, BrotherAgentArg




OBS_AGENT = ObserverAgentArgs(chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"])
PLAN_AGENT = PlannerAgentArg(chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"])
CONT_AGENT = ContAgentArg(chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"])
BIG_BROTHER = BrotherAgentArg(chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-2024-05-13"])

FLAGS_DESC = GenericPromptFlags(
    obs=dp.ObsFlags(
        is_visible= False,
        use_html=False,
        use_ax_tree=False,
        use_focused_element=False,
        use_error_logs=False,
        use_history=False,
        use_past_error_logs=False,
        use_action_history=False,
        use_think_history=False,
        use_diff=False,
        use_screenshot=False,
        use_som=False,
        extract_visible_tag=False,
        extract_clickable_tag=False,
        extract_coords="False",
        filter_visible_elements_only=False,
    ),
    action=dp.ActionFlags(
        multi_actions=False,
        action_set="bid",
        long_description=False,
        individual_examples=False,
    ),
    use_plan=False,
    use_criticise=True,
    use_thinking=True,
    use_memory=True,
    use_concrete_example=True,
    use_abstract_example=True,
    use_hints=True,
    enable_chat=False,
    max_prompt_tokens=None,
    be_cautious=True,
    extra_instructions=None,
)



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
        multi_actions=False,
        action_set="bid",
        long_description=True,
        individual_examples=True,
    ),
    use_plan=False,
    use_criticise=False,
    use_thinking=True,
    use_memory=False,
    use_concrete_example=True,
    use_abstract_example=True,
    use_hints=True,
    enable_chat=False,
    max_prompt_tokens=None,
    be_cautious=True,
    extra_instructions="Evaluate if the goal is complete based on your previous action, please include in your chain of thought why you think the goal is either reached or not. After you think the goal is completed please send the user a done message, no need to re-verify",
)

AGENT_4o = MyGenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-2024-05-13"],
    flags=FLAGS_GPT_4o,
)

AGENT_4o_MINI = MyGenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4o-mini-2024-07-18"],
    flags=FLAGS_GPT_4o,
)


