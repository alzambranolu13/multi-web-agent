#!/bin/bash
#SBATCH --job-name=generic_job 
#SBATCH --partition=unkillable
#SBATCH --time=05:00:00
module load python/3.10 cuda/11.8

export AGENTLAB_EXP_ROOT="/home/mila/a/alejandra.zambrano/scratch/"
export AGENTXRAY_SHARE_GRADIO="true"
export OPENAI_API_KEY="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"



SUFFIX="az-1"


export WA_HOMEPAGE="https://wa-homepage-${SUFFIX}.mcgill-nlp.org"

export WA_SHOPPING="https://wa-shopping-${SUFFIX}.mcgill-nlp.org/"

export WA_SHOPPING_ADMIN="https://wa-shopping-admin-${SUFFIX}.mcgill-nlp.org/admin"

export WA_REDDIT="https://wa-forum-${SUFFIX}.mcgill-nlp.org"

export WA_GITLAB="https://wa-gitlab-${SUFFIX}.mcgill-nlp.org"

export WA_WIKIPEDIA="https://wa-wikipedia-${SUFFIX}.mcgill-nlp.org/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"

export WA_MAP="https://wa-openstreetmap-${SUFFIX}.mcgill-nlp.org"

export WA_FULL_RESET="https://wa-reset-${SUFFIX}.mcgill-nlp.org"


export WEBARENA_DISABLE_RESET="false"

export WEBARENA_REPRODUCIBILITY_MODE="true"

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

python3 main.py --config generic --n_jobs 2

python3 main.py --config generic --n_jobs 4 --relaunch True --contains 2025-04-22_18-26-12_generic-on-webarena-train_generic


