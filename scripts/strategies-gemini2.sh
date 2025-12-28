cd ..
export OPENROUTER_API_KEY="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"
export OPENAI_API_KEY="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"

export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/strategies-gemini/strategy_2/"
SUFFIX="az-3"

export WA_HOMEPAGE="https://wa-homepage-${SUFFIX}.mcgill-nlp.org"
export WA_SHOPPING="https://wa-shopping-${SUFFIX}.mcgill-nlp.org/"
export WA_SHOPPING_ADMIN="https://wa-shopping-admin-${SUFFIX}.mcgill-nlp.org/admin"
export WA_REDDIT="https://wa-forum-${SUFFIX}.mcgill-nlp.org"
export WA_GITLAB="https://wa-gitlab-${SUFFIX}.mcgill-nlp.org"
export WA_WIKIPEDIA="https://wa-wikipedia-${SUFFIX}.mcgill-nlp.org/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="https://wa-openstreetmap-${SUFFIX}.mcgill-nlp.org"
export WA_FULL_RESET="https://wa-reset-${SUFFIX}.mcgill-nlp.org"



python3 main.py --config CPFixed --n_jobs 1 --reproduce --strategy strategy_2 --prompt_opt 5 --backend gemini --run_set hard --relaunch --contains 2025-12-21_02-07-26_cpfixed-controllercpfixed-google-gemini-2-5-flash-on-webarena-hard_strategy_2_v5 
python3 main.py --config CPFixed --n_jobs 1 --reproduce --strategy strategy_2 --prompt_opt 5 --backend gemini --run_set hard --relaunch --contains 2025-12-20_16-21-38_cpfixed-controllercpfixed-google-gemini-2-5-flash-on-webarena-hard_strategy_2_v5
python3 main.py --config CPFixed --n_jobs 1 --reproduce --strategy strategy_2 --prompt_opt 5 --backend gemini --run_set hard --relaunch --contains 2025-12-21_23-23-54_cpfixed-controllercpfixed-google-gemini-2-5-flash-on-webarena-hard_strategy_2_v5