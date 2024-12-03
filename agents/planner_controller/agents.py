import re
from typing import TYPE_CHECKING
from dataclasses import asdict

from agentlab.agents.most_basic_agent.most_basic_agent import MostBasicAgent
from agentlab.agents import dynamic_prompting as dp
from agentlab.agents.generic_agent.generic_agent import GenericAgent
from agentlab.llm.llm_utils import parse_html_tags_raise, image_to_jpg_base64_url, ParseError,SystemMessage, retry, Discussion
from agentlab.llm.chat_api import make_system_message, make_user_message
from browsergym.experiments.agent import AgentInfo

from .prompts.dynamic_prompts import MyMainPrompt
from .prompts.prompts import PlannerPrompt


if TYPE_CHECKING:
    from agentlab.llm.chat_api import BaseModelArgs



class PlannerAgent(MostBasicAgent):
    def __init__(self, temperature: float, use_chain_of_thought: bool, use_failed_steps: bool, chat_model_args: "BaseModelArgs"):
        super().__init__(temperature, use_chain_of_thought, chat_model_args)
        self.use_failed_steps= use_failed_steps

    def add_screenshot(self, prompt, screenshot):
        if isinstance(prompt, str):
            prompt = [{"type": "text", "text": prompt}]

        img_url = image_to_jpg_base64_url(screenshot)
        prompt.append(
            {
                "type": "image_url",
                "image_url": {"url": img_url, "detail": "auto"},
            }
        )
        return prompt

    def get_action(self, obs: dict, last_steps: list, steps_failed: list) -> tuple[str, dict]:

        main_prompt= PlannerPrompt('webarena', obs['goal'], self.use_failed_steps, last_steps, steps_failed)
        system_prompt, prompt = main_prompt.system_prompt, main_prompt.prompt
        prompt = self.add_screenshot(prompt, obs['screenshot'])

        messages = [make_system_message(system_prompt), make_user_message(prompt)]

        def parser(response: str) -> tuple[dict, bool, str]:
            blocks= parse_html_tags_raise(response, keys=('plan','observation'), optional_keys='thought')
            if len(blocks) == 0:
                raise ParseError("No code block found in the response")
            pattern = re.compile(r"[0-9]\..*\n")
            steps = pattern.findall(blocks['plan'])
            if len(steps)== 0:
                pattern = re.compile(r"[0-9]\..*.")
                steps = pattern.findall(blocks['plan'])
            steps = [step.split('.')[1] for step in steps]
            answer= {'steps':steps, 'observation': blocks['observation'], "response_raw": response}
            if 'thought' in blocks:
                answer['thought'] = blocks['thought']
            return answer

        ans_dict = retry(self.chat, messages, n_retry=6, parser=parser)

        return ans_dict
    

class ControllerAgent(GenericAgent):
    def __init__(self,chat_model_args, flags, max_retry ):
        super().__init__(chat_model_args=chat_model_args, flags=flags, max_retry=max_retry )
        self.goal = None
    
    def set_goal(self,goal):
        self.goal= goal
 
    def get_action(self,obs): 
        self.obs_history.append(obs)

        main_prompt = MyMainPrompt(
            action_set=self.action_set,
            obs_history=self.obs_history,
            actions=self.actions,
            memories=self.memories,
            thoughts=self.thoughts,
            previous_plan=self.plan,
            step=self.plan_step,
            flags=self.flags,
            goal = self.goal
        )


        max_prompt_tokens, max_trunc_itr = self._get_maxes()

        system_prompt = SystemMessage(dp.SystemPrompt().prompt)

        human_prompt = dp.fit_tokens(
            shrinkable=main_prompt,
            max_prompt_tokens=max_prompt_tokens,
            model_name=self.chat_model_args.model_name,
            max_iterations=max_trunc_itr,
            additional_prompts=system_prompt,
        )

        stats = {}
        try:
            # TODO, we would need to further shrink the prompt if the retry
            # cause it to be too long

            chat_messages = Discussion([system_prompt, human_prompt])

            ans_dict = retry(
                self.chat_llm,
                chat_messages,
                n_retry=self.max_retry,
                parser=main_prompt._parse_answer,
            )
            # inferring the number of retries, TODO: make this less hacky
            ans_dict["busted_retry"] = 0
            # inferring the number of retries, TODO: make this less hacky
            ans_dict["n_retry"] = (len(chat_messages) - 3) / 2
        except ParseError as e:
            ans_dict = dict(
                action=None,
                n_retry=self.max_retry + 1,
                busted_retry=1,
            )

        stats = self.chat_llm.get_stats()
        stats["n_retry"] = ans_dict["n_retry"]
        stats["busted_retry"] = ans_dict["busted_retry"]

        self.plan = ans_dict.get("plan", self.plan)
        self.plan_step = ans_dict.get("step", self.plan_step)
        self.actions.append(ans_dict["action"])
        self.memories.append(ans_dict.get("memory", None))
        self.thoughts.append(ans_dict.get("think", None))

        agent_info = AgentInfo(
            think=ans_dict.get("think", None),
            chat_messages=chat_messages,
            stats=stats,
            extra_info={"chat_model_args": asdict(self.chat_model_args)},
        )
        return ans_dict["action"], agent_info
  

        

