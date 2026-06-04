"""
Experiment — Impact Decomp Beta Sweep.

Hypothesis (top of research_backlog.md, queued 2026-05-29 from
capped_floor_impact_decomp Prediction B CONFIRMED):

  The 2026-05-29 capped_floor_impact_decomp experiment confirmed Prediction B:
  at β_loyalty=0.50, seed_refresh_capped inflates the seed memory's MemoryImpact
  by 0.113 vs seed_only_floor, yet rescues 7.5 pts LESS (72.5% vs 80.0%). The
  mechanism: amplified guilt recall via the γ·|emotion| term over-steers the
  agent without improving action timing.

  But that experiment only swept two endpoint cells (β_loyalty ∈ {0.05, 0.50}).
  The fine structure is unknown: at what loyalty-decay rate does the impact gap
  first cross the 0.05 threshold where it becomes mechanistically meaningful?
  And at that same threshold, does the rescue penalty first become detectable
  (>5 pts vs seed_only_floor)?

  This experiment sweeps β_loyalty ∈ {0.10, 0.20, 0.30, 0.40, 0.50} at
  β_guilt=0.05 fixed — five finely-spaced cells filling in the unexplored
  interior of the β_loyalty axis.

  Predictions:
    A: The impact gap grows monotonically in β_loyalty (more decay → more
       divergence between capped and floor modes).
    B: There is a threshold β_loyalty* ∈ (0.05, 0.50) where impact gap first
       crosses 0.05 — identifying where the over-steering mechanism activates.
    C: The rescue penalty becomes detectable (>5 pts) at or above β_loyalty*,
       confirming that impact inflation and rescue harm co-occur.

Design:
  - Same framework as capped_floor_impact_decomp but fine-grained β_loyalty axis
  - β_guilt = 0.05 fixed (matches the prior endpoint experiments)
  - β_loyalty ∈ {0.10, 0.20, 0.30, 0.40, 0.50}
  - Three modes: off, seed_only_floor, seed_refresh_capped
  - N_AGENTS = 40 per cell, chain_length = 10
  - collect_impact_trace = True for both non-off modes

Metrics:
  - Mean seed impact at ep0 per (mode, β_loyalty)
  - Impact gap: mean_impact(capped) − mean_impact(floor) at ep0
  - ep0 rescue rates per (mode, β_loyalty)
  - Rescue penalty: rescue_rate(floor) − rescue_rate(capped)
  - Threshold: first β_loyalty where impact_gap > 0.05

CSV schema:
  results_macro.csv — one row per (mode, beta_loyalty, agent_id, episode_idx)
  results_trace.csv — one row per (mode, beta_loyalty, agent_id, episode_idx, step)

Total episodes: 3 modes × 5 cells × 40 agents × 10 episodes = 6,000
"""

import csv, os, random
from . import sandbox, memory, emotion

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "impact_decomp_beta_sweep_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_MACRO = os.path.join(OUT_DIR, "results_macro.csv")
OUT_TRACE = os.path.join(OUT_DIR, "results_trace.csv")

T_SNAP         = 12
KAPPA          = 1.0
SEVERITY       = 1.0
RESCUE_IMP     = 0.7
BETA_GUILT     = 0.05   # fixed
BETA_LOYALTIES = [0.10, 0.20, 0.30, 0.40, 0.50]  # fine sweep
INJECT_MODES   = ["off", "seed_only_floor", "seed_refresh_capped"]
CHAIN_LENGTH   = 10
N_AGENTS       = 40

SEED_ONLY_FLOORS  = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}
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
    seed = 330000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, capped = _mode_args(inj_mode)
        do_trace = (inj_mode != "off")  # off has no seed-memory tracking
        for beta_l in BETA_LOYALTIES:
            decay = _decay_dict(BETA_GUILT, beta_l)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
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
                        collect_impact_trace=do_trace,
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0

                    macro_rows.append({
                        "mode":         inj_mode,
                        "beta_guilt":   BETA_GUILT,
                        "beta_loyalty": beta_l,
                        "agent_id":     agent_id,
                        "episode_idx":  ep_idx,
                        "outcome":      outcome,
                        "rescued":      rescued,
                        "n_memories":   len(M),
                    })

                    if do_trace:
                        for tr in r.get("impact_trace", []):
                            trace_rows.append({
                                "mode":                inj_mode,
                                "beta_guilt":          BETA_GUILT,
                                "beta_loyalty":        beta_l,
                                "agent_id":            agent_id,
                                "episode_idx":         ep_idx,
                                "step":                tr["step"],
                                "seed_impact":         tr["seed_impact"],
                                "top1_is_seed":        tr["top1_is_seed"],
                                "seed_stored_guilt":   tr["seed_stored_guilt"],
                                "seed_stored_loyalty": tr["seed_stored_loyalty"],
                                "seed_age":            tr["seed_age"],
                            })

    # Write macro CSV
    with open(OUT_MACRO, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=macro_rows[0].keys())
        w.writeheader(); w.writerows(macro_rows)
    print(f"Macro CSV: {len(macro_rows)} rows → {OUT_MACRO}")

    if trace_rows:
        with open(OUT_TRACE, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=trace_rows[0].keys())
            w.writeheader(); w.writerows(trace_rows)
        print(f"Trace CSV: {len(trace_rows)} rows → {OUT_TRACE}")

    # ── Summary ──────────────────────────────────────────────────────────────
    from collections import defaultdict

    ep0_rescued = defaultdict(int)
    ep0_total   = defaultdict(int)
    for row in macro_rows:
        if row["episode_idx"] == 0:
            k = (row["mode"], row["beta_loyalty"])
            ep0_total[k]   += 1
            ep0_rescued[k] += row["rescued"]

    # Per-step mean seed impact at ep0 per (mode, beta_loyalty)
    imp_sum   = defaultdict(float)
    imp_count = defaultdict(int)
    for tr in trace_rows:
        if tr["episode_idx"] == 0:
            k = (tr["mode"], tr["beta_loyalty"])
            imp_sum[k]   += tr["seed_impact"]
            imp_count[k] += 1

    print("\nep0 rescue rates + impact gap:")
    print(f"{'β_loyalty':>10}  {'off%':>6}  {'floor%':>7}  {'capped%':>8}  "
          f"{'rescue_penalty':>14}  {'impact_gap':>10}")
    for beta_l in BETA_LOYALTIES:
        off_pct    = 100.0 * ep0_rescued[("off",              beta_l)] / max(ep0_total[("off",              beta_l)], 1)
        floor_pct  = 100.0 * ep0_rescued[("seed_only_floor",  beta_l)] / max(ep0_total[("seed_only_floor",  beta_l)], 1)
        capped_pct = 100.0 * ep0_rescued[("seed_refresh_capped", beta_l)] / max(ep0_total[("seed_refresh_capped", beta_l)], 1)
        rescue_pen = floor_pct - capped_pct  # positive = floor rescues more

        fl_imp  = imp_sum[("seed_only_floor",     beta_l)] / max(imp_count[("seed_only_floor",     beta_l)], 1)
        cap_imp = imp_sum[("seed_refresh_capped", beta_l)] / max(imp_count[("seed_refresh_capped", beta_l)], 1)
        gap     = cap_imp - fl_imp  # positive = capped inflates impact

        print(f"{beta_l:>10.2f}  {off_pct:>6.1f}  {floor_pct:>7.1f}  {capped_pct:>8.1f}  "
              f"{rescue_pen:>14.1f}  {gap:>10.4f}")


if __name__ == "__main__":
    run()
