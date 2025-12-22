cd ..
export OPENROUTER_API_KEY="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"
export OPENAI_API_KEY="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"
export AGENTLAB_EXP_ROOT="/home/nlp/users/azambrano/agentlab_results/hardset_generation/"
SUFFIX="az-2"

export WA_HOMEPAGE="https://wa-homepage-${SUFFIX}.mcgill-nlp.org"
export WA_SHOPPING="https://wa-shopping-${SUFFIX}.mcgill-nlp.org/"
export WA_SHOPPING_ADMIN="https://wa-shopping-admin-${SUFFIX}.mcgill-nlp.org/admin"
export WA_REDDIT="https://wa-forum-${SUFFIX}.mcgill-nlp.org"
export WA_GITLAB="https://wa-gitlab-${SUFFIX}.mcgill-nlp.org"
export WA_WIKIPEDIA="https://wa-wikipedia-${SUFFIX}.mcgill-nlp.org/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export WA_MAP="https://wa-openstreetmap-${SUFFIX}.mcgill-nlp.org"
export WA_FULL_RESET="https://wa-reset-${SUFFIX}.mcgill-nlp.org"

#python3 main.py --config generic --n_jobs 4 --backend gemini  --run_set test --relaunch --contains 2025-12-17_20-22-21_generic-genericagent-google-gemini-2-5-flash-on-webarena-test_generic
#python3 main.py --config generic --n_jobs 4 --backend gemini  --run_set test --relaunch --contains 2025-12-17_21-06-25_generic-genericagent-google-gemini-2-5-flash-on-webarena-test_generic
python3 main.py --config generic --n_jobs 1 --backend gemini  --run_set test --relaunch --contains 2025-12-17_11-03-29_generic-genericagent-google-gemini-2-5-flash-on-webarena-test_generic 



