import os
import bgym
from dataclasses import dataclass


from agentlab.llm.chat_api import (
    OpenAIModelArgs,
)
from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs, GenericPromptFlags
from agentlab.agents import dynamic_prompting as dp

from agentlab.agents.generic_agent.agent_configs import FLAGS_GPT_4o
from agentlab.llm.base_api import BaseModelArgs
from agentlab.llm.chat_api import OpenAIModelArgs, ChatModel
import agentlab.llm.tracking as tracking
from openai import OpenAI

FLAGS_GPT_4o_plan = GenericPromptFlags(
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
        use_screenshot=False,
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
    use_plan=True,
    use_criticise=False,
    use_thinking=True,
    use_memory=False,
    use_concrete_example=True,
    use_abstract_example=True,
    use_hints=True,
    enable_chat=False,
    max_prompt_tokens=40_000,
    be_cautious=True,
    extra_instructions=None,
)

chat_model_41_mini=  OpenAIModelArgs(model_name="gpt-4.1-mini",max_total_tokens=128_000,max_input_tokens=128_000,max_new_tokens=16_384,vision_support=True)
AGENT_41_MINI = GenericAgentArgs(chat_model_args=chat_model_41_mini,flags=FLAGS_GPT_4o)
AGENT_41_PLAN = GenericAgentArgs(chat_model_args=chat_model_41_mini,flags=FLAGS_GPT_4o_plan)
chat_model_41=  OpenAIModelArgs(model_name="gpt-4.1-2025-04-14",max_total_tokens=128_000,max_input_tokens=128_000,max_new_tokens=16_384,vision_support=True)
AGENT_41 = GenericAgentArgs(chat_model_args=chat_model_41,flags=FLAGS_GPT_4o)

class OpenAICompatibleChatModel(ChatModel):
    def __init__(
        self, 
        model_name,
        api_key_env_var,
        base_url_env_var,
        api_key=None,
        base_url=None,
        temperature=0.5,
        max_tokens=1024,
        max_retry=4,
        min_retry_wait_time=60,
    ):
        if not api_key_env_var in os.environ:
            raise ValueError(f"{api_key_env_var} must be set in the environment")
        if not base_url_env_var in os.environ:
            raise ValueError(f"{base_url_env_var} must be set in the environment")

        if base_url is None:
            base_url = os.environ[base_url_env_var]
        
        super().__init__(
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retry=max_retry,
            min_retry_wait_time=min_retry_wait_time,
            api_key_env_var=api_key_env_var,
            client_class=OpenAI,
            client_args={
                "base_url": base_url,
            },
            pricing_func=tracking.get_pricing_openai,
        )


@dataclass
class VllmModelArgs(BaseModelArgs):
    """Serializable object for instantiating a generic chat model with an OpenAI
    model."""

    def set_base_url(self, base_url):
        self.base_url = base_url

    def set_api_key(self, api_key):
        self.api_key = api_key
    
    def make_model(self):
        base_url = None if not hasattr(self, "base_url") else self.base_url
        api_key = None if not hasattr(self, "api_key") else self.api_key
        
        return OpenAICompatibleChatModel(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_new_tokens,
            api_key_env_var="VLLM_API_KEY",
            base_url_env_var="VLLM_BASE_URL",
            base_url=base_url,
            api_key=api_key,
        )
    

def get_default_flags(
    use_screenshot=True,
    use_som=True,
    max_prompt_tokens=16384 - 4096,
    enable_chat=False,
):

    from agentlab.agents import dynamic_prompting as dp
    from agentlab.agents.generic_agent.generic_agent import GenericPromptFlags
    from browsergym.experiments.benchmark import HighLevelActionSetArgs

    flags = GenericPromptFlags(
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
            use_screenshot=use_screenshot,
            use_som=use_som,
            extract_visible_tag=True,
            extract_clickable_tag=True,
            extract_coords="False",
            filter_visible_elements_only=False,
        ),
        action=dp.ActionFlags(
            action_set=HighLevelActionSetArgs(
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
        enable_chat=enable_chat,
        max_prompt_tokens=max_prompt_tokens,
        be_cautious=True,
        extra_instructions=None,
    )

    return flags


def prepare_vllm_model(
    model_name="meta-llama/Llama-3.3-70B-Instruct",
    max_new_tokens=1024,
    max_prompt_tokens=16384 - 4096,
    max_total_tokens=16384,
    use_vision=False,
    enable_chat=False,
    base_url=None,
    api_key=None,
):
    # the base url and api key are set in VllmModelArgs's make_model,
    # so it is not necessary to set them here, but it is possible if needed
    model_args = VllmModelArgs(
        model_name=model_name,
        max_total_tokens=max_total_tokens,
        max_input_tokens=max_total_tokens - max_new_tokens,
        max_new_tokens=max_new_tokens,
        vision_support=use_vision,
    )
    if base_url is not None:
        model_args.set_base_url(base_url)
    if api_key is not None:
        model_args.set_api_key(api_key)

    agent_args = GenericAgentArgs(
        chat_model_args=model_args,
        flags=get_default_flags(
            max_prompt_tokens=max_prompt_tokens,
            use_som=use_vision,
            use_screenshot=use_vision,
            enable_chat=enable_chat,
        ),
    )

    return agent_args




AGENT_QWEN_25 = prepare_vllm_model(model_name="Qwen/Qwen2.5-VL-72B-Instruct",use_vision=True)