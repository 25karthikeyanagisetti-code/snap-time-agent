"""
Visualizations for Wave 3:
  - couplings_zoo.png       (Exp 5)
  - resonance_curve.png     (Exp 6)
  - hysteresis_collapse.png (Exp 7) — the headline
  - phase_boundary.png      (Exp 8)
"""
import csv, os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _coerce(s):
    try:
        v = float(s); return int(v) if v.is_integer() else v
    except ValueError:
        return s


def _load_outs(path, key_fields):
    by = defaultdict(list)
    with open(path) as f:
        for r in csv.DictReader(f):
            key = tuple(_coerce(r[k]) for k in key_fields)
            by[key].append(r["outcome"])
    return by


# ─── Exp 5: coupling zoo ─────────────────────────────────────────────────────
def couplings_chart():
    path = os.path.join(ROOT, "experiments/couplings_v1/results.csv")
    by = _load_outs(path, ("phi_mode", "kappa"))
    kappas = sorted({k for (_, k) in by})
    modes = ["additive", "multiplicative", "max", "logsumexp"]
    colors = {"additive":"#d62728","multiplicative":"#2ca02c",
              "max":"#9467bd","logsumexp":"#1f77b4"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    for m in modes:
        ys_fail = [sum(1 for o in by[(m,k)] if o in ("TIMEOUT","PARTNER_DEAD"))/len(by[(m,k)])*100 for k in kappas]
        ys_rescue = [sum(1 for o in by[(m,k)] if o == "PARTNER_RESCUED")/len(by[(m,k)])*100 for k in kappas]
        ax1.plot(kappas, ys_fail, "o-", lw=2.4, ms=8, color=colors[m], label=m)
        ax2.plot(kappas, ys_rescue, "o-", lw=2.4, ms=8, color=colors[m], label=m)

    ax1.set_xlabel("κ — emotion weight", fontsize=12)
    ax1.set_ylabel("Failure rate (%)", fontsize=12)
    ax1.set_title("Failure rate vs κ — four Φ couplings", fontsize=12)
    ax1.set_ylim(-5, 105); ax1.grid(alpha=0.3); ax1.legend(fontsize=10)

    ax2.set_xlabel("κ — emotion weight", fontsize=12)
    ax2.set_ylabel("Partner rescue rate (%)", fontsize=12)
    ax2.set_title("Partner rescue rate vs κ — four Φ couplings", fontsize=12)
    ax2.set_ylim(-5, 105); ax2.grid(alpha=0.3); ax2.legend(fontsize=10)

    plt.suptitle(
        "No-free-lunch confirmed across four couplings.\n"
        "Each Φ form has a distinct pathology — none gives both no-paralysis AND rescue capacity.",
        fontsize=13, y=1.02
    )
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/couplings_v1/couplings_zoo.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(); print(f"Wrote {out}")


# ─── Exp 6: resonance ────────────────────────────────────────────────────────
def resonance_chart():
    path = os.path.join(ROOT, "experiments/resonance_v1/results.csv")
    by = _load_outs(path, ("noise", "kappa"))
    noises = sorted({n for (n,_) in by})
    kappas = sorted({k for (_,k) in by})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))

    cmap = plt.cm.plasma(np.linspace(0.1, 0.9, len(kappas)))
    for i, k in enumerate(kappas):
        ys_fail = [sum(1 for o in by[(n,k)] if o in ("TIMEOUT","PARTNER_DEAD"))/len(by[(n,k)])*100 for n in noises]
        ys_rescue = [sum(1 for o in by[(n,k)] if o == "PARTNER_RESCUED")/len(by[(n,k)])*100 for n in noises]
        ax1.plot(noises, ys_fail, "o-", lw=2.2, ms=7, color=cmap[i], label=f"κ={k}")
        ax2.plot(noises, ys_rescue, "o-", lw=2.2, ms=7, color=cmap[i], label=f"κ={k}")

    for ax in (ax1, ax2):
        ax.set_xscale("symlog", linthresh=0.01)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=10, title="emotion weight")
        ax.set_xlabel("σ — emotion noise stddev (per step)", fontsize=12)
        ax.set_ylim(-5, 105)
    ax1.set_ylabel("Failure rate (%)", fontsize=12)
    ax2.set_ylabel("Partner rescue rate (%)", fontsize=12)
    ax1.set_title("Noise barely moves the deep valley (κ=0.25)", fontsize=12)
    ax2.set_title("Noise rescues partner ONLY at the valley shoulder (κ=0.5)", fontsize=12)

    plt.suptitle(
        "Stochastic resonance is local. Noise rescues agents at the valley shoulder, not at its bottom.",
        fontsize=13, y=1.02
    )
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/resonance_v1/resonance_curve.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(); print(f"Wrote {out}")


# ─── Exp 7: hysteresis (the headline) ────────────────────────────────────────
def hysteresis_chart():
    path = os.path.join(ROOT, "experiments/hysteresis_v1/results.csv")
    # Build agents[(k, agent_id)] = {ep_idx: outcome}
    agents = defaultdict(dict)
    with open(path) as f:
        for r in csv.DictReader(f):
            agents[(float(r["kappa"]), int(r["agent_id"]))][int(r["episode_idx"])] = r["outcome"]
    ks = sorted({k for (k,_) in agents})

    # Population outcome distribution by episode index, per kappa
    fig, axes = plt.subplots(1, len(ks), figsize=(15, 6), sharey=True)
    for ax, k in zip(axes, ks):
        by_ep = defaultdict(list)
        for (kk, aid), eps in agents.items():
            if kk != k: continue
            for e_idx, out in eps.items():
                by_ep[e_idx].append(out)
        eps_idx = sorted(by_ep.keys())
        rescues = [sum(1 for x in by_ep[e] if x=="PARTNER_RESCUED")/len(by_ep[e])*100 for e in eps_idx]
        resources = [sum(1 for x in by_ep[e] if x=="RESOURCE_TAKEN")/len(by_ep[e])*100 for e in eps_idx]
        fails = [sum(1 for x in by_ep[e] if x in ("TIMEOUT","PARTNER_DEAD"))/len(by_ep[e])*100 for e in eps_idx]
        ax.plot(eps_idx, rescues, "o-", lw=2.4, ms=8, color="#2ca02c", label="rescued")
        ax.plot(eps_idx, resources, "s-", lw=2.4, ms=8, color="#1f77b4", label="resource")
        ax.plot(eps_idx, fails, "^-", lw=2.4, ms=8, color="#d62728", label="failed")
        ax.set_xlabel("episode in chain", fontsize=11)
        ax.set_title(f"κ = {k}", fontsize=12)
        ax.set_ylim(-5, 105); ax.grid(alpha=0.3)
        ax.legend(fontsize=10, loc="center right")
        if ax is axes[0]:
            ax.set_ylabel("% of population", fontsize=11)
    plt.suptitle(
        "Self-memory homogenizes the population — rescue capacity COLLAPSES after episode 1.\n"
        "Even at κ=1.0 (the committed regime), chained agents lose the ability to rescue.",
        fontsize=13, y=1.03
    )
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/hysteresis_v1/hysteresis_collapse.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(); print(f"Wrote {out}")


# ─── Exp 8: phase boundary (high-res) ────────────────────────────────────────
def phase_boundary_chart():
    path = os.path.join(ROOT, "experiments/phase_boundary_v1/results.csv")
    by = _load_outs(path, ("t_snap", "kappa"))
    ts = sorted({t for (t,_) in by})
    ks = sorted({k for (_,k) in by})

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = {8:"#d62728", 12:"#ff7f0e", 20:"#2ca02c"}
    for t in ts:
        ys = [sum(1 for o in by[(t,k)] if o in ("TIMEOUT","PARTNER_DEAD"))/len(by[(t,k)])*100 for k in ks]
        ax.plot(ks, ys, "-", lw=2.4, color=colors[t], label=f"T_snap = {t}")
        # Mark peak
        peak_i = int(np.argmax(ys))
        ax.scatter([ks[peak_i]], [ys[peak_i]], s=140, color=colors[t],
                   edgecolor="black", lw=1.5, zorder=5)
        ax.annotate(f"peak: {ys[peak_i]:.0f}% @ κ={ks[peak_i]:.2f}",
                    xy=(ks[peak_i], ys[peak_i]),
                    xytext=(ks[peak_i]+0.05, ys[peak_i]+3),
                    fontsize=10, color=colors[t], fontweight="bold")

    ax.axhline(50, ls="--", color="gray", alpha=0.5)
    ax.text(0.92, 52, "50% threshold", fontsize=9, color="gray", ha="right")
    ax.set_xlabel("κ — emotion weight (high resolution: 41 points)", fontsize=12)
    ax.set_ylabel("Failure rate (%)", fontsize=12)
    ax.set_title(
        "The Paralysis Valley narrows and shifts right as Snap Time grows — but never disappears.\n"
        "More deliberation time gives the agent more chances to commit, but a residual valley persists.",
        fontsize=12, pad=12
    )
    ax.set_ylim(-3, 110); ax.set_xlim(-0.02, 1.02)
    ax.grid(alpha=0.3); ax.legend(fontsize=11)
    plt.tight_layout()
    out = os.path.join(ROOT, "experiments/phase_boundary_v1/phase_boundary.png")
    plt.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(); print(f"Wrote {out}")


def main():
    couplings_chart()
    resonance_chart()
    hysteresis_chart()
    phase_boundary_chart()


if __name__ == "__main__":
    main()
