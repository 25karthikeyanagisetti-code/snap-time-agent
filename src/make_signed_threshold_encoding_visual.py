"""
Visualize the signed_threshold_encoding sweep.

Two-panel chart:
  (left)  rescue rate per episode for each (τ_g, τ_l) cell
  (right) divergence@ep5–9  AND  ep9 rescue rate as 2x2 heatmaps

Headline number: ep9 rescue rate collapses to 0% under both high-τ_guilt
cells, regardless of τ_loyalty. Asymmetric thresholds do not sort the
population — they expose a NEW failure mode (prior-dilution lockout).
"""
import csv, os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "signed_threshold_encoding_v1",
)
CSV_PATH = os.path.join(OUT_DIR, "results.csv")
PNG_PATH = os.path.join(OUT_DIR, "signed_threshold_encoding.png")

FIG_BG = "#0e131f"
AX_BG = "#131927"
GRID_COLOR = "#1f2638"
TEXT = "#e8edf5"
ACCENT = "#ffe2ac"

CELL_COLORS = {
    "G0.3_L0.3": "#7fffa1",   # curiosity green — symmetric-low (baseline)
    "G0.3_L0.7": "#4fc3f7",   # loyalty blue   — loyalty-stingy
    "G0.7_L0.3": "#ff6b6b",   # survival red   — guilt-stingy
    "G0.7_L0.7": "#c084fc",   # guilt purple   — symmetric-high
}
CELL_LABEL = {
    "G0.3_L0.3": "G=0.3, L=0.3 — symmetric-low",
    "G0.3_L0.7": "G=0.3, L=0.7 — loyalty-stingy",
    "G0.7_L0.3": "G=0.7, L=0.3 — guilt-stingy",
    "G0.7_L0.7": "G=0.7, L=0.7 — symmetric-high",
}


def _load():
    rows = []
    with open(CSV_PATH) as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def _per_episode_rescue(rows):
    out = {}
    for cell in sorted({r["cell"] for r in rows}):
        sub = [r for r in rows if r["cell"] == cell]
        by_agent = defaultdict(dict)
        for r in sub:
            by_agent[r["agent_id"]][int(r["episode_idx"])] = int(r["rescued"])
        n = len(by_agent)
        rates = [
            sum(by_agent[a][ep] for a in by_agent) / n
            for ep in range(10)
        ]
        out[cell] = rates
    return out


def _divergence_and_ep9(rows):
    div = {}
    ep9 = {}
    for cell in sorted({r["cell"] for r in rows}):
        sub = [r for r in rows if r["cell"] == cell]
        by_agent = defaultdict(dict)
        for r in sub:
            by_agent[r["agent_id"]][int(r["episode_idx"])] = int(r["rescued"])
        rescuers = [a for a in by_agent if by_agent[a][1] == 1]
        failers = [a for a in by_agent if by_agent[a][1] == 0]
        diffs = []
        for ep in range(5, 10):
            if rescuers and failers:
                r1 = sum(by_agent[a][ep] for a in rescuers) / len(rescuers)
                r0 = sum(by_agent[a][ep] for a in failers) / len(failers)
                diffs.append(r1 - r0)
        div[cell] = (sum(diffs) / len(diffs)) if diffs else 0.0
        ep9[cell] = sum(by_agent[a][9] for a in by_agent) / len(by_agent)
    return div, ep9


def main():
    rows = _load()
    rescue = _per_episode_rescue(rows)
    div, ep9 = _divergence_and_ep9(rows)

    fig = plt.figure(figsize=(13, 5.2), facecolor=FIG_BG)
    gs = fig.add_gridspec(1, 5, wspace=0.45)
    ax0 = fig.add_subplot(gs[0, :3])
    ax1 = fig.add_subplot(gs[0, 3])
    ax2 = fig.add_subplot(gs[0, 4])

    for ax in (ax0, ax1, ax2):
        ax.set_facecolor(AX_BG)
        for s in ax.spines.values():
            s.set_color(GRID_COLOR)
        ax.tick_params(colors=TEXT)

    # ── Panel 0: per-episode rescue rate trajectories ──────────────────────
    ax0.grid(color=GRID_COLOR, linestyle="-", linewidth=0.6)
    eps = list(range(10))
    for cell, rates in rescue.items():
        pcts = [r * 100 for r in rates]
        ax0.plot(
            eps, pcts, marker="o", linewidth=2.2,
            color=CELL_COLORS[cell], label=CELL_LABEL[cell],
        )
    ax0.set_xlabel("episode index in chain", color=TEXT)
    ax0.set_ylabel("rescue rate (%)", color=TEXT)
    ax0.set_title(
        "Population rescue rate over a 10-episode chain — κ=1.0",
        color=ACCENT, fontsize=12, pad=12,
    )
    ax0.set_xticks(eps)
    ax0.set_ylim(-5, 100)
    leg = ax0.legend(
        facecolor=AX_BG, edgecolor=GRID_COLOR, labelcolor=TEXT,
        fontsize=9, loc="upper right", framealpha=0.95,
    )
    leg.get_frame().set_linewidth(0.6)

    # Annotate the headline number on the chart
    ax0.annotate(
        "high-τ_guilt cells\ncollapse to 0%",
        xy=(9, 0), xytext=(6.5, 35),
        color="#ff6b6b", fontsize=10, ha="left",
        arrowprops=dict(color="#ff6b6b", arrowstyle="->", linewidth=1.2),
    )

    # ── Panel 1: ep9 rescue rate heatmap ───────────────────────────────────
    cell_grid = [["G0.3_L0.3", "G0.3_L0.7"], ["G0.7_L0.3", "G0.7_L0.7"]]
    ep9_mat = [[ep9[c] * 100 for c in row] for row in cell_grid]
    im1 = ax1.imshow(
        ep9_mat, cmap="magma", vmin=0, vmax=20, aspect="auto",
    )
    ax1.set_xticks([0, 1]); ax1.set_yticks([0, 1])
    ax1.set_xticklabels(["L=0.3", "L=0.7"], color=TEXT)
    ax1.set_yticklabels(["G=0.3", "G=0.7"], color=TEXT)
    ax1.set_title("ep9 rescue rate (%)", color=ACCENT, fontsize=11, pad=10)
    for i in range(2):
        for j in range(2):
            v = ep9_mat[i][j]
            tcol = "#0e131f" if v > 10 else TEXT
            ax1.text(j, i, f"{v:.0f}", ha="center", va="center",
                     color=tcol, fontsize=14, fontweight="bold")
    cbar1 = fig.colorbar(im1, ax=ax1, fraction=0.04)
    cbar1.ax.tick_params(colors=TEXT)
    cbar1.outline.set_edgecolor(GRID_COLOR)

    # ── Panel 2: divergence@5-9 heatmap ────────────────────────────────────
    div_mat = [[div[c] * 100 for c in row] for row in cell_grid]
    vmax = max(abs(div[c] * 100) for c in div)
    vmax = max(vmax, 6.0)
    im2 = ax2.imshow(
        div_mat, cmap="PuOr", vmin=-vmax, vmax=vmax, aspect="auto",
    )
    ax2.set_xticks([0, 1]); ax2.set_yticks([0, 1])
    ax2.set_xticklabels(["L=0.3", "L=0.7"], color=TEXT)
    ax2.set_yticklabels(["G=0.3", "G=0.7"], color=TEXT)
    ax2.set_title("divergence@ep5–9  (pts)", color=ACCENT, fontsize=11, pad=10)
    for i in range(2):
        for j in range(2):
            v = div_mat[i][j]
            ax2.text(j, i, f"{v:+.1f}", ha="center", va="center",
                     color="#0e131f", fontsize=13, fontweight="bold")
    cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.04)
    cbar2.ax.tick_params(colors=TEXT)
    cbar2.outline.set_edgecolor(GRID_COLOR)

    fig.suptitle(
        "Signed-threshold encoding — asymmetric gates do NOT sort the population",
        color=TEXT, fontsize=13, y=1.02,
    )

    fig.savefig(PNG_PATH, dpi=140, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"Wrote chart to {PNG_PATH}")
    print(f"\nHeadline numbers:")
    print(f"  G=0.7,L=0.3 ep9 rescue: {ep9['G0.7_L0.3']*100:.1f}%")
    print(f"  G=0.7,L=0.7 ep9 rescue: {ep9['G0.7_L0.7']*100:.1f}%")
    print(f"  best divergence: G=0.3,L=0.7 = {div['G0.3_L0.7']*100:+.1f} pts")


if __name__ == "__main__":
    main()
