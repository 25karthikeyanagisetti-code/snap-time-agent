"""
Visualize jitter + tag-aware recall, the 2x2 combination experiment.

Two panels:
  (left)  per-episode rescue rate trajectory, one line per cell —
          shows the homogenization collapse at ep1 and the sustained
          plateau for ep2-19, for all four cells.
  (right) bar chart of behavioral-failure rate (<=4/20 rescues) and
          ep5-9 mean sustained rescue rate per cell, showing the
          additive combination effect.
"""
import csv, collections, math, os
import matplotlib.pyplot as plt

EXP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "jitter_plus_tag_aware_v1",
)
RESULTS = os.path.join(EXP_DIR, "results.csv")
OUT_PNG = os.path.join(EXP_DIR, "jitter_plus_tag_aware.png")

PALETTE = {
    "fig_bg": "#0e131f",
    "ax_bg": "#131927",
    "grid": "#1f2638",
    "text": "#e8edf5",
}

CELL_COLORS = {
    "off_off": "#ff6b6b",   # legacy baseline — red
    "off_on":  "#4fc3f7",   # tag-aware alone — blue
    "on_off":  "#c084fc",   # jitter alone — purple
    "on_on":   "#7fffa1",   # both — green
}
CELL_LABELS = {
    "off_off": "neither (legacy)",
    "off_on":  "tag-aware recall only",
    "on_off":  "jitter only (σ=0.40)",
    "on_on":   "both (jitter + tag-aware)",
}
CELLS = ["off_off", "off_on", "on_off", "on_on"]


def load():
    rows = list(csv.DictReader(open(RESULTS)))
    by_cell_ep = collections.defaultdict(lambda: collections.defaultdict(list))
    by_cell_agent = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in rows:
        cell, ep, agent = r["cell"], int(r["episode_idx"]), int(r["agent_id"])
        rescued = int(r["rescued"])
        by_cell_ep[cell][ep].append(rescued)
        by_cell_agent[cell][agent][ep] = rescued
    return by_cell_ep, by_cell_agent


def main():
    by_cell_ep, by_cell_agent = load()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.patch.set_facecolor(PALETTE["fig_bg"])
    for ax in (ax1, ax2):
        ax.set_facecolor(PALETTE["ax_bg"])
        ax.tick_params(colors=PALETTE["text"])
        for spine in ax.spines.values():
            spine.set_color(PALETTE["grid"])
        ax.grid(True, color=PALETTE["grid"], linewidth=0.6)

    # --- Left: trajectory ---
    for cell in CELLS:
        eps = sorted(by_cell_ep[cell].keys())
        rates = [100 * sum(by_cell_ep[cell][e]) / len(by_cell_ep[cell][e]) for e in eps]
        ax1.plot(eps, rates, marker="o", ms=4, lw=2,
                 color=CELL_COLORS[cell], label=CELL_LABELS[cell])
    ax1.set_xlabel("episode", color=PALETTE["text"])
    ax1.set_ylabel("rescue rate (%)", color=PALETTE["text"])
    ax1.set_title("Per-episode rescue rate — homogenization collapse\n"
                   "then sustained plateau (κ=1.0, β_guilt=0.30 laundering regime)",
                   color=PALETTE["text"])
    ax1.legend(facecolor=PALETTE["ax_bg"], edgecolor=PALETTE["grid"],
               labelcolor=PALETTE["text"], fontsize=9)

    # --- Right: bar chart, failure rate + ep5-9 sustained rate ---
    fail_rates, fail_errs = [], []
    ep59_rates, ep59_errs = [], []
    for cell in CELLS:
        agents = by_cell_agent[cell]
        n = len(agents)
        fails = []
        ep59 = []
        for aid, eps in agents.items():
            total = sum(eps.values())
            fails.append(1 if total <= 4 else 0)
            ep59.append(sum(eps[e] for e in range(5, 10)) / 5)
        p = sum(fails) / n
        fail_rates.append(100 * p)
        fail_errs.append(200 * math.sqrt(p * (1 - p) / n))
        m = sum(ep59) / n
        ep59_rates.append(100 * m)
        ep59_errs.append(200 * math.sqrt(m * (1 - m) / n) / math.sqrt(5))

    x = range(len(CELLS))
    w = 0.38
    bars1 = ax2.bar([i - w / 2 for i in x], fail_rates, width=w, yerr=fail_errs,
                    capsize=4, color="#ff6b6b", label="behavioral-failure rate (≤4/20)")
    bars2 = ax2.bar([i + w / 2 for i in x], ep59_rates, width=w, yerr=ep59_errs,
                    capsize=4, color="#7fffa1", label="ep5-9 sustained rescue rate")
    for b, v in zip(bars1, fail_rates):
        ax2.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}%",
                 ha="center", color=PALETTE["text"], fontsize=9)
    for b, v in zip(bars2, ep59_rates):
        ax2.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}%",
                 ha="center", color=PALETTE["text"], fontsize=9)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels([CELL_LABELS[c].replace(" (", "\n(") for c in CELLS],
                         color=PALETTE["text"], fontsize=8.5)
    ax2.set_ylabel("%", color=PALETTE["text"])
    ax2.set_title("Failure rate collapses, sustained rescue triples\n"
                   "(N=200 agents/cell, error bars = 2SE)", color=PALETTE["text"])
    ax2.legend(facecolor=PALETTE["ax_bg"], edgecolor=PALETTE["grid"],
               labelcolor=PALETTE["text"], fontsize=9)
    ax2.set_ylim(0, 85)

    fig.suptitle("Jitter + Tag-Aware Recall: additive combination under asymmetric memory decay",
                  color=PALETTE["text"], fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130, bbox_inches="tight", facecolor=PALETTE["fig_bg"])
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
