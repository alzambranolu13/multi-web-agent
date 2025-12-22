cd ..
export OPENAI_API_KEY="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"
export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/strategies-41mini/strategy_1/"
SUFFIX="az-3"

export WA_HOMEPAGE="https://wa-homepage-${SUFFIX}.mcgill-nlp.org"
export WA_SHOPPING="https://wa-shopping-${SUFFIX}.mcgill-nlp.org/"
export WA_SHOPPING_ADMIN="https://wa-shopping-admin-${SUFFIX}.mcgill-nlp.org/admin"
export WA_REDDIT="https://wa-forum-${SUFFIX}.mcgill-nlp.org"
export WA_GITLAB="https://wa-gitlab-${SUFFIX}.mcgill-nlp.org"
export WA_WIKIPEDIA="https://wa-wikipedia-${SUFFIX}.mcgill-nlp.org/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="https://wa-openstreetmap-${SUFFIX}.mcgill-nlp.org"
export WA_FULL_RESET="https://wa-reset-${SUFFIX}.mcgill-nlp.org"


python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_1 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-05_13-53-10_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_1_v3 
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_1 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-06_11-32-04_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_1_v3

export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/strategies-41mini/strategy_2/"
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_2 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-09_09-06-51_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_2_v3 

export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/strategies-41mini/strategy_3/"
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_3 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-07_15-05-07_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_3_v3
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_3 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-09_09-27-36_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_3_v3 

export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/strategies-41mini/strategy_4/"
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_4 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-07_21-54-42_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_4_v3 
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_4 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-08_11-31-14_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_4_v3
python3 main.py --config CPFixed --n_jobs 4 --reproduce --strategy strategy_4 --prompt_opt 3 --backend 41-mini --run_set easy --relaunch --contains 2025-09-08_14-03-54_cpfixed-controllercpfixed-gpt-4-1-mini-on-webarena-hard_strategy_4_v3