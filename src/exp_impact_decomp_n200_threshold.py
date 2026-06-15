"""
Experiment — Impact Decomp N=200 Threshold Replication.

Hypothesis (top of research_backlog.md, queued 2026-06-04 from
impact_decomp_beta_sweep PARTIAL):

  The 2026-06-04 impact_decomp_beta_sweep confirmed that the seed impact
  gap between seed_refresh_capped and seed_only_floor grows monotonically
  with β_loyalty, crossing the 0.05 threshold at β_loyalty* ≈ 0.35–0.40.
  However, the rescue penalty (floor − capped rescue rate) was not
  detectable at N=40 (range ±7.5 pts, inside 2-SE ≈ 14 pts).

  This experiment replications the two threshold-straddling cells:
    β_loyalty ∈ {0.30, 0.40}
  at N=200 agents, narrowing the 2-SE band to ~7 pts.

  Predictions:
    A: At β_loyalty=0.30 (below threshold, impact gap ≈ 0.025), rescue
       penalty stays inside ±4 pts → source-vs-gate isomorphism confirmed
       below threshold.
    B: At β_loyalty=0.40 (above threshold, impact gap ≈ 0.060), rescue
       penalty exceeds ±4 pts → impact amplification causes detectable
       over-steering above threshold.

  If both cells fall inside ±4 pts, the isomorphism is complete across the
  full β_loyalty axis, and the 0.05 impact-gap threshold is a mathematical
  artifact with no behavioral correlate.

Design:
  - β_guilt = 0.05 fixed (matches prior experiments)
  - β_loyalty ∈ {0.30, 0.40} (threshold-straddling cells only)
  - Three modes: off, seed_only_floor, seed_refresh_capped
  - N_AGENTS = 200 per cell, chain_length = 10
  - collect_impact_trace = True for non-off modes

Metrics:
  - ep0 rescue rate per (mode, β_loyalty)
  - Rescue penalty: rescue_rate(floor) − rescue_rate(capped)
  - Mean seed impact at ep0 per (mode, β_loyalty)
  - Impact gap: mean_impact(capped) − mean_impact(floor) at ep0

CSV schema:
  results_macro.csv — one row per (mode, beta_loyalty, agent_id, episode_idx)
  results_trace.csv — one row per (mode, beta_loyalty, agent_id, ep, step)

Total episodes: 3 modes × 2 cells × 200 agents × 10 episodes = 12,000
"""

import csv, os, random
from . import sandbox, memory, emotion

OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "impact_decomp_n200_threshold_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_MACRO = os.path.join(OUT_DIR, "results_macro.csv")
OUT_TRACE = os.path.join(OUT_DIR, "results_trace.csv")

T_SNAP         = 12
KAPPA          = 1.0
SEVERITY       = 1.0
RESCUE_IMP     = 0.7
BETA_GUILT     = 0.05
BETA_LOYALTIES = [0.30, 0.40]   # threshold-straddling cells
INJECT_MODES   = ["off", "seed_only_floor", "seed_refresh_capped"]
CHAIN_LENGTH   = 10
N_AGENTS       = 200

SEED_ONLY_FLOORS   = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}
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
    seed = 410000   # fresh RNG seed, distinct from prior experiments
    total_episodes = len(INJECT_MODES) * len(BETA_LOYALTIES) * N_AGENTS * CHAIN_LENGTH
    print(f"Total episodes to run: {total_episodes}")

    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, capped = _mode_args(inj_mode)
        do_trace = (inj_mode != "off")
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

    # Write CSVs
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

    imp_sum   = defaultdict(float)
    imp_count = defaultdict(int)
    for tr in trace_rows:
        if tr["episode_idx"] == 0:
            k = (tr["mode"], tr["beta_loyalty"])
            imp_sum[k]   += tr["seed_impact"]
            imp_count[k] += 1

    se_factor = (1.0 / (N_AGENTS ** 0.5)) * 50  # ~2-SE estimate for rescue %
    print(f"\nN={N_AGENTS} per cell | 2-SE ≈ {se_factor:.1f} pts for rescue rates")
    print(f"\nep0 rescue rates + impact gap (β_guilt=0.05 fixed):")
    print(f"{'β_loyalty':>10}  {'off%':>6}  {'floor%':>7}  {'capped%':>8}  "
          f"{'penalty(f-c)':>13}  {'impact_gap':>11}  {'conclusion':>18}")

    results = {}
    for beta_l in BETA_LOYALTIES:
        off_pct    = 100.0 * ep0_rescued[("off",                 beta_l)] / max(ep0_total[("off",                 beta_l)], 1)
        floor_pct  = 100.0 * ep0_rescued[("seed_only_floor",     beta_l)] / max(ep0_total[("seed_only_floor",     beta_l)], 1)
        capped_pct = 100.0 * ep0_rescued[("seed_refresh_capped", beta_l)] / max(ep0_total[("seed_refresh_capped", beta_l)], 1)
        rescue_pen = floor_pct - capped_pct

        fl_imp  = imp_sum[("seed_only_floor",     beta_l)] / max(imp_count[("seed_only_floor",     beta_l)], 1)
        cap_imp = imp_sum[("seed_refresh_capped", beta_l)] / max(imp_count[("seed_refresh_capped", beta_l)], 1)
        gap     = cap_imp - fl_imp

        conclusion = "isomorphism" if abs(rescue_pen) <= 4.0 else "divergence"
        print(f"{beta_l:>10.2f}  {off_pct:>6.1f}  {floor_pct:>7.1f}  {capped_pct:>8.1f}  "
              f"{rescue_pen:>13.1f}  {gap:>11.4f}  {conclusion:>18}")
        results[beta_l] = {
            "off": off_pct, "floor": floor_pct, "capped": capped_pct,
            "rescue_pen": rescue_pen, "gap": gap,
        }

    # Verdict
    both_iso = all(abs(results[b]["rescue_pen"]) <= 4.0 for b in BETA_LOYALTIES)
    print(f"\nVerdict: {'HELD — isomorphism complete (both cells inside ±4 pts)' if both_iso else 'PARTIAL/FAILED — at least one cell exceeds ±4 pts'}")
    return results


if __name__ == "__main__":
    run()
