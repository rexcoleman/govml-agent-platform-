#!/usr/bin/env python
"""Generate figures for FP-08."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def setup_time():
    generations = ["FP-01\nManual\n(2024)", "FP-05\ngovML v2.4\n--fill", "FP-03\nblog-track\n+ G17", "FP-08\nMCP\n(projected)"]
    times = [60, 30, 10, 5]
    colors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71"]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(generations, times, color=colors, edgecolor="#2c3e50", linewidth=1.2)
    for bar, t in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{t} min", ha="center", fontweight="bold", fontsize=12)
    ax.set_ylabel("Setup Time (minutes)", fontsize=12)
    ax.set_title("Project Setup Time: 4 Generations of Automation", fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.annotate("90% reduction", xy=(3, 5), xytext=(2.5, 35),
               fontsize=12, fontweight="bold", color="#27ae60",
               arrowprops=dict(arrowstyle="->", color="#27ae60"))
    plt.tight_layout()
    for p in ["outputs/figures/setup_time.png", "blog/images/setup_time.png"]:
        Path(p).parent.mkdir(parents=True, exist_ok=True); plt.savefig(p, dpi=150)
    print("Generated: setup_time.png")

def agent_boundary():
    categories = ["Agent-Safe\n(automated)", "Human-Required\n(judgment)"]
    counts = [6, 5]
    colors = ["#3498db", "#e74c3c"]
    items_agent = "Template filling\nGate checking\nRepo hygiene\nConfig validation\nADR formatting\nPublication checklist"
    items_human = "Thesis formulation\nRQ design\nFinding interpretation\nTradeoff judgment\nBlog voice"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.barh([0], [6], color="#3498db", height=0.5, edgecolor="#2c3e50")
    ax1.barh([0], [5], left=[6], color="#e74c3c", height=0.5, edgecolor="#2c3e50")
    ax1.set_xlim(0, 11); ax1.set_yticks([]); ax1.set_xlabel("Tasks")
    ax1.set_title("Agent vs Human Governance Tasks", fontweight="bold")
    ax1.text(3, 0, "6 Agent", ha="center", va="center", fontweight="bold", color="white", fontsize=12)
    ax1.text(8.5, 0, "5 Human", ha="center", va="center", fontweight="bold", color="white", fontsize=12)
    ax2.axis("off")
    ax2.text(0.05, 0.95, "Agent-Safe:", fontweight="bold", fontsize=11, va="top", color="#3498db", transform=ax2.transAxes)
    ax2.text(0.05, 0.85, items_agent, fontsize=10, va="top", transform=ax2.transAxes, family="monospace")
    ax2.text(0.55, 0.95, "Human-Required:", fontweight="bold", fontsize=11, va="top", color="#e74c3c", transform=ax2.transAxes)
    ax2.text(0.55, 0.85, items_human, fontsize=10, va="top", transform=ax2.transAxes, family="monospace")
    plt.tight_layout()
    for p in ["outputs/figures/agent_boundary.png", "blog/images/agent_boundary.png"]:
        plt.savefig(p, dpi=150)
    print("Generated: agent_boundary.png")

if __name__ == "__main__":
    print("Generating FP-08 figures...")
    setup_time(); agent_boundary()
    print("Done.")
