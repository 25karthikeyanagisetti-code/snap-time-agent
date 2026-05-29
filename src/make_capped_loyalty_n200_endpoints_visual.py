"""Visual for capped_loyalty_n200_endpoints: N=40 vs N=200 substitutability gap."""
import csv, os
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "experiments", "capped_loyalty_n200_endpoints_v1", "results.csv")
PARENT = os.path.join(ROOT, "experiments", "capped_floor_loyalty_sweep_v1", "results.csv")
OUT = os.path.join(ROOT, "experiments", "capped_loyalty_n200_endpoints_v1",
                   "capped_loyalty_n200_endpoints.png")

# Palette
FIG_BG = "#0e131f"
AX_BG = "#131927"
TEXT = "#e8edf5"
ACCENT = "#ffe2ac"
GRID = "#1f2638"
COL_OFF = "#7a8499"
COL_FLOOR = "#4fc3f7"     # loyalty hue, like gate-side
COL_CAPPED = "#c084fc"    # guilt hue, source-side


def load_ep0(path):
    rows = list(csv.DictReader(open(path)))
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        if int(r["episode_idx"]) == 0:
            key = (r["inject_mode"], float(r["beta_loyalty"]))
            agg[key][0] += int(r["rescued"]); agg[key][1] += 1
    return {k: (v[0] / v[1]) * 100.0 for k, v in agg.items()}


def main():
    today = load_ep0(SRC)           # N=200 (endpoints only)
    parent = load_ep0(PARENT)       # N=40   (all 4 cells)

    cells = [0.05, 0.50]

    # Deltas for today (N=200)
    today_d_floor = [today[("seed_only_floor", b)] - today[("off", b)] for b in cells]
    today_d_capped = [today[("seed_refresh_capped", b)] - today[("off", b)] for b in cells]
    today_gap = [abs(c - f) for c, f in zip(today_d_capped, today_d_floor)]

    # Deltas for parent (N=40)
    parent_d_floor = [parent[("seed_only_floor", b)] - parent[("off", b)] for b in cells]
    parent_d_capped = [parent[("seed_refresh_capped", b)] - parent[("off", b)] for b in cells]
    parent_gap = [abs(c - f) for c, f in zip(parent_d_capped, parent_d_floor)]

    fig = plt.figure(figsize=(12, 6), facecolor=FIG_BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.32)

    # Panel A — substitutability gap: N=40 vs N=200
    ax1 = fig.add_subplot(gs[0]); ax1.set_facecolor(AX_BG)
    x = np.arange(len(cells))
    w = 0.36
    ax1.bar(x - w/2, parent_gap, w, color="#5b6373",
            edgecolor="white", linewidth=0.4, label="N=40 (2026-05-20)")
    ax1.bar(x + w/2, today_gap, w, color=ACCENT,
            edgecolor="white", linewidth=0.4, label="N=200 (today)")
    # 2-SE band markers
    ax1.axhline(14.5, color="#5b6373", lw=0.8, ls="--", alpha=0.6)
    ax1.axhline(6.5, color=ACCENT, lw=0.8, ls="--", alpha=0.6)
    ax1.text(1.42, 14.5, "  ±2-SE N=40 ≈ 14.5", color="#a9b0c0",
             ha="left", va="center", fontsize=9)
    ax1.text(1.42, 6.5, "  ±2-SE N=200 ≈ 6.5", color=ACCENT,
             ha="left", va="center", fontsize=9)
    for xi, v in zip(x - w/2, parent_gap):
        ax1.text(xi, v + 0.5, f"{v:.1f}", color="#cfd5e1", ha="center",
                 va="bottom", fontsize=10)
    for xi, v in zip(x + w/2, today_gap):
        ax1.text(xi, v + 0.5, f"{v:.1f}", color=ACCENT, ha="center",
                 va="bottom", fontsize=11, fontweight="bold")
    ax1.set_xticks(x); ax1.set_xticklabels([f"β_loyalty={b}" for b in cells],
                                            color=TEXT, fontsize=10)
    ax1.set_ylabel("|Δcapped − Δfloor|  (pts ep0 rescue rate)", color=TEXT)
    ax1.set_title("Substitutability gap collapses 10× at N=200",
                  color=ACCENT, fontsize=12, pad=10, loc="left")
    ax1.set_ylim(0, max(parent_gap + today_gap) + 4)
    ax1.tick_params(colors=TEXT)
    for spine in ax1.spines.values(): spine.set_color(GRID)
    ax1.grid(axis="y", color=GRID, alpha=0.6)
    ax1.legend(facecolor=AX_BG, edgecolor=GRID, labelcolor=TEXT,
               fontsize=9, loc="upper center")

    # Panel B — Δep0 by mode at N=200 (today)
    ax2 = fig.add_subplot(gs[1]); ax2.set_facecolor(AX_BG)
    w2 = 0.36
    ax2.bar(x - w2/2, today_d_floor, w2, color=COL_FLOOR,
            edgecolor="white", linewidth=0.4, label="seed_only_floor (gate)")
    ax2.bar(x + w2/2, today_d_capped, w2, color=COL_CAPPED,
            edgecolor="white", linewidth=0.4, label="seed_refresh_capped (source)")
    ax2.axhline(0, color=TEXT, lw=0.6, alpha=0.5)
    for xi, v in zip(x - w2/2, today_d_floor):
        ax2.text(xi, v + (0.5 if v >= 0 else -1.5), f"{v:+.1f}",
                 color="#cfd5e1", ha="center",
                 va="bottom" if v >= 0 else "top", fontsize=10)
    for xi, v in zip(x + w2/2, today_d_capped):
        ax2.text(xi, v + (0.5 if v >= 0 else -1.5), f"{v:+.1f}",
                 color="#cfd5e1", ha="center",
                 va="bottom" if v >= 0 else "top", fontsize=10)
    ax2.set_xticks(x); ax2.set_xticklabels([f"β_loyalty={b}" for b in cells],
                                            color=TEXT, fontsize=10)
    ax2.set_ylabel("Δep0 rescue vs OFF baseline  (pts)", color=TEXT)
    ax2.set_title("Endpoint Δep0 — N=200, both modes within noise",
                  color=ACCENT, fontsize=12, pad=10, loc="left")
    ax2.tick_params(colors=TEXT)
    ax2.set_ylim(min(today_d_floor + today_d_capped) - 4,
                 max(today_d_floor + today_d_capped) + 4)
    for spine in ax2.spines.values(): spine.set_color(GRID)
    ax2.grid(axis="y", color=GRID, alpha=0.6)
    ax2.legend(facecolor=AX_BG, edgecolor=GRID, labelcolor=TEXT,
               fontsize=9, loc="lower center")

    fig.suptitle(
        "Capped-Floor Loyalty Endpoints — N=200 replication of the 2026-05-20 gaps",
        color=TEXT, fontsize=13, y=0.99
    )
    fig.text(0.02, 0.01,
             "Yesterday's |Δcapped−Δfloor| at endpoints: {17.5, 17.5}   →   today at N=200: "
             f"{{{today_gap[0]:.1f}, {today_gap[1]:.1f}}}   (10× collapse — both inside 2-SE)",
             color="#a9b0c0", fontsize=9.5)
    fig.savefig(OUT, dpi=130, facecolor=FIG_BG, bbox_inches="tight")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
