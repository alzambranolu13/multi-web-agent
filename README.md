# multi-web-agent

## Versioning

The current agentlab/browsergym versions are used for po-web-agents:
- AgentLab: 
  - repo: `alzambranolu/AgentLab`
  - branch: [`project-3`](https://github.com/alzambranolu13/AgentLab)
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
