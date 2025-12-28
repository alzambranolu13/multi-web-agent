import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib

webarena_info = pd.read_json("data/test_raw.json")
print(webarena_info)

with open("data/hard_tasks.json", "r") as file:
    hard_tasks = json.load(file)

with open("data/easy_tasks.json", "r") as file:
    easy_tasks = json.load(file)

with open("data/medium_tasks.json", "r") as file:
    medium_tasks = json.load(file)


def do_counts(task_list):
    category_counts = {'GITLAB': 0, 'SHOPPING_ADMIN': 0, 'SHOPPING': 0, 'MAP': 0, 'REDDIT': 0 , "MULTI-SITE":0}
    multi_site = 0
    no_multi_site = 0
    for task in task_list:
        task_info = webarena_info[webarena_info["task_id"] == int(task)]
        category = task_info.get("start_url").item().split("__")[1]
        sites = task_info.get("sites").iloc[0]
        if len(sites) > 1:
            category_counts["MULTI-SITE"] += 1
            multi_site += 1
        else:
            no_multi_site += 1
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
    return category_counts
 


hard_counts = do_counts(hard_tasks)
medium_counts = do_counts(medium_tasks)
easy_counts = do_counts(easy_tasks)

print("Hard distribution:", hard_counts)
print("Medium distribution:", medium_counts)
print("Easy distribution:", easy_counts)


labels = ["Easy", "Medium", "Hard"]  # e.g., Train / Val / Test or three tasks

# ----- unify category order (sorted by total count for readability)
cats = sorted(easy_counts.keys(), key=lambda k: easy_counts.get(k,0)+medium_counts.get(k,0)+hard_counts.get(k,0), reverse=True)

# ----- prepare arrays
A = np.array([easy_counts[c] for c in cats])
B = np.array([medium_counts[c] for c in cats])
C = np.array([hard_counts[c] for c in cats])

totA, totB, totC = A.sum(), B.sum(), C.sum()

# percentages per series (each bar’s % of its own distribution)
pctA = A / totA * 100 if totA else np.zeros_like(A, dtype=float)
pctB = B / totB * 100 if totB else np.zeros_like(B, dtype=float)
pctC = C / totC * 100 if totC else np.zeros_like(C, dtype=float)

y = np.arange(len(cats))
bar_h = 0.22
gap = 0.04  # small gap between grouped bars

fig, ax = plt.subplots(figsize=(7.2, 3.8))  # good for two-column papers

# Matplotlib default color cycle keeps it simple and print-friendly

cmap = matplotlib.colormaps['Set2']
colors = [cmap(i) for i in range(3)]

barsA = ax.barh(y + (bar_h + gap), A, height=bar_h, label=labels[0], edgecolor='black', color=colors[0], linewidth=0.5, alpha=0.9)
barsB = ax.barh(y,                   B, height=bar_h, label=labels[1], edgecolor='black', color=colors[2],linewidth=0.5, alpha=0.9)
barsC = ax.barh(y - (bar_h + gap), C, height=bar_h, label=labels[2], edgecolor='black', color=colors[1],  linewidth=0.5, alpha=0.9)

# Add % labels to the right of each bar
def add_pct_labels(bars, pcts):
    for bar, pct in zip(bars, pcts):
        x = bar.get_width()
        y = bar.get_y() + bar.get_height()/2
        ax.text(x + max(0.01 * ax.get_xlim()[1], 1), y, f"{pct:.1f}%", va='center', ha='left', fontsize=9)

add_pct_labels(barsA, pctA)
add_pct_labels(barsB, pctB)
add_pct_labels(barsC, pctC)

# Axes, grid, legend
ax.set_yticks(y)
ax.set_yticklabels(cats, fontsize=10)
ax.set_xlabel("Count", fontsize=11)
#ax.set_title("Task Distributions by Difficulty Set (Counts with % of each set)", fontsize=11, pad=8)
ax.grid(axis='x', linestyle='--', alpha=0.4)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.legend(frameon=False, ncols=3, fontsize=9, handlelength=1.5, columnspacing=1.2)

# Make room for labels to the right
max_count = max(A.max(), B.max(), C.max())
ax.set_xlim(0, max_count * 1.35)

plt.tight_layout()
plt.savefig("figures/merged_task_distributions.pdf", bbox_inches="tight")  # vector for LaTeX
plt.savefig("figures/merged_task_distributions.png", dpi=300, bbox_inches="tight")  # high-res PNG
