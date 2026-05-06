"""Chart for exp_decay_asymmetry — ep5–9 mean rescue rate AND population
divergence@5–9 across β_loyalty (β_guilt held at 0.05). The asymmetric-decay
hypothesis predicted both should rise; the data shows mean is flat and
divergence flips sign. Two panels share the x-axis.

Saves: experiments/decay_asymmetry_v1/decay_asymmetry.png
"""
import csv, os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(ROOT, "experiments", "decay_asymmetry_v1")
CSV_PATH = os.path.join(EXP_DIR, "results.csv")
PNG_PATH = os.path.join(EXP_DIR, "decay_asymmetry.png")

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
    late = defaultdict(lambda: [0, 0])             # (beta_l) -> [resc, total]
    ep1_class = defaultdict(dict)                  # (beta_l) -> {agent: ep1_rescued}
    late_split = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # bl -> cls -> [resc,total]
    for r in rows:
        bl = float(r["beta_loyalty"])
        ag = int(r["agent_id"])
        ep = int(r["episode_idx"])
        rescued = int(r["rescued"])
        if ep == 1:
            ep1_class[bl][ag] = rescued
        if 5 <= ep <= 9:
            late[bl][0] += rescued
            late[bl][1] += 1
    for r in rows:
        bl = float(r["beta_loyalty"])
        ag = int(r["agent_id"])
        ep = int(r["episode_idx"])
        if 5 <= ep <= 9:
            cls = ep1_class[bl].get(ag, 0)
            late_split[bl][cls][0] += int(r["rescued"])
            late_split[bl][cls][1] += 1
    bls = sorted(late.keys())
    late_mean = [100 * late[bl][0] / late[bl][1] for bl in bls]
    div = []
    for bl in bls:
        s = late_split[bl]
        r1 = 100 * s[1][0] / s[1][1] if s[1][1] else 0.0
        r0 = 100 * s[0][0] / s[0][1] if s[0][1] else 0.0
        div.append(r1 - r0)
    return bls, late_mean, div


def main():
    bls, late_mean, div = load()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 6.6), sharex=True,
                                    gridspec_kw={"height_ratios": [1.0, 1.0]})
    fig.patch.set_facecolor(BG)

    # Panel A — ep5–9 mean rescue
    ax1.set_facecolor(PANEL)
    for s in ax1.spines.values():
        s.set_color(GRID)
    ax1.tick_params(colors=TEXT)
    ax1.grid(True, color=GRID, linewidth=0.7)
    ax1.plot(bls, late_mean, marker="o", linewidth=2.0, color=LOYALTY,
             markersize=9, label="rescue rate ep5–9 mean")
    for x, y in zip(bls, late_mean):
        ax1.annotate(f"{y:0.1f}%", xy=(x, y), xytext=(0, 10),
                     textcoords="offset points", color=TEXT,
                     ha="center", fontsize=9)
    ax1.axhline(28.0, color=GUILT, linestyle="--", linewidth=1.3, alpha=0.85,
                label="rescue-encoding OFF baseline (28%)")
    ax1.axhline(15.0, color=SURV, linestyle="--", linewidth=1.3, alpha=0.85,
                label="rescue-encoding ON @0.7 baseline (15%)")
    ax1.set_ylim(0, 35)
    ax1.set_ylabel("ep5–9 mean rescue (%)", color=TEXT)
    ax1.set_title(
        "Decay Asymmetry — mean rescue is flat (range 2.0 pts), divergence flips sign",
        color=TEXT, pad=10
    )
    leg = ax1.legend(facecolor=PANEL, edgecolor=GRID, framealpha=0.9,
                     fontsize=9, loc="upper left")
    for t in leg.get_texts():
        t.set_color(TEXT)

    # Panel B — divergence@5–9
    ax2.set_facecolor(PANEL)
    for s in ax2.spines.values():
        s.set_color(GRID)
    ax2.tick_params(colors=TEXT)
    ax2.grid(True, color=GRID, linewidth=0.7)
    ax2.axhline(0.0, color=TEXT, linestyle=":", linewidth=1.0, alpha=0.5)
    bar_colors = [ACCENT if v >= 0 else SURV for v in div]
    bars = ax2.bar([str(b) for b in bls], div, color=bar_colors,
                   edgecolor=GRID, linewidth=0.8, width=0.55)
    for bar, v in zip(bars, div):
        y = bar.get_height()
        offset = 1.6 if y >= 0 else -3.0
        ax2.annotate(f"{v:+.1f} pts", xy=(bar.get_x() + bar.get_width() / 2, y),
                     xytext=(0, offset), textcoords="offset points",
                     color=TEXT, ha="center", fontsize=9)
    ax2.set_ylim(-25, 20)
    ax2.set_ylabel("divergence@5–9 (pts)\n[ep1-rescuers − ep1-failers]", color=TEXT)
    ax2.set_xlabel("β_loyalty   (β_guilt held fixed at 0.05)", color=TEXT)

    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=160, facecolor=BG)
    print(f"Wrote {PNG_PATH}")


if __name__ == "__main__":
    main()
