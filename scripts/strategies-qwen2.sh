cd ..
export OPENAI_API_KEY="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"

export VLLM_API_KEY="vllm-mg5sPKx4W5NqF"
export VLLM_BASE_URL="https://vllm.mcgill-nlp.org/v1"

export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/strategies-qwen/"
SUFFIX="az-4"

export WA_HOMEPAGE="https://wa-homepage-${SUFFIX}.mcgill-nlp.org"
export WA_SHOPPING="https://wa-shopping-${SUFFIX}.mcgill-nlp.org/"
export WA_SHOPPING_ADMIN="https://wa-shopping-admin-${SUFFIX}.mcgill-nlp.org/admin"
export WA_REDDIT="https://wa-forum-${SUFFIX}.mcgill-nlp.org"
export WA_GITLAB="https://wa-gitlab-${SUFFIX}.mcgill-nlp.org"
export WA_WIKIPEDIA="https://wa-wikipedia-${SUFFIX}.mcgill-nlp.org/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="https://wa-openstreetmap-${SUFFIX}.mcgill-nlp.org"
export WA_FULL_RESET="https://wa-reset-${SUFFIX}.mcgill-nlp.org"



python3 main.py --config CPFixed --n_jobs 2 --reproduce --strategy strategy_3 --prompt_opt 3 --backend qwen --run_set hard --relaunch --contains 2025-05-16_12-07-06_cpfixed-controllercpfixed-qwen-qwen2-5-vl-72b-instruct-on-webarena-test_strategy_3_v3
python3 main.py --config CPFixed --n_jobs 2 --reproduce --strategy strategy_3 --prompt_opt 3 --backend qwen --run_set hard 
python3 main.py --config CPFixed --n_jobs 2 --reproduce --strategy strategy_3 --prompt_opt 3 --backend qwen --run_set hard 
python3 main.py --config CPFixed --n_jobs 2 --reproduce --strategy strategy_3 --prompt_opt 3 --backend qwen --run_set hard 
python3 main.py --config CPFixed --n_jobs 2 --reproduce --strategy strategy_3 --prompt_opt 3 --backend qwen --run_set hard 
