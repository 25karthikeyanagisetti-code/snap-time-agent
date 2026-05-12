"""
Build the headline 2-panel chart for tag_aware_injection_v1.

Left panel:  ep0 rescue rate per β_guilt cell, INJ-OFF vs INJ-ON.
Right panel: ep5-9 mean rescue rate per β_guilt cell, INJ-OFF vs INJ-ON.

Dark palette consistent with the rest of the repo.
"""
import csv, os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "tag_aware_injection_v1",
)
RESULTS_CSV = os.path.join(BASE, "results.csv")
OUT_PNG = os.path.join(BASE, "tag_aware_injection.png")

FACE = "#0e131f"
AXES_FACE = "#131927"
TEXT = "#e8edf5"
GRID = "#1f2638"
ACCENT = "#ffe2ac"

COLOR_OFF = "#4fc3f7"   # loyalty blue — INJ off (tag-aware recall only)
COLOR_ON = "#c084fc"    # guilt purple — INJ on (recall + injection)
COLOR_BASELINE = "#ff6b6b"  # survival red — symmetric reference


def load():
    rows = []
    with open(RESULTS_CSV) as f:
        for r in csv.DictReader(f):
            rows.append({
                "inj": int(r["tag_aware_injection"]),
                "bg": float(r["beta_guilt"]),
                "agent": int(r["agent_id"]),
                "ep": int(r["episode_idx"]),
                "rescued": int(r["rescued"]),
            })
    return rows


def summarize(rows):
    """Per (inj, bg): ep0 mean, ep5-9 mean."""
    buckets = defaultdict(list)
    ep0 = defaultdict(list)
    for r in rows:
        if 5 <= r["ep"] <= 9:
            buckets[(r["inj"], r["bg"])].append(r["rescued"])
        if r["ep"] == 0:
            ep0[(r["inj"], r["bg"])].append(r["rescued"])
    out = {}
    for k, v in buckets.items():
        out[k] = {"ep5_9": 100.0 * sum(v) / len(v)}
    for k, v in ep0.items():
        out.setdefault(k, {})["ep0"] = 100.0 * sum(v) / len(v)
        # Wilson-ish: report N for footnote
        out[k]["n_ep0"] = len(v)
    return out


def main():
    rows = load()
    S = summarize(rows)
    betas = [0.05, 0.15, 0.30, 0.50]

    ep0_off = [S[(0, b)]["ep0"] for b in betas]
    ep0_on = [S[(1, b)]["ep0"] for b in betas]
    ep59_off = [S[(0, b)]["ep5_9"] for b in betas]
    ep59_on = [S[(1, b)]["ep5_9"] for b in betas]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    fig.patch.set_facecolor(FACE)

    x = np.arange(len(betas))
    width = 0.35

    for ax in axes:
        ax.set_facecolor(AXES_FACE)
        ax.tick_params(colors=TEXT)
        for spine in ax.spines.values():
            spine.set_color(GRID)
        ax.grid(True, color=GRID, linewidth=0.7, axis="y")
        ax.set_axisbelow(True)

    # LEFT — ep0 rescue rate
    ax = axes[0]
    ax.bar(x - width/2, ep0_off, width, color=COLOR_OFF,
           label="INJ-OFF  (tag-aware recall only)", edgecolor=GRID)
    ax.bar(x + width/2, ep0_on, width, color=COLOR_ON,
           label="INJ-ON   (recall + tag-aware injection)", edgecolor=GRID)
    # Annotate deltas
    for xi, (a, b) in enumerate(zip(ep0_off, ep0_on)):
        d = b - a
        sign = "+" if d >= 0 else ""
        ax.text(xi, max(a, b) + 3.0, f"{sign}{d:.0f}",
                ha="center", color=ACCENT, fontsize=10, weight="bold")
    ax.set_xticks(x); ax.set_xticklabels([f"{b:.2f}" for b in betas], color=TEXT)
    ax.set_ylim(0, 100)
    ax.set_xlabel("β_guilt  (β_loyalty fixed = 0.05)", color=TEXT)
    ax.set_ylabel("ep0 rescue rate (%)", color=TEXT)
    ax.set_title("Episode 0  rescue rate  —  before any laundering",
                 color=TEXT, fontsize=12, weight="bold")
    leg = ax.legend(loc="lower left", facecolor=AXES_FACE, edgecolor=GRID)
    for t in leg.get_texts():
        t.set_color(TEXT)

    # RIGHT — ep5-9 mean rescue rate
    ax = axes[1]
    ax.bar(x - width/2, ep59_off, width, color=COLOR_OFF,
           label="INJ-OFF  (tag-aware recall only)", edgecolor=GRID)
    ax.bar(x + width/2, ep59_on, width, color=COLOR_ON,
           label="INJ-ON   (recall + tag-aware injection)", edgecolor=GRID)
    for xi, (a, b) in enumerate(zip(ep59_off, ep59_on)):
        d = b - a
        sign = "+" if d >= 0 else ""
        ax.text(xi, max(a, b) + 1.6, f"{sign}{d:.1f}",
                ha="center", color=ACCENT, fontsize=10, weight="bold")
    ax.set_xticks(x); ax.set_xticklabels([f"{b:.2f}" for b in betas], color=TEXT)
    ax.set_ylim(0, 60)
    ax.set_xlabel("β_guilt  (β_loyalty fixed = 0.05)", color=TEXT)
    ax.set_ylabel("ep5–9 mean rescue rate (%)", color=TEXT)
    ax.set_title("Episode 5–9 mean  —  long-run committed-rescuer regime",
                 color=TEXT, fontsize=12, weight="bold")
    leg = ax.legend(loc="lower left", facecolor=AXES_FACE, edgecolor=GRID)
    for t in leg.get_texts():
        t.set_color(TEXT)

    # Suptitle
    fig.suptitle(
        "Tag-Aware Injection — the residual β_guilt=0.50 ep0 collapse is NOT closed",
        color=TEXT, fontsize=13.5, weight="bold", y=0.99,
    )
    fig.text(
        0.5, 0.012,
        "N=50 agents per cell · κ=1.0 · T_snap=12 · chain=10 episodes · "
        "tag-aware recall always ON · ablation: tag-aware INJECTION",
        ha="center", color=TEXT, fontsize=9, alpha=0.85,
    )
    plt.tight_layout(rect=[0, 0.035, 1, 0.95])
    plt.savefig(OUT_PNG, facecolor=FACE, dpi=140, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")

    # Also print the structured summary for the README table
    print()
    print("β_guilt | INJ-OFF ep0 | INJ-ON ep0 | Δep0 | INJ-OFF ep5-9 | INJ-ON ep5-9 | Δep5-9")
    for i, b in enumerate(betas):
        print(f"{b:.2f}    | {ep0_off[i]:5.1f}%      | {ep0_on[i]:5.1f}%     | "
              f"{ep0_on[i]-ep0_off[i]:+5.1f} | {ep59_off[i]:5.1f}%        | "
              f"{ep59_on[i]:5.1f}%       | {ep59_on[i]-ep59_off[i]:+5.1f}")


if __name__ == "__main__":
    main()
