#!/bin/bash
#SBATCH --job-name=generic_job 
#SBATCH --partition=unkillable
#SBATCH --time=05:00:00
module load python/3.10 cuda/11.8

export AGENTLAB_EXP_ROOT="/home/mila/a/alejandra.zambrano/scratch"
export AGENTXRAY_SHARE_GRADIO="true"
export OPENAI_API_KEY="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"

export BASE_URL="http://ec2-18-232-29-212.compute-1.amazonaws.com"

export WA_SHOPPING="$BASE_URL:7770/"
export WA_SHOPPING_ADMIN="$BASE_URL:7780/admin"
export WA_REDDIT="$BASE_URL:9999"
export WA_GITLAB="$BASE_URL:8023"
export WA_WIKIPEDIA="$BASE_URL:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="$BASE_URL:3000"
export WA_HOMEPAGE="$BASE_URL:4399"


#Configuration for webarena-browsergym
pip install browsergym-webarena
pip install -r requirements.txt

echo BROWSER-GYM-DONE

#Configuration for multiagent
cd multi-web-agent
python -m venv venv
source venv/bin/activate
cd ../AgentLab
pip install -e .
playwright install
cd ../multi-web-agent
pip install -r requirements.txt

echo MULTIAGENT-DONE

python3 main.py --config CP --n_jobs 4


python3 main.py --config CP --n_jobs 4 --relaunch True --contains 2024-12-16_23-46-45_cp-on-webarena-test_CP

