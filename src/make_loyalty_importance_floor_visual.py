"""Chart for exp_loyalty_importance_floor — ep9 rescue rate and ep5-9 mean
across rescue_importance, with the OFF/ON baselines from the valenced
experiment overlaid as horizontal reference lines.

Saves: experiments/loyalty_importance_floor_v1/loyalty_importance_floor.png
"""
import csv, os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(ROOT, "experiments", "loyalty_importance_floor_v1")
CSV_PATH = os.path.join(EXP_DIR, "results.csv")
PNG_PATH = os.path.join(EXP_DIR, "loyalty_importance_floor.png")

BG = "#0e131f"
PANEL = "#131927"
GRID = "#1f2638"
TEXT = "#e8edf5"
ACCENT = "#ffe2ac"
LOYALTY = "#4fc3f7"
GUILT = "#c084fc"
SURV = "#ff6b6b"


def load():
    rows = list(csv.DictReader(open(CSV_PATH)))
    by_cell_ep = defaultdict(lambda: [0, 0])
    by_cell_late = defaultdict(lambda: [0, 0])
    for r in rows:
        rim = float(r["rescue_importance"])
        ep = int(r["episode_idx"])
        by_cell_ep[(rim, ep)][0] += int(r["rescued"])
        by_cell_ep[(rim, ep)][1] += 1
        if 5 <= ep <= 9:
            by_cell_late[rim][0] += int(r["rescued"])
            by_cell_late[rim][1] += 1
    rims = sorted(set(k[0] for k in by_cell_ep))
    ep9 = []
    late = []
    for rim in rims:
        s, n = by_cell_ep[(rim, 9)]
        ep9.append(100 * s / n)
        s2, n2 = by_cell_late[rim]
        late.append(100 * s2 / n2)
    return rims, ep9, late


def main():
    rims, ep9, late = load()

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.tick_params(colors=TEXT)
    ax.grid(True, color=GRID, linewidth=0.7)

    ax.plot(rims, ep9, marker="o", linewidth=2.0, color=LOYALTY,
            label="rescue rate at ep9", markersize=8)
    ax.plot(rims, late, marker="s", linewidth=2.0, color=ACCENT,
            label="rescue rate ep5–9 mean (stable window)", markersize=8)

    # Reference baselines from prior experiments (valenced_encoding_v1, 2026-05-02)
    ax.axhline(28.0, color=GUILT, linestyle="--", linewidth=1.3,
               label="rescue-encoding OFF baseline (28%)", alpha=0.85)
    ax.axhline(15.0, color=SURV, linestyle="--", linewidth=1.3,
               label="rescue-encoding ON @0.7 baseline (15%)", alpha=0.85)

    # Annotate each ep5–9 point
    for x, y in zip(rims, late):
        ax.annotate(f"{y:0.1f}%", xy=(x, y), xytext=(0, 8),
                    textcoords="offset points", color=TEXT,
                    ha="center", fontsize=9)

    ax.set_xlabel("rescue_importance (loyalty channel encoding strength)", color=TEXT)
    ax.set_ylabel("rescue rate (%)", color=TEXT)
    ax.set_xticks(rims)
    ax.set_ylim(0, 35)
    ax.set_title("Loyalty Importance Floor — boomerang is structural, not importance-driven",
                 color=TEXT, pad=12)
    leg = ax.legend(facecolor=PANEL, edgecolor=GRID, framealpha=0.9, fontsize=9,
                    loc="upper left")
    for t in leg.get_texts():
        t.set_color(TEXT)

    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=160, facecolor=BG)
    print(f"Wrote {PNG_PATH}")


if __name__ == "__main__":
    main()
