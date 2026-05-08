"""
Build the headline chart for laundering_kappa_invariance_v1.

Three-panel composition (shared x-axis: β_guilt cells):
  TOP    — Per-agent total stored emotion CHANNELS (guilt vs loyalty),
            summed across the entire M store at end-of-ep4. Mirrors the
            κ=1.0 audit panel — should show the same channel-collapse
            shape (guilt drops, loyalty flat).
  MIDDLE — % of FAILURE-TAGGED memories whose CURRENT decayed emotion has
            stored.loyalty > stored.guilt at end-of-ep4 (the laundering
            rate). Overlay the κ=1.0 audit numbers as transparent reference
            bars to make the κ-invariance immediately legible.
  BOTTOM — Macro behavior at κ=0.5: ep0 rescue rate vs ep5–9 mean rescue
            rate per cell, showing that κ=0.5 sits in a flat low-rescue
            regime (the boomerang shoulder) while the laundering machinery
            is identical to κ=1.0.
"""
import csv, os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(HERE, "experiments", "laundering_kappa_invariance_v1")
SNAP_CSV = os.path.join(EXP_DIR, "memory_snapshot.csv")
RESULTS_CSV = os.path.join(EXP_DIR, "results.csv")
OUT_PNG = os.path.join(EXP_DIR, "laundering_kappa_invariance.png")

# Reference numbers from experiments/memory_population_audit_v1 (κ=1.0).
# (β_guilt, laundering %)
KAPPA_1_0_LAUNDERING = {0.05: 0.0, 0.15: 78.3, 0.30: 75.2, 0.50: 77.9}

# Theme
FIG_BG = "#0e131f"
AX_BG = "#131927"
GRID = "#1f2638"
TEXT = "#e8edf5"
ACCENT = "#ffe2ac"

C_GUILT = "#c084fc"
C_LOYALTY = "#4fc3f7"
C_KAPPA1 = "#7fffa1"   # reference bars (κ=1.0)


def _style_axes(ax):
    ax.set_facecolor(AX_BG)
    for spine in ax.spines.values():
        spine.set_color("#3a4055")
    ax.tick_params(colors=TEXT, which="both")
    ax.yaxis.label.set_color(TEXT)
    ax.xaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    ax.grid(True, color=GRID, linestyle="-", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def main():
    # --- Aggregate snapshot rows at end-of-ep4 ---
    g_total = defaultdict(float)
    l_total = defaultdict(float)
    n_agents = defaultdict(int)
    fail_count = defaultdict(int)
    fail_loy_dom = defaultdict(int)
    seen = set()
    with open(SNAP_CSV) as f:
        for row in csv.DictReader(f):
            if int(row["snapshot_after_ep"]) != 4:
                continue
            cell = float(row["beta_guilt"])
            aid = int(row["agent_id"])
            key = (cell, aid)
            if key not in seen:
                seen.add(key)
                n_agents[cell] += 1
            g_total[cell] += float(row["guilt"])
            l_total[cell] += float(row["loyalty"])
            if row["tag"] == "failure":
                fail_count[cell] += 1
                if float(row["loyalty"]) > float(row["guilt"]) + 1e-9:
                    fail_loy_dom[cell] += 1

    cells = sorted(g_total.keys())
    g_mean = [g_total[c] / n_agents[c] for c in cells]
    l_mean = [l_total[c] / n_agents[c] for c in cells]
    laundered = [
        100.0 * fail_loy_dom[c] / fail_count[c] if fail_count[c] else 0.0
        for c in cells
    ]
    laundered_k1 = [KAPPA_1_0_LAUNDERING.get(c, 0.0) for c in cells]

    # --- Aggregate macro outcomes ---
    ep0_resc = defaultdict(list)   # cell -> list of rescued{0,1} at ep0
    ep59_resc = defaultdict(list)
    with open(RESULTS_CSV) as f:
        for row in csv.DictReader(f):
            cell = float(row["beta_guilt"])
            ep = int(row["episode_idx"])
            r = int(row["rescued"])
            if ep == 0:
                ep0_resc[cell].append(r)
            elif 5 <= ep <= 9:
                ep59_resc[cell].append(r)
    ep0_rate = [100.0 * sum(ep0_resc[c]) / len(ep0_resc[c]) for c in cells]
    ep59_rate = [100.0 * sum(ep59_resc[c]) / len(ep59_resc[c]) for c in cells]

    # --- Build figure ---
    fig, axes = plt.subplots(
        3, 1, figsize=(11, 11), facecolor=FIG_BG,
        gridspec_kw={"height_ratios": [1.0, 1.0, 0.85], "hspace": 0.42},
    )
    ax1, ax2, ax3 = axes
    for ax in axes:
        _style_axes(ax)

    x = np.arange(len(cells))
    bw = 0.36
    cell_labels = [f"β_guilt={c:.2f}" for c in cells]

    # === TOP PANEL: stored channel totals at κ=0.5 ===
    bars_g = ax1.bar(x - bw/2, g_mean, bw, color=C_GUILT, edgecolor="#1a1e2c",
                     linewidth=0.5, label="Σ stored guilt per agent")
    bars_l = ax1.bar(x + bw/2, l_mean, bw, color=C_LOYALTY, edgecolor="#1a1e2c",
                     linewidth=0.5, label="Σ stored loyalty per agent")
    for bars in (bars_g, bars_l):
        for b in bars:
            h = b.get_height()
            ax1.text(b.get_x() + b.get_width() / 2, h + 0.025, f"{h:.2f}",
                     ha="center", va="bottom", color=TEXT, fontsize=9)

    ax1.set_ylabel("Σ |channel| over M, per agent")
    ax1.set_title(
        "κ=0.5 (boomerang shoulder) — same channel-collapse pattern as κ=1.0",
        loc="left", fontsize=13, weight="bold", pad=10,
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(cell_labels)
    ax1.set_ylim(0, max(max(g_mean), max(l_mean)) * 1.30)
    ax1.legend(facecolor=AX_BG, edgecolor="#3a4055", labelcolor=TEXT, loc="upper right")

    ratio = [g_mean[i] / l_mean[i] if l_mean[i] > 0 else float("nan") for i in range(len(cells))]
    for i, r in enumerate(ratio):
        ax1.text(i, -0.1, f"G/L = {r:.2f}", ha="center", va="top",
                 color=ACCENT, fontsize=10, fontweight="bold",
                 transform=ax1.get_xaxis_transform())

    # === MIDDLE PANEL: laundering rate at κ=0.5 vs κ=1.0 reference ===
    bars_k05 = ax2.bar(x - bw/2, laundered, bw, color=C_LOYALTY,
                       edgecolor="#1a1e2c", linewidth=0.5, label="κ=0.5 (this run)")
    bars_k10 = ax2.bar(x + bw/2, laundered_k1, bw, color=C_KAPPA1,
                       edgecolor="#1a1e2c", linewidth=0.5, alpha=0.55,
                       label="κ=1.0 (memory_population_audit_v1)")
    for b, v in zip(bars_k05, laundered):
        ax2.text(b.get_x() + b.get_width()/2, v + 2.5, f"{v:.0f}%",
                 ha="center", va="bottom", color=TEXT, fontsize=10, weight="bold")
    for b, v in zip(bars_k10, laundered_k1):
        ax2.text(b.get_x() + b.get_width()/2, v + 2.5, f"{v:.0f}%",
                 ha="center", va="bottom", color="#aab8a4", fontsize=9)
    # n on top
    for i, fc in enumerate([fail_count[c] for c in cells]):
        ax2.text(i - bw/2, 4, f"n={fc}", ha="center", va="bottom",
                 color="#aab8c8", fontsize=8)

    ax2.set_xticks(x)
    ax2.set_xticklabels(cell_labels)
    ax2.set_ylabel("% of failure-tagged memories\nwith loyalty > guilt at recall time")
    ax2.set_ylim(0, 100)
    ax2.set_title(
        "Laundering microstructure is κ-invariant — both regimes flip ~75–80% of "
        "failure memories",
        loc="left", fontsize=12.5, weight="bold", pad=10,
    )
    ax2.axhline(50, color=ACCENT, linewidth=0.8, linestyle="--", alpha=0.5, zorder=0)
    ax2.text(len(cells) - 0.5, 51.5, "50% threshold (majority-flipped)",
             color=ACCENT, fontsize=8, ha="right", va="bottom", alpha=0.8)
    ax2.legend(facecolor=AX_BG, edgecolor="#3a4055", labelcolor=TEXT, loc="upper left")

    # === BOTTOM PANEL: macro rescue rate at κ=0.5 ===
    bars_ep0 = ax3.bar(x - bw/2, ep0_rate, bw, color="#7fffa1",
                       edgecolor="#1a1e2c", linewidth=0.5, label="ep0 rescue (fresh)")
    bars_ep59 = ax3.bar(x + bw/2, ep59_rate, bw, color="#ff8db4",
                        edgecolor="#1a1e2c", linewidth=0.5, label="ep5–9 mean rescue")
    for bars in (bars_ep0, bars_ep59):
        for b in bars:
            h = b.get_height()
            ax3.text(b.get_x() + b.get_width()/2, h + 0.6, f"{h:.1f}%",
                     ha="center", va="bottom", color=TEXT, fontsize=9)
    ax3.set_xticks(x)
    ax3.set_xticklabels(cell_labels)
    ax3.set_ylabel("rescue rate (%)")
    ax3.set_ylim(0, max(max(ep0_rate), max(ep59_rate)) * 1.5 + 1)
    ax3.set_title(
        "Macro behavior at κ=0.5 — boomerang shoulder is a flat low-rescue regime "
        "regardless of decay asymmetry",
        loc="left", fontsize=12.5, weight="bold", pad=10,
    )
    ax3.legend(facecolor=AX_BG, edgecolor="#3a4055", labelcolor=TEXT, loc="upper right")

    fig.text(
        0.5, 0.012,
        "Snapshot at end of episode 4 across 100 agents per cell, β_loyalty=0.05 fixed, "
        "κ=0.5, T_snap=12, severity=1.0, chain_length=10, 4,000 episodes total. "
        "Reference bars in middle panel from experiments/memory_population_audit_v1 (κ=1.0).",
        ha="center", color="#9aa3b8", fontsize=9,
    )

    plt.savefig(OUT_PNG, dpi=140, facecolor=FIG_BG, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
