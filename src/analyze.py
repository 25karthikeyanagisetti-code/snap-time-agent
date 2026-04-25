"""
Analyze results.csv from a sweep and produce heatmaps + summary stats.
Run with: python -m src.analyze
"""

import os
import csv
import math
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EXP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "regime_map_v1"
)
CSV_PATH = os.path.join(EXP_DIR, "results.csv")


def load():
    rows = []
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            row["t_snap"] = int(row["t_snap"])
            row["kappa"] = float(row["kappa"])
            row["seeded_memory"] = int(row["seeded_memory"])
            row["target_switches"] = int(row["target_switches"])
            row["steps_used"] = int(row["steps_used"])
            rows.append(row)
    return rows


def aggregate(rows, t_snaps, kappas, seeded):
    """
    For each (t_snap, kappa) cell, compute:
      - rescue_rate
      - resource_rate
      - timeout_rate
      - hesitation_rate (frac of episodes with >=1 target switch)
      - avg_switches
      - failure_rate (timeouts + partner_dead — agent failed to commit)
    Returns dict cell -> metrics
    """
    cells = defaultdict(list)
    for r in rows:
        if r["seeded_memory"] != seeded:
            continue
        cells[(r["t_snap"], r["kappa"])].append(r)

    out = {}
    for (t, k), eps in cells.items():
        n = len(eps)
        rescue = sum(1 for e in eps if e["outcome"] == "PARTNER_RESCUED") / n
        resource = sum(1 for e in eps if e["outcome"] == "RESOURCE_TAKEN") / n
        timeout = sum(1 for e in eps if e["outcome"] == "TIMEOUT") / n
        partner_dead = sum(1 for e in eps if e["outcome"] == "PARTNER_DEAD") / n
        hesitation = sum(1 for e in eps if e["target_switches"] >= 1) / n
        avg_switches = sum(e["target_switches"] for e in eps) / n
        # Failure = neither outcome achieved (timeout OR partner died from inaction)
        failure = timeout + partner_dead
        out[(t, k)] = {
            "rescue": rescue, "resource": resource, "timeout": timeout,
            "partner_dead": partner_dead, "hesitation": hesitation,
            "avg_switches": avg_switches, "failure": failure,
            "n": n,
        }
    return out


def matrix_for(metric, agg, t_snaps, kappas):
    M = np.zeros((len(t_snaps), len(kappas)))
    for i, t in enumerate(t_snaps):
        for j, k in enumerate(kappas):
            M[i, j] = agg.get((t, k), {}).get(metric, 0.0)
    return M


def plot_heatmap(ax, M, t_snaps, kappas, title, cmap="viridis", vmax=None):
    im = ax.imshow(M, aspect="auto", origin="lower", cmap=cmap,
                   vmin=0, vmax=vmax if vmax else M.max())
    ax.set_xticks(range(len(kappas)))
    ax.set_xticklabels([str(k) for k in kappas])
    ax.set_yticks(range(len(t_snaps)))
    ax.set_yticklabels([str(t) for t in t_snaps])
    ax.set_xlabel("kappa (emotion weight)")
    ax.set_ylabel("T_snap")
    ax.set_title(title)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            color = "white" if v < (M.max() * 0.5) else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color=color, fontsize=8)
    return im


def main():
    rows = load()
    t_snaps = sorted({r["t_snap"] for r in rows})
    kappas = sorted({r["kappa"] for r in rows})

    agg_seeded = aggregate(rows, t_snaps, kappas, seeded=1)
    agg_nomem = aggregate(rows, t_snaps, kappas, seeded=0)

    # Big figure: 4 metrics x 2 conditions
    fig, axes = plt.subplots(4, 2, figsize=(13, 16))
    metrics = [
        ("failure",     "Failure rate (timeout + partner death)", "Reds"),
        ("rescue",      "Partner rescue rate",                    "Greens"),
        ("resource",    "Resource taken rate",                    "Blues"),
        ("hesitation",  "Hesitation rate (>=1 target switch)",    "Purples"),
    ]
    for i, (metric, title, cmap) in enumerate(metrics):
        Ms = matrix_for(metric, agg_seeded, t_snaps, kappas)
        Mn = matrix_for(metric, agg_nomem, t_snaps, kappas)
        plot_heatmap(axes[i, 0], Ms, t_snaps, kappas,
                     f"{title}\n[seeded memory]", cmap=cmap, vmax=1.0)
        plot_heatmap(axes[i, 1], Mn, t_snaps, kappas,
                     f"{title}\n[no memory — control]", cmap=cmap, vmax=1.0)

    plt.tight_layout()
    out = os.path.join(EXP_DIR, "heatmaps.png")
    plt.savefig(out, dpi=120, bbox_inches="tight")
    print(f"Wrote {out}")

    # Headline figure: failure rate vs kappa, one line per T_snap, seeded only
    fig2, ax = plt.subplots(figsize=(9, 6))
    for t in t_snaps:
        ys = [agg_seeded[(t, k)]["failure"] for k in kappas]
        ax.plot(kappas, ys, marker="o", label=f"T_snap={t}")
    ax.set_xlabel("kappa (emotion weight)")
    ax.set_ylabel("Failure rate (timeout or partner death)")
    ax.set_title("Failure rate vs emotion weight\n(seeded abandonment memory)")
    ax.legend()
    ax.grid(alpha=0.3)
    out2 = os.path.join(EXP_DIR, "failure_curve.png")
    plt.savefig(out2, dpi=120, bbox_inches="tight")
    print(f"Wrote {out2}")

    # Print a digest
    print("\n=== SEEDED MEMORY ===")
    print(f"{'T_snap':>6} {'kappa':>6} {'rescue':>8} {'resource':>8} "
          f"{'timeout':>8} {'hesit':>6} {'failure':>8}")
    for t in t_snaps:
        for k in kappas:
            m = agg_seeded[(t, k)]
            print(f"{t:>6} {k:>6.2f} {m['rescue']:>8.2f} {m['resource']:>8.2f} "
                  f"{m['timeout']:>8.2f} {m['hesitation']:>6.2f} {m['failure']:>8.2f}")

    print("\n=== NO MEMORY (control) ===")
    print(f"{'T_snap':>6} {'kappa':>6} {'rescue':>8} {'resource':>8} "
          f"{'timeout':>8} {'hesit':>6} {'failure':>8}")
    for t in t_snaps:
        for k in kappas:
            m = agg_nomem[(t, k)]
            print(f"{t:>6} {k:>6.2f} {m['rescue']:>8.2f} {m['resource']:>8.2f} "
                  f"{m['timeout']:>8.2f} {m['hesitation']:>6.2f} {m['failure']:>8.2f}")


if __name__ == "__main__":
    main()
