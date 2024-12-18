from agentlab.llm.tracking import set_tracker


def cost_tracker_decorator(get_action, suffix=""):
    def wrapper(self, obs, last_steps=None, steps_failed= None, previous_plan= None):
        with set_tracker(suffix) as tracker:
            if last_steps== None:
                action, agent_info = get_action(self, obs)
            else:
                action, agent_info = get_action(self, obs, last_steps=last_steps,steps_failed=steps_failed, previous_plan=previous_plan)
        agent_info.get("stats").update(tracker.stats)
        return action, agent_info

    return wrapper