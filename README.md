# multi-web-agent

## setting up

We use python 3.12.

First, install requirements
```bash
# assumign inside /path/to/multi-web-agent
python -m venv venv
source venv/bin/activate
```

Next, we need to install agentlab from the repository. we are using a stable fork of agentlab (no change) for stability purposes. we keep a version in `stable`. To install agentlab, do this:

```bash
# assuming you are in /path/to/multi-web-agent
cd ..
git clone https://github.com/alzambranolu13/AgentLab  #
#hash 695f7e648d2c1fb79ffe85f2dc26cf015ac1dbbb
cd AgentLab/
git checkout stable

# Now, you can install agentlab now:
pip install -e .
playwright install

# Now, go back to multi-web-agent:
cd ../multi-web-agent

# finally, install requirements, which has a diff version of agentlab
pip install -r requirements.txt
```

You can now use multi-web-agent!
