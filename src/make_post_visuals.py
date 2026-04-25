"""
Generate LinkedIn-ready visualizations from the regime_map_v1 results.

Three charts:
  1. paralysis_valley_hero.png  — annotated failure curve (the headline visual)
  2. memory_on_vs_off.png        — bar comparison showing the valley needs memory
  3. regime_map.png              — 3-zone strip labeling rational/paralyzed/committed

Run: python -m src.make_post_visuals
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

EXP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "regime_map_v1"
)
CSV = os.path.join(EXP_DIR, "results.csv")


def load_failures():
    """Returns failure_rate[(t_snap, kappa, seeded)] = fraction of episodes
    that ended in TIMEOUT or PARTNER_DEAD."""
    by_cell = defaultdict(list)
    with open(CSV) as f:
        for r in csv.DictReader(f):
            t = int(r["t_snap"])
            k = float(r["kappa"])
            s = int(r["seeded_memory"])
            by_cell[(t, k, s)].append(r["outcome"])
    out = {}
    for cell, outcomes in by_cell.items():
        n = len(outcomes)
        fail = sum(1 for o in outcomes if o in ("TIMEOUT", "PARTNER_DEAD")) / n
        out[cell] = fail
    return out


# ─── chart 1: hero failure curve ──────────────────────────────────────────────
def hero_chart(failures, kappas, t_snaps_to_plot):
    fig, ax = plt.subplots(figsize=(11, 7))

    # Plot only the meaningful T_snap values (drop 3, 5 which are flat 1.0)
    colors = ["#d62728", "#ff7f0e", "#9467bd", "#2ca02c"]
    for i, t in enumerate(t_snaps_to_plot):
        ys = [failures[(t, k, 1)] * 100 for k in kappas]
        ax.plot(kappas, ys, marker="o", linewidth=2.6, markersize=9,
                label=f"Snap Time = {t}", color=colors[i % len(colors)])

    # Shade the paralysis valley (kappa range 0.15 to 0.7)
    ax.axvspan(0.15, 0.7, alpha=0.15, color="#d62728")
    ax.text(0.42, 92, "PARALYSIS VALLEY",
            fontsize=15, fontweight="bold", color="#a01010",
            ha="center", va="center")

    # Annotate worst point
    worst_t, worst_k, worst_v = max(
        ((t, k, failures[(t, k, 1)]) for t in t_snaps_to_plot for k in kappas
         if 0.1 < k < 0.6),
        key=lambda x: x[2]
    )
    ax.annotate(
        f"{worst_v*100:.0f}% failure\n@ κ={worst_k}",
        xy=(worst_k, worst_v * 100),
        xytext=(worst_k + 0.6, worst_v * 100 - 3),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
        fontsize=11, fontweight="bold",
    )

    ax.set_xlabel("κ — emotion weight in decisions", fontsize=14)
    ax.set_ylabel("Failure rate (%)", fontsize=14)
    ax.set_title(
        "A small amount of emotion makes the agent fail MORE than no emotion.\n"
        "Failure peaks in the middle, not at the extremes.",
        fontsize=14, pad=15
    )
    ax.set_ylim(-5, 105)
    ax.set_xlim(-0.15, 4.2)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=12, framealpha=0.95)
    ax.tick_params(labelsize=11)

    plt.tight_layout()
    out = os.path.join(EXP_DIR, "paralysis_valley_hero.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


# ─── chart 2: memory on vs off bar comparison ─────────────────────────────────
def comparison_chart(failures, kappas, t_snap=12):
    fig, ax = plt.subplots(figsize=(11, 6.5))

    seeded   = [failures[(t_snap, k, 1)] * 100 for k in kappas]
    no_mem   = [failures[(t_snap, k, 0)] * 100 for k in kappas]

    x = np.arange(len(kappas))
    w = 0.38

    bars1 = ax.bar(x - w/2, seeded, w,
                   label="With seeded emotional memory",
                   color="#d62728", edgecolor="black", linewidth=0.5)
    bars2 = ax.bar(x + w/2, no_mem, w,
                   label="No memory (control)",
                   color="#7f7f7f", edgecolor="black", linewidth=0.5)

    # Value labels on top
    for bars in (bars1, bars2):
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, h + 1.5, f"{h:.0f}%",
                    ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels([f"κ={k}" for k in kappas])
    ax.set_ylabel("Failure rate (%)", fontsize=13)
    ax.set_title(
        f"The Paralysis Valley exists ONLY when emotional memory is present.\n"
        f"(Snap Time = {t_snap}, 200 episodes per cell)",
        fontsize=13, pad=12
    )
    ax.set_ylim(0, 110)
    ax.legend(loc="upper right", fontsize=11)
    ax.grid(alpha=0.25, axis="y")
    ax.tick_params(labelsize=11)

    plt.tight_layout()
    out = os.path.join(EXP_DIR, "memory_on_vs_off.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


# ─── chart 3: 3-zone regime strip ─────────────────────────────────────────────
def regime_map(failures, kappas, t_snap=12):
    fig, ax = plt.subplots(figsize=(12, 6))

    fails    = [failures[(t_snap, k, 1)] * 100 for k in kappas]

    # Background zones
    ax.axvspan(-0.2, 0.12,  color="#9ed09e", alpha=0.35, label="_")
    ax.axvspan(0.12, 0.85,  color="#e57373", alpha=0.35, label="_")
    ax.axvspan(0.85, 4.5,   color="#7eb6e0", alpha=0.35, label="_")

    # Zone labels — placed in a header band ABOVE the data
    ax.text(0.0,   125, "RATIONAL",
            fontsize=14, fontweight="bold", ha="center", va="center", color="#1f5d1f")
    ax.text(0.0,   115, "(grabs resource)",
            fontsize=10, ha="center", va="center", color="#1f5d1f")

    ax.text(0.49,  125, "PARALYZED",
            fontsize=14, fontweight="bold", ha="center", va="center", color="#a01010")
    ax.text(0.49,  115, "(can't decide)",
            fontsize=10, ha="center", va="center", color="#a01010")

    ax.text(2.6,   125, "COMMITTED",
            fontsize=14, fontweight="bold", ha="center", va="center", color="#15498a")
    ax.text(2.6,   115, "(rescues partner)",
            fontsize=10, ha="center", va="center", color="#15498a")

    ax.plot(kappas, fails, "o-", linewidth=3.0, markersize=11, color="black")
    for k, v in zip(kappas, fails):
        offset = 5 if v < 95 else -8
        va = "bottom" if v < 95 else "top"
        ax.text(k, v + offset, f"{v:.0f}%", ha="center", va=va,
                fontsize=11, fontweight="bold")

    ax.set_xlabel("κ — emotion weight", fontsize=13)
    ax.set_ylabel("Failure rate (%)", fontsize=13)
    ax.set_title(
        f"Three behavior regimes emerge as emotion weight increases\n"
        f"(Snap Time = {t_snap}, with seeded memory)",
        fontsize=13, pad=12
    )
    ax.set_ylim(-5, 135)
    ax.set_xlim(-0.2, 4.4)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.grid(alpha=0.25)
    ax.tick_params(labelsize=11)

    plt.tight_layout()
    out = os.path.join(EXP_DIR, "regime_map.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


def main():
    failures = load_failures()
    kappas = sorted({k for (_, k, _) in failures.keys()})
    t_snaps = sorted({t for (t, _, _) in failures.keys()})

    hero_chart(failures, kappas, t_snaps_to_plot=[8, 12, 20, 40])
    comparison_chart(failures, kappas, t_snap=12)
    regime_map(failures, kappas, t_snap=12)


if __name__ == "__main__":
    main()
