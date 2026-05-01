"""
Visualize Experiment 9 — Selective encoding vs Homogenization Collapse.

Produces ONE figure (selective_encoding_collapse.png) with two panels:
  1. Population rescue rate per episode, one curve per τ.
  2. Divergence index per episode (rescue-rate gap between agents who
     rescued in ep0 vs agents who did not), one curve per τ.

Also prints the headline numbers.
"""
import csv, os
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "experiments", "selective_encoding_v1", "results.csv")
OUT_PNG = os.path.join(ROOT, "experiments", "selective_encoding_v1",
                       "selective_encoding_collapse.png")


def load():
    rows = []
    with open(RESULTS) as f:
        for r in csv.DictReader(f):
            rows.append({
                "tau": float(r["tau"]),
                "agent_id": int(r["agent_id"]),
                "ep": int(r["episode_idx"]),
                "outcome": r["outcome"],
                "n_memories": int(r["n_memories"]),
                "was_encoded": int(r["was_encoded"]),
                "e_max": float(r["e_max"]),
            })
    return rows


def main():
    rows = load()
    taus = sorted({r["tau"] for r in rows})
    eps = sorted({r["ep"] for r in rows})

    # population rescue rate by (tau, ep)
    pop_rescue = {}
    for tau in taus:
        for ep in eps:
            sel = [r for r in rows if r["tau"] == tau and r["ep"] == ep]
            pop_rescue[(tau, ep)] = (
                100.0 * sum(1 for r in sel if r["outcome"] == "PARTNER_RESCUED")
                / max(1, len(sel))
            )

    # divergence index: rescue-rate gap between ep0-rescuers and ep0-non-rescuers
    # at each episode index.
    by_agent = defaultdict(dict)  # (tau, agent_id) -> {ep: outcome}
    for r in rows:
        by_agent[(r["tau"], r["agent_id"])][r["ep"]] = r["outcome"]

    divergence = {}
    for tau in taus:
        # split agents by ep0 outcome
        ep0_rescuers = [aid for (t, aid), eps_d in by_agent.items()
                        if t == tau and eps_d.get(0) == "PARTNER_RESCUED"]
        ep0_others = [aid for (t, aid), eps_d in by_agent.items()
                      if t == tau and eps_d.get(0) != "PARTNER_RESCUED"]
        for ep in eps:
            def rate(ids):
                if not ids:
                    return None
                hits = sum(1 for aid in ids
                           if by_agent[(tau, aid)].get(ep) == "PARTNER_RESCUED")
                return 100.0 * hits / len(ids)
            r1 = rate(ep0_rescuers)
            r2 = rate(ep0_others)
            if r1 is None or r2 is None:
                divergence[(tau, ep)] = 0.0
            else:
                divergence[(tau, ep)] = abs(r1 - r2)

    # encoding rate: fraction of episodes that wrote to memory
    enc_rate = {}
    for tau in taus:
        sel = [r for r in rows if r["tau"] == tau]
        enc_rate[tau] = 100.0 * sum(r["was_encoded"] for r in sel) / max(1, len(sel))

    # ── Headline numbers ─────────────────────────────────────────────────────
    print("\n=== HEADLINE NUMBERS ===")
    print(f"{'tau':>5} | {'enc%':>6} | {'rescue@ep0':>10} | {'rescue@ep9':>10} | "
          f"{'div@ep9':>8}")
    print("-" * 60)
    for tau in taus:
        print(f"{tau:>5.2f} | {enc_rate[tau]:>6.1f} | "
              f"{pop_rescue[(tau, 0)]:>10.1f} | {pop_rescue[(tau, 9)]:>10.1f} | "
              f"{divergence[(tau, 9)]:>8.1f}")

    headline_div = max(divergence[(tau, 9)] for tau in taus)
    headline_tau = max(taus, key=lambda t: divergence[(t, 9)])
    print(f"\nMax divergence@ep9 = {headline_div:.1f} pts at τ = {headline_tau}")

    # ── Plot ────────────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    cmap = plt.cm.viridis(np.linspace(0.1, 0.9, len(taus)))

    for i, tau in enumerate(taus):
        ys = [pop_rescue[(tau, ep)] for ep in eps]
        ax1.plot(eps, ys, "o-", lw=2.4, ms=8, color=cmap[i],
                 label=f"τ = {tau:.1f}  (enc {enc_rate[tau]:.0f}%)")
        ds = [divergence[(tau, ep)] for ep in eps]
        ax2.plot(eps, ds, "o-", lw=2.4, ms=8, color=cmap[i],
                 label=f"τ = {tau:.1f}")

    ax1.set_xlabel("Episode index in chain", fontsize=12)
    ax1.set_ylabel("Population rescue rate (%)", fontsize=12)
    ax1.set_title("Rescue capacity over chained episodes (κ=1.0)", fontsize=12)
    ax1.set_ylim(-5, 105)
    ax1.set_xticks(eps)
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=9, title="encoding gate")

    ax2.set_xlabel("Episode index in chain", fontsize=12)
    ax2.set_ylabel("Divergence index (%-pt rescue-rate gap)", fontsize=12)
    ax2.set_title("Behavioral type persistence: ep0-rescuers vs others",
                  fontsize=12)
    ax2.set_ylim(-2, max(50, headline_div + 5))
    ax2.set_xticks(eps)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=9, title="encoding gate")

    plt.suptitle(
        "Selective encoding vs Homogenization Collapse (κ=1.0, T_snap=12, "
        "100 agents, 10-episode chains)\n"
        "Higher τ encodes only emotionally-extreme outcomes — does it preserve"
        " between-agent variation?",
        fontsize=13, y=1.02
    )
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"\nWrote {OUT_PNG}")


if __name__ == "__main__":
    main()
