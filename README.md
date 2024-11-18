# multi-web-agent

## Versioning

The current agentlab/browsergym versions are used for po-web-agents:
- AgentLab: 
  - repo: `alzambranolu/AgentLab`
  - branch: [`project-1`](https://github.com/alzambranolu13/AgentLab)
  - hash: [`096cb59ed581d97c74607a0f86f6c9779a80be0c`](https://github.com/alzambranolu13/AgentLab/commit/096cb59ed581d97c74607a0f86f6c9779a80be0c)
- BrowserGym: `0.13.1`



## Setting up

We use python 3.12.

First, clone this repo and create a virtual environment:
```bash
git clone https://github.com/McGill-NLP/multi-web-agent.git
cd multi-web-agent
python -m venv venv
source venv/bin/activate
```

Next, we need to install agentlab from the repository. we are using a stable fork of agentlab (no change) for stability purposes. we keep a version in `stable`. To install agentlab, do this:

```bash
# assuming you are in /path/to/multi-web-agent
git clone https://github.com/alzambranolu13/AgentLab  #
cd AgentLab/
git checkout project-1

# Now, you can install agentlab now:
pip install -e .
playwright install

# finally, install requirements, which has a diff version of agentlab
pip install -r requirements.txt
```

You can now use multi-web-agent!
