# multi-web-agent

## Versioning

The current agentlab/browsergym versions are used for po-web-agents:
- AgentLab: 
  - repo: `alzambranolu/AgentLab`
  - branch: [`project-4`](https://github.com/alzambranolu13/AgentLab)
  - hash: [`be1998c5fad5bda47ba50497ec3899aae03e85ec`](https://github.com/alzambranolu13/AgentLab/commit/be1998c5fad5bda47ba50497ec3899aae03e85ec)
- BrowserGym: `0.13.1`



## Setting up

We use python 3.12.

First, clone this repo and create a virtual environment:
```bash
git clone https://github.com/McGill-NLP/multi-web-agent.git
cd multi-web-agent
python3 -m venv venv
source venv/bin/activate
```

Next, we need to install agentlab from the repository. we are using a stable fork of agentlab (no change) for stability purposes. we keep a version in `stable`. To install agentlab, do this:

```bash
# assuming you are in /path/to/multi-web-agent
git clone https://github.com/alzambranolu13/AgentLab  #
cd AgentLab/
git checkout project-3

# Now, you can install agentlab now:
pip install -e .
playwright install

# finally go back to multi-web-agent and  install requirements
cd ..
pip install -r requirements.txt
```

You can now use multi-web-agent!

## Running Experiments

### Running Main Experiments (`main.py`)

The `main.py` script runs experiments on WebArena benchmarks with various agent configurations.

#### Basic Usage

```bash
python main.py --config CPFixed --run_set test --n_jobs 1
```

#### Common Examples

**Important:** The benchmark includes difficulty-based splits (`hard`, `medium`, `easy`) that are useful for evaluating agent performance across different complexity levels. See the "Running Difficulty-Based Sets" section below for examples.

**Run a test set experiment with default settings:**
```bash
python main.py --config CPFixed --run_set test
```

**Run with a specific model:**
```bash
python main.py --config CPFixed --run_set test --planner 41-mini --controller 41-mini
```

**Run with reproducibility mode:**
```bash
python main.py --config CPFixed --run_set test --reproduce
```

**Run with multiple parallel jobs:**
```bash
python main.py --config CPFixed --run_set test --n_jobs 4
```

**Relaunch an existing experiment:**
```bash
python main.py --relaunch --contains "experiment_name"
```

#### Running Difficulty-Based Sets

The benchmark includes tasks categorized by difficulty (hard, medium, easy). These sets are particularly useful for evaluating agent performance across different complexity levels.

**Run on hard difficulty tasks:**
```bash
python main.py --config CPFixed --run_set hard
```

**Run on medium difficulty tasks:**
```bash
python main.py --config CPFixed --run_set medium
```

**Run on easy difficulty tasks:**
```bash
python main.py --config CPFixed --run_set easy
```

**Run all difficulty sets with custom models:**
```bash
# Hard tasks
python main.py --config CPFixed --run_set hard --planner 41-mini --controller 41-mini --n_jobs 4

# Medium tasks
python main.py --config CPFixed --run_set medium --planner 41-mini --controller 41-mini --n_jobs 4

# Easy tasks
python main.py --config CPFixed --run_set easy --planner 41-mini --controller 41-mini --n_jobs 4
```


#### Configuration Options

- `--config`: Agent configuration type
  - `generic`: Single-agent configuration
  - `CP`: Planner-Controller configuration
  - `CPFixed`: Planner-Controller with fixed plan (default)
  - `CPO`: Planner-Controller-Observer configuration

- `--run_set`: Dataset split to run on
  - `train`: Training set
  - `test`: Test set (default)
  - `valid`: Validation set
  - `hard`: Hard difficulty tasks
  - `medium`: Medium difficulty tasks
  - `easy`: Easy difficulty tasks

- `--n_jobs`: Number of parallel jobs (default: 1)
- `--planner`: Model for planner agent (e.g., `4o-mini`, `41-mini`, default: `41-mini`)
- `--controller`: Model for controller agent (e.g., `4o-mini`, `41-mini`, default: `41-mini`)
- `--backend`: Model for single-agent/generic config
- `--strategy`: Strategy identifier for planner (default: `strategy_1`)
- `--prompt_opt`: Prompt option index for planner (default: 0)
- `--suffix`: Suffix for experiment name
- `--reproduce`: Enable reproducibility mode (makes agents deterministic)
- `--relaunch`: Relaunch an existing study
- `--contains`: Keyword to find experiment directory when relaunching
- `--ignore_dependencies`: Ignore task dependencies in benchmark

#### Full Example

```bash
python main.py \
    --config CPFixed \
    --run_set test \
    --n_jobs 4 \
    --planner 41-mini \
    --controller 41-mini \
    --strategy strategy_1 \
    --prompt_opt 0 \
    --suffix my_experiment
```

### Running UI Assistant (`ui_assistant.py`)

The `ui_assistant.py` script provides an interactive browser-based interface for testing agents on custom websites. This is useful for debugging and demonstration purposes.

#### Basic Usage

```bash
python ui_assistant.py --config CP --start_url https://www.google.com
```

#### Common Examples

**Run with Planner-Controller configuration:**
```bash
python ui_assistant.py --config CP --start_url https://www.google.com
```

**Run with Planner-Controller-Observer configuration:**
```bash
python ui_assistant.py --config CPO --start_url https://example.com
```

**Run with generic single-agent configuration:**
```bash
python ui_assistant.py --config generic --start_url https://www.google.com
```

#### Configuration Options

- `--config`: Agent configuration type
  - `generic`: Single-agent configuration
  - `CP`: Planner-Controller configuration (default)
  - `CPO`: Planner-Controller-Observer configuration

- `--start_url`: The starting URL for the agent (default: `https://www.google.com`)

#### Features

- **Interactive Browser**: The browser window opens in non-headless mode, allowing you to observe the agent's actions
- **Video Recording**: Automatically records videos of the agent's interactions
- **User Messages**: Waits for user messages, making it suitable for interactive testing
- **Custom Viewport**: Uses a 1500x1280 viewport for better visibility
- **Slow Motion**: Includes 1000ms slow-mo for easier observation

#### Notes

- The UI assistant runs in interactive mode with the browser visible
- Results are saved to `ui_assistant_logs` directory
- The agent will wait for user input when configured to do so
- This tool is primarily for development and demonstration purposes
