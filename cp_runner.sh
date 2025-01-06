#!/bin/bash
#SBATCH --job-name=generic_job 
#SBATCH --partition=unkillable
#SBATCH --time=05:00:00
module load python/3.10 cuda/11.8

export AGENTLAB_EXP_ROOT="/home/mila/a/alejandra.zambrano/scratch/new_scratch"
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

# export WA_SHOPPING="https://wa-shopping-az-0.mcgill-nlp.org"
# export WA_SHOPPING_ADMIN="https://wa-shopping-admin-az-0.mcgill-nlp.org/admin"
# export WA_REDDIT="https://wa-forum-az-0.mcgill-nlp.org/forums/all"
# export WA_GITLAB="https://wa-gitlab-az-0.mcgill-nlp.org/explore"
# export WA_WIKIPEDIA="https://wa-wikipedia-az-0.mcgill-nlp.org/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
# export WA_MAP="https://wa-openstreetmap-az-0.mcgill-nlp.org"
# export WA_HOMEPAGE="https://wa-homepage-az-0.mcgill-nlp.org"

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


python3 main.py --config CP --n_jobs 4 --relaunch True --contains 2025-01-04_12-40-19_cp-on-webarena-100_CP

