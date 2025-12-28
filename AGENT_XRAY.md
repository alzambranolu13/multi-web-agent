# 1. run app:

create a screen:
```bash
SUFFIX=qwen
CF_TUNNEL=agent-xray-mwa-$SUFFIX

screen -S $CF_TUNNEL
```

run app:
```bash
source venv/bin/activate

SUFFIX=qwen
export AGENTXRAY_APP_PORT=24863
export AGENTLAB_EXP_ROOT=/home/nlp/users/azambrano/agentlab_results/strategies-$SUFFIX
python -m utils.agent_xray
```

# 2. create cf tunnel

```bash
SUFFIX=qwen
AGENTXRAY_APP_PORT=24863
DOMAIN_NAME=mcgill-nlp.org

# create a tunnel
CF_TUNNEL=agent-xray-mwa-$SUFFIX
CF_PORT=$AGENTXRAY_APP_PORT
# First, if you have an existing tunnel, delete it
cloudflared tunnel cleanup $CF_TUNNEL
cloudflared tunnel delete $CF_TUNNEL
# Now, create a new tunnel and route it to the correct domain
cloudflared tunnel create $CF_TUNNEL
cloudflared tunnel route dns --overwrite-dns $CF_TUNNEL $CF_TUNNEL.$DOMAIN_NAME
# # In general, you can run the tunnel with:
# cloudflared tunnel run  --url http://localhost:$CF_PORT $CF_TUNNEL
# Preferably, run it in a screen session:
screen -S cf-$CF_TUNNEL -dm cloudflared tunnel run  --url http://localhost:$CF_PORT $CF_TUNNEL
```






