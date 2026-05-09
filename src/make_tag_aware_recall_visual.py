"""
Visualize tag-aware recall vs legacy stored-guilt recall across β_guilt.

Headline chart: side-by-side panels showing
  (left)  ep5–9 mean rescue rate vs β_guilt for each recall mode
  (right) ep0 rescue rate vs β_guilt (regime-break check)
"""
import csv, collections, os
import matplotlib.pyplot as plt

EXP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "tag_aware_recall_v1",
)
RESULTS = os.path.join(EXP_DIR, "results.csv")
OUT_PNG = os.path.join(EXP_DIR, "tag_aware_recall.png")

PALETTE = {
    "fig_bg": "#0e131f",
    "ax_bg": "#131927",
    "grid": "#1f2638",
    "text": "#e8edf5",
    "accent": "#ffe2ac",
    "legacy": "#ff6b6b",   # survival red — "laundered failure"
    "tag_aw": "#7fffa1",   # curiosity green — "intact identity"
    "guilt": "#c084fc",
    "loyalty": "#4fc3f7",
}


def load_metrics():
    rows = list(csv.DictReader(open(RESULTS)))
    by_cell = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        key = (int(r["tag_aware"]), float(r["beta_guilt"]))
        by_cell[key][int(r["agent_id"])].append((int(r["episode_idx"]),
                                                   r["outcome"],
                                                   int(r["rescued"])))
    out = {}
    for key, agents in by_cell.items():
        ep0_r = []
        ep59 = []
        ep59_R = []
        ep59_F = []
        for aid, eps in agents.items():
            ep0_list = [(o, rs) for (ep, o, rs) in eps if ep == 0]
            ep59_list = [rs for (ep, _, rs) in eps if 5 <= ep <= 9]
            if not ep0_list:
                continue
            ep0_outc, _ = ep0_list[0]
            ep0_rescued = 1 if ep0_outc == "PARTNER_RESCUED" else 0
            ep0_r.append(ep0_rescued)
            ep59_mean = sum(ep59_list) / len(ep59_list) if ep59_list else 0
            ep59.append(ep59_mean)
            (ep59_R if ep0_rescued else ep59_F).append(ep59_mean)
        out[key] = {
            "ep0": 100 * sum(ep0_r) / len(ep0_r) if ep0_r else 0,
            "ep59": 100 * sum(ep59) / len(ep59) if ep59 else 0,
            "ep59_R": 100 * sum(ep59_R) / len(ep59_R) if ep59_R else 0,
            "ep59_F": 100 * sum(ep59_F) / len(ep59_F) if ep59_F else 0,
            "div":    (100 * sum(ep59_R) / len(ep59_R) - 100 * sum(ep59_F) / len(ep59_F))
                      if (ep59_R and ep59_F) else 0,
            "n": len(ep0_r),
        }
    return out


def main():
    metrics = load_metrics()
    betas = [0.05, 0.15, 0.30, 0.50]

    legacy_ep59 = [metrics[(0, b)]["ep59"] for b in betas]
    tag_ep59    = [metrics[(1, b)]["ep59"] for b in betas]
    legacy_ep0  = [metrics[(0, b)]["ep0"] for b in betas]
    tag_ep0     = [metrics[(1, b)]["ep0"] for b in betas]

    plt.rcParams.update({
        "axes.edgecolor": PALETTE["text"],
        "axes.labelcolor": PALETTE["text"],
        "xtick.color": PALETTE["text"],
        "ytick.color": PALETTE["text"],
        "text.color": PALETTE["text"],
        "font.size": 10,
    })

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.0))
    fig.patch.set_facecolor(PALETTE["fig_bg"])

    # Panel A — ep5–9 mean rescue rate
    ax = axes[0]
    ax.set_facecolor(PALETTE["ax_bg"])
    ax.plot(betas, legacy_ep59, "o-", color=PALETTE["legacy"], lw=2.4,
            ms=9, label="LEGACY (stored-guilt > 0.4)")
    ax.plot(betas, tag_ep59, "s-", color=PALETTE["tag_aw"], lw=2.4,
            ms=9, label="TAG-AWARE (origin tag)")
    for b, l, t in zip(betas, legacy_ep59, tag_ep59):
        ax.annotate(f"{l:.0f}%", (b, l), textcoords="offset points",
                    xytext=(8, -12), color=PALETTE["legacy"], fontsize=9)
        ax.annotate(f"{t:.0f}%", (b, t), textcoords="offset points",
                    xytext=(8, 6), color=PALETTE["tag_aw"], fontsize=9)
    ax.set_xlabel(r"$\beta_{\rm guilt}$  (with $\beta_{\rm loyalty}=0.05$ fixed)")
    ax.set_ylabel("ep5–9 mean rescue rate (%)")
    ax.set_title("Tag-aware recall ≈ doubles long-run rescue capacity",
                 color=PALETTE["accent"], pad=12, fontsize=11.5)
    ax.set_ylim(0, 60)
    ax.grid(True, color=PALETTE["grid"], lw=0.7)
    ax.legend(loc="upper right", facecolor=PALETTE["ax_bg"],
              edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"])

    # Panel B — ep0 rescue rate (regime-break check)
    ax = axes[1]
    ax.set_facecolor(PALETTE["ax_bg"])
    ax.plot(betas, legacy_ep0, "o-", color=PALETTE["legacy"], lw=2.4,
            ms=9, label="LEGACY")
    ax.plot(betas, tag_ep0, "s-", color=PALETTE["tag_aw"], lw=2.4,
            ms=9, label="TAG-AWARE")
    for b, l, t in zip(betas, legacy_ep0, tag_ep0):
        ax.annotate(f"{l:.0f}%", (b, l), textcoords="offset points",
                    xytext=(8, -14), color=PALETTE["legacy"], fontsize=9)
        ax.annotate(f"{t:.0f}%", (b, t), textcoords="offset points",
                    xytext=(8, 6), color=PALETTE["tag_aw"], fontsize=9)
    ax.axhline(y=84, ls="--", color=PALETTE["loyalty"], lw=1.0, alpha=0.6)
    ax.text(0.50, 87, "symmetric-β baseline", color=PALETTE["loyalty"],
            fontsize=8, ha="right")
    ax.set_xlabel(r"$\beta_{\rm guilt}$")
    ax.set_ylabel("ep0 rescue rate (%)")
    ax.set_title("Regime-break at β_guilt=0.30 disappears under tag-aware recall",
                 color=PALETTE["accent"], pad=12, fontsize=11.5)
    ax.set_ylim(0, 100)
    ax.grid(True, color=PALETTE["grid"], lw=0.7)
    ax.legend(loc="lower left", facecolor=PALETTE["ax_bg"],
              edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"])

    fig.suptitle("Tag-Aware Recall — Laundering IS the divergence-erosion mechanism",
                 color=PALETTE["text"], fontsize=13.5, y=0.995)
    fig.text(0.5, 0.01,
             "κ=1.0 · T_snap=12 · severity=1.0 · n=50 agents/cell × 4 β_guilt × "
             "2 modes × 10 episodes = 4,000 episodes",
             ha="center", color=PALETTE["text"], fontsize=8.5, alpha=0.7)
    fig.tight_layout(rect=[0, 0.025, 1, 0.96])
    fig.savefig(OUT_PNG, facecolor=PALETTE["fig_bg"], dpi=150, bbox_inches="tight")
    print(f"Wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
