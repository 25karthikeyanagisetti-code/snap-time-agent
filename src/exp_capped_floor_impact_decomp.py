"""
Experiment — Capped Floor Impact Decomposition.

Hypothesis (top of research_backlog.md, queued 2026-05-20 as deconfirmation
experiment after the capped_loyalty_n200_endpoints HELD result):

  The N=200 replication at the endpoint cells (β_loyalty ∈ {0.05, 0.50})
  showed that the macro ep0 rescue-rate gap between seed_only_floor and
  seed_refresh_capped collapses to within the 2-SE band (0.0 pts and 3.5 pts
  respectively). That HELD result closes the source-vs-gate isomorphism at the
  MACRO level (episode rescue rates).

  But it leaves open a MICRO question: do the per-step seed-memory impact
  traces ALSO agree across modes, or do the modes differ at the recall-side
  measurement layer with their effects cancelling downstream into the same
  macro outcome?

  Prediction A (consolidated isomorphism): impact traces are within noise
  across modes at both β_loyalty cells. The max-guardrail operator produces
  the same seed-memory impact regardless of where it's applied (stored-state
  source vs injection gate). This means the source-vs-gate equivalence holds
  ALL THE WAY DOWN to the MemoryImpact term.

  Prediction B (downstream cancellation): impact traces DIVERGE across modes
  (e.g. seed_refresh_capped inflates seed impact by boosting the γ·|emotion|
  term) while ep0 rescue rates remain similar. This would mean the two modes
  reach the same outcome via different recall-level computations — an
  architectural difference that matters for any downstream extension (e.g. if
  you add multi-memory blending or a weighted injection rule).

Design:
  - Mirrors exp_seed_refresh_capped_v1 exactly (same params / chain / modes)
  - Adds collect_impact_trace=True to every run_episode call
  - Sweeps β_loyalty ∈ {0.05, 0.50} at β_guilt=0.05 fixed
    (the two endpoints from capped_loyalty_n200_endpoints HELD)
  - Three modes: off, seed_only_floor, seed_refresh_capped
  - N_AGENTS=40, chain_length=10 — same as prior replication chain

Metrics:
  - Per-step seed_impact: mean ± std per (mode, β_loyalty, episode_idx, step)
  - ep0 rescue rates (macro replicate of N=40 endpoints)
  - Max inter-mode impact gap at ep0 across all steps:
      max_step |mean_impact(capped) − mean_impact(floor)| at each β_loyalty cell
  - Also log: seed_stored_guilt, seed_stored_loyalty, seed_age per step

CSV schema (two files):
  results_macro.csv — one row per (mode, beta_loyalty, agent_id, episode_idx):
    mode, beta_loyalty, agent_id, episode_idx, rescued, outcome, n_memories

  results_trace.csv — one row per (mode, beta_loyalty, agent_id, episode_idx, step):
    mode, beta_loyalty, agent_id, episode_idx, step,
    seed_impact, top1_is_seed, seed_stored_guilt, seed_stored_loyalty, seed_age

Total episodes: 3 modes × 2 β_loyalty cells × 40 agents × 10 episodes = 2,400
"""

import csv, os, random
from . import sandbox, memory, emotion

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "capped_floor_impact_decomp_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_MACRO   = os.path.join(OUT_DIR, "results_macro.csv")
OUT_TRACE   = os.path.join(OUT_DIR, "results_trace.csv")

T_SNAP        = 12
KAPPA         = 1.0
SEVERITY      = 1.0
RESCUE_IMP    = 0.7
BETA_GUILT    = 0.05   # fixed — same as seed_refresh_capped sweep axis
BETA_LOYALTIES = [0.05, 0.50]  # the two endpoint cells from capped_loyalty_n200_endpoints
INJECT_MODES  = ["off", "seed_only_floor", "seed_refresh_capped"]
CHAIN_LENGTH  = 10
N_AGENTS      = 40

SEED_ONLY_FLOORS = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}
SEED_REFRESH_FLOOR = dict(emotion.TAG_FLOORS_DEFAULT["seed"])


def _decay_dict(beta_guilt, beta_loyalty):
    return {
        "survival":  0.0,
        "guilt":     beta_guilt,
        "loyalty":   beta_loyalty,
        "fear":      0.0,
        "curiosity": 0.0,
    }


def _outcome_to_tag(outcome):
    if outcome == "PARTNER_RESCUED":
        return "rescue"
    if outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        return "failure"
    return "timeout"


def _mode_args(mode):
    """Return (tag_aware_injection, tag_floors, seed_refresh_capped) triple."""
    if mode == "off":
        return False, None, False
    if mode == "seed_only_floor":
        return True, SEED_ONLY_FLOORS, False
    if mode == "seed_refresh_capped":
        return False, None, True
    raise ValueError(f"Unknown mode: {mode}")


def run():
    macro_rows = []
    trace_rows = []
    seed = 229000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, capped = _mode_args(inj_mode)
        for beta_l in BETA_LOYALTIES:
            decay = _decay_dict(BETA_GUILT, beta_l)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(
                    M, severity=SEVERITY, preage=15
                )
                # Tag the seeded prior and attach per-memory floor for capped mode
                M[0]["tag"] = "seed"
                M[0]["encoding_emotion_floor"] = dict(SEED_REFRESH_FLOOR)
                for ep_idx in range(CHAIN_LENGTH):
                    len_before = len(M)
                    r = sandbox.run_episode(
                        t_snap=T_SNAP, kappa=KAPPA,
                        seed_memory=False,
                        mem_severity=SEVERITY,
                        mem_emotion_decay=decay,
                        carry_memory=M,
                        encode_outcome=True,
                        positive_encoding=True,
                        rescue_importance=RESCUE_IMP,
                        rng=rng,
                        tag_aware_recall=True,
                        tag_aware_injection=tag_inj,
                        tag_floors=tag_floors,
                        seed_refresh_capped_on_recall=capped,
                        collect_impact_trace=True,
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0

                    macro_rows.append({
                        "mode":        inj_mode,
                        "beta_guilt":  BETA_GUILT,
                        "beta_loyalty": beta_l,
                        "agent_id":    agent_id,
                        "episode_idx": ep_idx,
                        "outcome":     outcome,
                        "rescued":     rescued,
                        "n_memories":  len(M),
                    })

                    for tr in r["impact_trace"]:
                        trace_rows.append({
                            "mode":          inj_mode,
                            "beta_guilt":    BETA_GUILT,
                            "beta_loyalty":  beta_l,
                            "agent_id":      agent_id,
                            "episode_idx":   ep_idx,
                            "step":          tr["step"],
                            "seed_impact":   tr["seed_impact"],
                            "top1_is_seed":  tr["top1_is_seed"],
                            "seed_stored_guilt":   tr["seed_stored_guilt"],
                            "seed_stored_loyalty": tr["seed_stored_loyalty"],
                            "seed_age":      tr["seed_age"],
                        })

    # Write macro CSV
    with open(OUT_MACRO, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=macro_rows[0].keys())
        w.writeheader(); w.writerows(macro_rows)
    print(f"Macro CSV: {len(macro_rows)} rows → {OUT_MACRO}")

    # Write trace CSV
    with open(OUT_TRACE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=trace_rows[0].keys())
        w.writeheader(); w.writerows(trace_rows)
    print(f"Trace CSV: {len(trace_rows)} rows → {OUT_TRACE}")

    # Quick summary: ep0 rescue rates per cell
    from collections import defaultdict
    ep0_rescued  = defaultdict(int)
    ep0_total    = defaultdict(int)
    for row in macro_rows:
        if row["episode_idx"] == 0:
            k = (row["mode"], row["beta_loyalty"])
            ep0_total[k]   += 1
            ep0_rescued[k] += row["rescued"]
    print("\nep0 rescue rates:")
    for inj_mode in INJECT_MODES:
        for beta_l in BETA_LOYALTIES:
            k = (inj_mode, beta_l)
            pct = 100.0 * ep0_rescued[k] / ep0_total[k] if ep0_total[k] else float("nan")
            print(f"  {inj_mode:25s}  β_loyalty={beta_l:.2f}  → {pct:.1f}%  (N={ep0_total[k]})")


if __name__ == "__main__":
    run()
