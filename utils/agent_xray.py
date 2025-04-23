from agentlab.analyze.agent_xray import run_gradio, RESULTS_DIR

from agents import cont_plan_obs, planner_controller

if __name__ == "__main__":
    run_gradio(RESULTS_DIR)