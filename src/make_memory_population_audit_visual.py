"""
Build the headline chart for memory_population_audit_v1.

Two-panel composition (shared x-axis: β_guilt cells):
  TOP    — Per-agent total stored emotion CHANNELS (guilt vs loyalty),
            summed across the entire M store at end-of-ep4. Shows the
            channel-collapse: guilt total drops ~50% from cell A → C while
            loyalty total stays flat.
  BOTTOM — % of FAILURE-TAGGED memories whose CURRENT decayed emotion has
            stored.loyalty > stored.guilt (the "laundered" fraction). This
            is the mechanism number: failure memories that no longer look
            like failure memories during recall.
"""
import csv, os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(HERE, "experiments", "memory_population_audit_v1")
SNAP_CSV = os.path.join(EXP_DIR, "memory_snapshot.csv")
OUT_PNG = os.path.join(EXP_DIR, "memory_population_audit.png")

# Theme (matches existing experiments)
FIG_BG = "#0e131f"
AX_BG = "#131927"
GRID = "#1f2638"
TEXT = "#e8edf5"
ACCENT = "#ffe2ac"

C_SURVIVAL = "#ff6b6b"
C_GUILT = "#c084fc"
C_LOYALTY = "#4fc3f7"
C_FEAR = "#ffd166"
C_CURIOSITY = "#7fffa1"


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
    # Aggregate snapshot rows at end-of-ep4
    g_total = defaultdict(float)   # cell -> sum of stored guilt over all memories
    l_total = defaultdict(float)   # cell -> sum of stored loyalty over all memories
    n_agents = defaultdict(int)
    fail_count = defaultdict(int)
    fail_loy_dom = defaultdict(int)

    seen_agent_cell = set()

    with open(SNAP_CSV) as f:
        for row in csv.DictReader(f):
            if int(row["snapshot_after_ep"]) != 4:
                continue
            cell = float(row["beta_guilt"])
            aid = int(row["agent_id"])
            key = (cell, aid)
            if key not in seen_agent_cell:
                seen_agent_cell.add(key)
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

    # Build figure
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 8), facecolor=FIG_BG,
        gridspec_kw={"height_ratios": [1.1, 1.0], "hspace": 0.32},
    )
    _style_axes(ax1)
    _style_axes(ax2)

    x = np.arange(len(cells))
    bw = 0.36
    cell_labels = [f"β_guilt={c:.2f}" for c in cells]

    # === TOP PANEL: stored channel totals ===
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
        "Memory Laundering — asymmetric forgiveness collapses the guilt channel "
        "while leaving loyalty flat",
        loc="left", fontsize=13, weight="bold", pad=10,
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(cell_labels)
    ax1.set_ylim(0, max(max(g_mean), max(l_mean)) * 1.25)
    ax1.legend(facecolor=AX_BG, edgecolor="#3a4055", labelcolor=TEXT, loc="upper right")

    # Annotation: G/L ratio drift
    ratio = [g_mean[i] / l_mean[i] if l_mean[i] > 0 else float("nan") for i in range(len(cells))]
    for i, r in enumerate(ratio):
        ax1.text(i, -0.1, f"G/L = {r:.2f}", ha="center", va="top",
                 color=ACCENT, fontsize=10, fontweight="bold",
                 transform=ax1.get_xaxis_transform())

    # === BOTTOM PANEL: % of failure-tagged memories now loyalty-dominant ===
    bar_colors = [C_GUILT if v < 5.0 else "#ff8db4" for v in laundered]
    bars_f = ax2.bar(x, laundered, bw * 1.6, color=bar_colors,
                     edgecolor="#1a1e2c", linewidth=0.5)
    for b, v, fc in zip(bars_f, laundered, [fail_count[c] for c in cells]):
        ax2.text(b.get_x() + b.get_width()/2, v + 2.5, f"{v:.0f}%",
                 ha="center", va="bottom", color=TEXT, fontsize=11, weight="bold")
        # Place n-label just above the bar; for the v=0 bar, place above 0%
        n_y = max(v - 5.0, 4.0) if v >= 8.0 else v + 9.0
        ax2.text(b.get_x() + b.get_width()/2, n_y, f"n={fc}",
                 ha="center", va="top" if v >= 8.0 else "bottom",
                 color=TEXT, fontsize=8)

    ax2.set_xticks(x)
    ax2.set_xticklabels(cell_labels)
    ax2.set_ylabel("% of failure-tagged memories\nwith loyalty > guilt at recall time")
    ax2.set_ylim(0, 100)
    ax2.set_title(
        "Failure-tagged memories that are now loyalty-class at recall — "
        "the outcome ledger flips",
        loc="left", fontsize=12.5, weight="bold", pad=10,
    )

    # Reference line at 0 (the "no laundering" baseline)
    ax2.axhline(0, color="#3a4055", linewidth=1, zorder=0)
    ax2.axhline(50, color=ACCENT, linewidth=0.8, linestyle="--", alpha=0.5, zorder=0)
    ax2.text(len(cells) - 0.5, 51.5, "50% threshold (majority-flipped)",
             color=ACCENT, fontsize=8, ha="right", va="bottom", alpha=0.8)

    # Footer caption
    fig.text(
        0.5, 0.012,
        "Snapshot at end of episode 4 across 100 agents per cell, β_loyalty=0.05 fixed, κ=1.0, "
        "T_snap=12, severity=1.0, chain_length=10. n on bars = failure-tagged memories pooled across agents.",
        ha="center", color="#9aa3b8", fontsize=9,
    )

    plt.savefig(OUT_PNG, dpi=140, facecolor=FIG_BG, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
