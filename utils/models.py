from agentlab.llm.chat_api import (
    OpenAIModelArgs,
)

from agentlab.agents.generic_agent.generic_agent import GenericAgentArgs
from agentlab.agents.generic_agent.agent_configs import FLAGS_GPT_4o



chat_model_41=  OpenAIModelArgs(model_name="gpt-4.1-mini",max_total_tokens=128_000,max_input_tokens=128_000,max_new_tokens=16_384,vision_support=True)
AGENT_41_M = GenericAgentArgs(chat_model_args=chat_model_41,flags=FLAGS_GPT_4o)