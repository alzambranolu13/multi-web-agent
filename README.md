# multi-web-agent

## setting up agentlab

First, install requirements
```bash
# assumign inside /path/to/multi-web-agent
pip install -r requiremnets.txt
```

we are using a stable fork of agentlab (no change) for stability purposes. we keep a version in `stable`. To install agentlab, do this:

```bash
# assuming you are in /path/to/multi-web-agent
cd ..
git clone https://github.com/alzambranolu13/AgentLab
cd AgentLab/
git checkout stable

# Now, you can install agentlab now:
pip install -e .

# Now, go back to multi-web-agent:
cd ../multi-web-agent
```

You can now use multi-web-agent!