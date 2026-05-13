"""Chart-builder for exp_seed_only_floor_b30_n200.

One PNG with two panels:
  Left  — ep0 rescue rate per mode at β_guilt=0.30, with binomial 1-SE error
          bars (N=200 per arm). Annotated with Δfull and Δseed vs OFF.
  Right — N=40 (prior) vs N=200 (this run) Δ comparison, focused on the
          |Δfull − Δseed| gap that motivated the replication.
"""
import csv, math, os
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "experiments", "seed_only_floor_b30_n200_v1")
CSV_PATH = os.path.join(EXP, "results.csv")
OUT_PNG = os.path.join(EXP, "seed_only_floor_b30_n200.png")

PALETTE = {
    "fig_bg": "#0e131f",
    "ax_bg": "#131927",
    "grid":  "#1f2638",
    "text":  "#e8edf5",
    "accent": "#ffe2ac",
    "off":   "#c9d3e3",
    "full":  "#7fffa1",
    "seed":  "#c084fc",
}


def _rate(rows, pred):
    sel = [int(r["rescued"]) for r in rows if pred(r)]
    if not sel:
        return 0.0, 0
    return sum(sel) / len(sel), len(sel)


def _se(p, n):
    return math.sqrt(p * (1 - p) / max(n, 1))


def main():
    rows = list(csv.DictReader(open(CSV_PATH)))

    # ep0 rates per mode
    modes = ["off", "full", "seed_only"]
    p_ep0, n_ep0 = {}, {}
    for m in modes:
        p_ep0[m], n_ep0[m] = _rate(
            rows, lambda r, m=m: r["inject_mode"] == m and int(r["episode_idx"]) == 0
        )

    dfull = (p_ep0["full"] - p_ep0["off"]) * 100
    dseed = (p_ep0["seed_only"] - p_ep0["off"]) * 100
    gap_n200 = abs(dfull - dseed)

    # Prior N=40 numbers from exp_seed_only_floor_v1 at β_guilt=0.30:
    #   OFF=77.5%, Full=77.5%, Seed-only=62.5% → Δfull=0, Δseed=−15, gap=15
    dfull_n40 = 0.0
    dseed_n40 = -15.0
    gap_n40 = abs(dfull_n40 - dseed_n40)

    plt.rcParams.update({
        "figure.facecolor": PALETTE["fig_bg"],
        "axes.facecolor":   PALETTE["ax_bg"],
        "axes.edgecolor":   PALETTE["grid"],
        "axes.labelcolor":  PALETTE["text"],
        "xtick.color":      PALETTE["text"],
        "ytick.color":      PALETTE["text"],
        "text.color":       PALETTE["text"],
        "axes.grid":        True,
        "grid.color":       PALETTE["grid"],
        "grid.alpha":       0.6,
    })

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.5, 5.5))

    # ── LEFT: ep0 rates per mode with 1-SE error bars
    xs = [0, 1, 2]
    pcts = [p_ep0[m] * 100 for m in modes]
    ses = [_se(p_ep0[m], n_ep0[m]) * 100 for m in modes]
    colors = [PALETTE["off"], PALETTE["full"], PALETTE["seed"]]
    labels = ["INJ-OFF", "Full floors", "Seed-only floor"]

    axL.bar(xs, pcts, color=colors, edgecolor=PALETTE["text"], linewidth=0.5,
            yerr=ses, ecolor=PALETTE["accent"], capsize=6, alpha=0.92)
    for x, p, n in zip(xs, pcts, [n_ep0[m] for m in modes]):
        axL.text(x, p + 1.7, f"{p:.1f}%", ha="center", va="bottom",
                 color=PALETTE["text"], fontsize=11, fontweight="bold")
        axL.text(x, 3, f"N={n}", ha="center", va="bottom",
                 color=PALETTE["text"], fontsize=9, alpha=0.7)

    axL.set_xticks(xs)
    axL.set_xticklabels(labels, fontsize=10)
    axL.set_ylabel("ep0 rescue rate (%)", fontsize=11)
    axL.set_ylim(0, 90)
    axL.set_title("ep0 rescue rate at β_guilt=0.30, N=200 per arm",
                  color=PALETTE["accent"], fontsize=12, pad=12)

    # Δ annotations
    box_y = 78
    axL.text(1.0, box_y, f"Δfull = {dfull:+.1f} pts", ha="center", va="center",
             color=PALETTE["full"], fontsize=11, fontweight="bold")
    axL.text(2.0, box_y, f"Δseed = {dseed:+.1f} pts", ha="center", va="center",
             color=PALETTE["seed"], fontsize=11, fontweight="bold")

    # ── RIGHT: gap comparison N=40 vs N=200
    bar_xs = [0.0, 1.0]
    gaps = [gap_n40, gap_n200]
    bar_colors = ["#ff6b6b", "#7fffa1"]
    axR.bar(bar_xs, gaps, color=bar_colors, edgecolor=PALETTE["text"],
            linewidth=0.5, width=0.55, alpha=0.92)
    for x, g in zip(bar_xs, gaps):
        axR.text(x, g + 0.4, f"{g:.1f} pts", ha="center", va="bottom",
                 color=PALETTE["text"], fontsize=12, fontweight="bold")

    # 2-SE bar overlay (N=200) — visually contextualises the surviving gap
    se_diff = math.sqrt(
        _se(p_ep0["full"], n_ep0["full"]) ** 2
        + _se(p_ep0["seed_only"], n_ep0["seed_only"]) ** 2
    ) * 100
    axR.axhline(2 * se_diff, color=PALETTE["accent"], linestyle="--",
                linewidth=1.2, alpha=0.75)
    axR.text(1.0, 2 * se_diff + 0.4, f"2-SE @ N=200 ≈ {2*se_diff:.1f} pts",
             ha="center", va="bottom", color=PALETTE["accent"],
             fontsize=10, alpha=0.9)

    axR.set_xticks(bar_xs)
    axR.set_xticklabels(["N=40 (2026-05-12)", "N=200 (this run)"], fontsize=10)
    axR.set_ylabel("|Δfull − Δseed| at ep0 (pts)", fontsize=11)
    axR.set_ylim(0, max(16, 2 * se_diff + 4))
    axR.set_title("β_guilt=0.30 disagreement: collapses with N",
                  color=PALETTE["accent"], fontsize=12, pad=12)

    fig.suptitle(
        "Seed-Only Floor Replication — β_guilt=0.30 N=200 tightens to 1 pt",
        color=PALETTE["text"], fontsize=13, fontweight="bold", y=0.995,
    )

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_PNG, dpi=150, facecolor=PALETTE["fig_bg"])
    print(f"Wrote {OUT_PNG}")
    print(f"ep0  OFF={p_ep0['off']*100:.2f}%  FULL={p_ep0['full']*100:.2f}%  SEED={p_ep0['seed_only']*100:.2f}%")
    print(f"Δfull={dfull:+.2f}  Δseed={dseed:+.2f}  gap_n200={gap_n200:.2f}  gap_n40={gap_n40:.2f}")


if __name__ == "__main__":
    main()
