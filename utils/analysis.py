"""
Script to analyze and visualize task distribution by difficulty and category.

This script creates visualizations showing the distribution of tasks across
different difficulty levels (easy, medium, hard) and categories (GITLAB, SHOPPING, etc.).
"""
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

webarena_info = pd.read_json("data/test_raw.json")
logger.debug(f"Loaded WebArena info: {len(webarena_info)} tasks")


def do_counts(task_list):
    """
    Count tasks by category and multi-site status.
    
    Args:
        task_list: List of task IDs to count
        
    Returns:
        Dictionary with category counts
    """
    category_counts = {'GITLAB': 0, 'SHOPPING_ADMIN': 0, 'SHOPPING': 0, 'MAP': 0, 'REDDIT': 0, "MULTI-SITE": 0}
    for task in task_list:
        task_info = webarena_info[webarena_info["task_id"] == int(task)]
        category = task_info.get("start_url").item().split("__")[1]
        sites = task_info.get("sites").iloc[0]
        if len(sites) > 1:
            category_counts["MULTI-SITE"] += 1
        else:
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
    return category_counts
 


if __name__ == "__main__":
    with open("data/hard_tasks.json", "r") as file:
        hard_tasks = json.load(file)

    with open("data/easy_tasks.json", "r") as file:
        easy_tasks = json.load(file)

    with open("data/medium_tasks.json", "r") as file:
        medium_tasks = json.load(file)

    hard_counts = do_counts(hard_tasks)
    medium_counts = do_counts(medium_tasks)
    easy_counts = do_counts(easy_tasks)

    logger.info(f"Hard distribution: {hard_counts}")
    logger.info(f"Medium distribution: {medium_counts}")
    logger.info(f"Easy distribution: {easy_counts}")

    labels = ["Easy", "Medium", "Hard"]

    # Unify category order (sorted by total count for readability)
    cats = sorted(easy_counts.keys(), key=lambda k: easy_counts.get(k, 0) + medium_counts.get(k, 0) + hard_counts.get(k, 0), reverse=True)

    # Prepare arrays
    A = np.array([easy_counts[c] for c in cats])
    B = np.array([medium_counts[c] for c in cats])
    C = np.array([hard_counts[c] for c in cats])

    totA, totB, totC = A.sum(), B.sum(), C.sum()

    # Percentages per series (each bar's % of its own distribution)
    pctA = A / totA * 100 if totA else np.zeros_like(A, dtype=float)
    pctB = B / totB * 100 if totB else np.zeros_like(B, dtype=float)
    pctC = C / totC * 100 if totC else np.zeros_like(C, dtype=float)

    y = np.arange(len(cats))
    bar_h = 0.22
    gap = 0.04  # Small gap between grouped bars

    fig, ax = plt.subplots(figsize=(7.2, 3.8))  # Good for two-column papers

    cmap = matplotlib.colormaps['Set2']
    colors = [cmap(i) for i in range(3)]

    barsA = ax.barh(y + (bar_h + gap), A, height=bar_h, label=labels[0], edgecolor='black', color=colors[0], linewidth=0.5, alpha=0.9)
    barsB = ax.barh(y, B, height=bar_h, label=labels[1], edgecolor='black', color=colors[2], linewidth=0.5, alpha=0.9)
    barsC = ax.barh(y - (bar_h + gap), C, height=bar_h, label=labels[2], edgecolor='black', color=colors[1], linewidth=0.5, alpha=0.9)

    # Add % labels to the right of each bar
    def add_pct_labels(bars, pcts):
        for bar, pct in zip(bars, pcts):
            x = bar.get_width()
            y = bar.get_y() + bar.get_height() / 2
            ax.text(x + max(0.01 * ax.get_xlim()[1], 1), y, f"{pct:.1f}%", va='center', ha='left', fontsize=9)

    add_pct_labels(barsA, pctA)
    add_pct_labels(barsB, pctB)
    add_pct_labels(barsC, pctC)

    # Axes, grid, legend
    ax.set_yticks(y)
    ax.set_yticklabels(cats, fontsize=10)
    ax.set_xlabel("Count", fontsize=11)
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.legend(frameon=False, ncols=3, fontsize=9, handlelength=1.5, columnspacing=1.2)

    # Make room for labels to the right
    max_count = max(A.max(), B.max(), C.max())
    ax.set_xlim(0, max_count * 1.35)

    plt.tight_layout()
    plt.savefig("figures/merged_task_distributions.pdf", bbox_inches="tight")  # Vector for LaTeX
    plt.savefig("figures/merged_task_distributions.png", dpi=300, bbox_inches="tight")  # High-res PNG
    logger.info("Visualization saved to figures/merged_task_distributions.{pdf,png}")
