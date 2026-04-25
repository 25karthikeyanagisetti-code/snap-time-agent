"""
Visualizations for the second wave of experiments:
  - Exp 2: severity sweep      → severity_threshold.png
  - Exp 3: phi-mode comparison → phi_mode_comparison.png
  - Exp 4: forgiveness         → forgiveness_heatmap.png + aging_collapse.png
"""
import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _failures(csv_path, key_fields):
    """key_fields: tuple of column names → tuple key. Returns failure_rate dict."""
    by = defaultdict(list)
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            key = tuple(_coerce(r[k]) for k in key_fields)
            by[key].append(r["outcome"])
    return {
        k: sum(1 for o in outs if o in ("TIMEOUT", "PARTNER_DEAD")) / len(outs)
        for k, outs in by.items()
    }


def _outcome_breakdown(csv_path, key_fields):
    by = defaultdict(lambda: defaultdict(int))
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            key = tuple(_coerce(r[k]) for k in key_fields)
            by[key][r["outcome"]] += 1
    return by


def _coerce(s):
    try:
        v = float(s)
        return int(v) if v.is_integer() else v
    except ValueError:
        return s


# ─── Exp 2: severity threshold ───────────────────────────────────────────────
def severity_chart():
    csv_path = os.path.join(ROOT, "experiments/severity_sweep_v1/results.csv")
    fails = _failures(csv_path, ("severity", "kappa"))
    sevs = sorted({s for (s, _) in fails})
    kappas = sorted({k for (_, k) in fails})

    fig, ax = plt.subplots(figsize=(11, 7))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.95, len(sevs)))

    for i, sev in enumerate(sevs):
        ys = [fails[(sev, k)] * 100 for k in kappas]
        ax.plot(kappas, ys, marker="o", linewidth=2.4, markersize=8,
                label=f"severity = {sev}", color=cmap[i])

    ax.axhline(40, ls="--", color="gray", alpha=0.5)
    ax.text(3.5, 42, "rational baseline (~40%)", fontsize=9, color="gray")

    ax.annotate(
        "Valley emerges\nbetween severity 0.4 and 0.6",
        xy=(0.25, 80), xytext=(1.4, 80),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.4),
        fontsize=11, fontweight="bold",
    )

    ax.set_xlabel("κ — emotion weight", fontsize=13)
    ax.set_ylabel("Failure rate (%)", fontsize=13)
    ax.set_title(
        "The Paralysis Valley has a memory-severity threshold.\n"
        "Below severity ≈ 0.4 it does not exist at all. Above, it deepens fast.",
        fontsize=13, pad=12
    )
    ax.set_ylim(-3, 105)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10, loc="lower left", ncol=2)
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/severity_sweep_v1/severity_threshold.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


# ─── Exp 3: phi mode comparison ──────────────────────────────────────────────
def phi_mode_chart():
    csv_path = os.path.join(ROOT, "experiments/phi_mode_v1/results.csv")
    fails = _failures(csv_path, ("phi_mode", "kappa"))
    breakdown = _outcome_breakdown(csv_path, ("phi_mode", "kappa"))
    kappas = sorted({k for (_, k) in fails})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))

    # Left: failure rate comparison
    add_y = [fails[("additive", k)] * 100 for k in kappas]
    mul_y = [fails[("multiplicative", k)] * 100 for k in kappas]
    ax1.plot(kappas, add_y, "o-", linewidth=2.6, markersize=9,
             label="Additive: Φ = -v + κ⟨e,c⟩", color="#d62728")
    ax1.plot(kappas, mul_y, "s-", linewidth=2.6, markersize=9,
             label="Multiplicative: Φ = -v(1+κ⟨e,c⟩)", color="#2ca02c")
    ax1.axvspan(0.15, 0.7, alpha=0.12, color="#d62728")
    ax1.text(0.42, 92, "Paralysis Valley\n(additive only)", ha="center",
             fontsize=11, fontweight="bold", color="#a01010")
    ax1.set_xlabel("κ — emotion weight", fontsize=12)
    ax1.set_ylabel("Failure rate (%)", fontsize=12)
    ax1.set_title("Multiplicative coupling eliminates the valley", fontsize=12)
    ax1.set_ylim(-5, 105)
    ax1.legend(fontsize=10)
    ax1.grid(alpha=0.3)

    # Right: outcome breakdown — multiplicative never rescues
    rescue_add = []
    rescue_mul = []
    for k in kappas:
        n_a = sum(breakdown[("additive", k)].values())
        n_m = sum(breakdown[("multiplicative", k)].values())
        rescue_add.append(breakdown[("additive", k)].get("PARTNER_RESCUED", 0) / n_a * 100)
        rescue_mul.append(breakdown[("multiplicative", k)].get("PARTNER_RESCUED", 0) / n_m * 100)
    x = np.arange(len(kappas))
    w = 0.38
    ax2.bar(x - w/2, rescue_add, w, label="Additive", color="#d62728",
            edgecolor="black", linewidth=0.5)
    ax2.bar(x + w/2, rescue_mul, w, label="Multiplicative", color="#2ca02c",
            edgecolor="black", linewidth=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"κ={k}" for k in kappas])
    ax2.set_ylabel("Partner rescue rate (%)", fontsize=12)
    ax2.set_title("…but multiplicative NEVER rescues the partner",
                  fontsize=12)
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=10)
    ax2.grid(alpha=0.3, axis="y")

    plt.suptitle("Trade-off: removing paralysis costs the capacity for sacrifice.",
                 fontsize=14, y=1.02)
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/phi_mode_v1/phi_mode_comparison.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


# ─── Exp 4: forgiveness heatmap (preage × decay × kappa) ─────────────────────
def forgiveness_chart():
    csv_path = os.path.join(ROOT, "experiments/forgiveness_v1/results.csv")
    fails = _failures(csv_path, ("preage", "decay", "kappa"))
    preages = sorted({p for (p, _, _) in fails})
    decays = sorted({d for (_, d, _) in fails})
    kappas = sorted({k for (_, _, k) in fails})

    fig, axes = plt.subplots(1, len(kappas), figsize=(16, 5.5),
                             sharey=True)
    for ax, k in zip(axes, kappas):
        grid = np.array([
            [fails[(p, d, k)] * 100 for d in decays] for p in preages
        ])
        im = ax.imshow(grid, cmap="RdYlGn_r", vmin=0, vmax=100, aspect="auto")
        ax.set_xticks(range(len(decays)))
        ax.set_xticklabels([f"{d}" for d in decays])
        ax.set_yticks(range(len(preages)))
        ax.set_yticklabels([f"{p}" for p in preages])
        ax.set_xlabel("emotion-decay rate", fontsize=11)
        if ax is axes[0]:
            ax.set_ylabel("memory pre-age (steps)", fontsize=11)
        ax.set_title(f"κ = {k}", fontsize=12)
        for i in range(len(preages)):
            for j in range(len(decays)):
                ax.text(j, i, f"{grid[i,j]:.0f}", ha="center", va="center",
                        fontsize=9,
                        color="white" if grid[i,j] > 60 else "black")

    cbar = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02)
    cbar.set_label("Failure rate (%)", fontsize=11)
    plt.suptitle(
        "Aging the memory escapes the valley. Active forgiveness during the "
        "episode does almost nothing.",
        fontsize=13, y=1.02
    )
    out = os.path.join(ROOT, "experiments/forgiveness_v1/forgiveness_heatmap.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


# ─── Exp 4 part 2: aging collapse — average across decay axis ────────────────
def aging_collapse_chart():
    csv_path = os.path.join(ROOT, "experiments/forgiveness_v1/results.csv")
    fails = _failures(csv_path, ("preage", "decay", "kappa"))
    preages = sorted({p for (p, _, _) in fails})
    kappas = sorted({k for (_, _, k) in fails})

    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = ["#d62728", "#ff7f0e", "#2ca02c"]
    for ki, k in enumerate(kappas):
        ys = []
        for p in preages:
            # average across all decay rates at this (preage, k)
            decays = sorted({d for (pp, d, kk) in fails if pp == p and kk == k})
            avg = np.mean([fails[(p, d, k)] * 100 for d in decays])
            ys.append(avg)
        ax.plot(preages, ys, "o-", linewidth=2.6, markersize=10,
                label=f"κ = {k}", color=colors[ki])

    ax.axhline(40, ls="--", color="gray", alpha=0.5)
    ax.text(155, 42, "rational baseline (~40%)", fontsize=10, color="gray")

    ax.annotate(
        "Aging collapses ALL κ regimes\nto the same rational baseline.",
        xy=(150, 38), xytext=(60, 70),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.4),
        fontsize=11, fontweight="bold",
    )

    ax.set_xlabel("memory pre-age (steps)", fontsize=13)
    ax.set_ylabel("Failure rate (%) — averaged across decay rates", fontsize=12)
    ax.set_title(
        "Forgiveness via aging is a flattener, not a balancer.\n"
        "Old memories collapse paralyzed AND committed agents to neutral rationality.",
        fontsize=13, pad=12
    )
    ax.set_ylim(0, 105)
    ax.legend(fontsize=11, loc="upper right")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/forgiveness_v1/aging_collapse.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {out}")


def main():
    severity_chart()
    phi_mode_chart()
    forgiveness_chart()
    aging_collapse_chart()


if __name__ == "__main__":
    main()
