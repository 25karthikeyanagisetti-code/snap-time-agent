"""
Experiment — Capped-Floor Loyalty Sweep (channel symmetry of the source-vs-gate
isomorphism).

Hypothesis (top of research_backlog.md, queued 2026-05-19 from the
seed_refresh_capped HELD result):
  Yesterday's exp_seed_refresh_capped showed that applying the per-dim
  max(stored, floor) guardrail to the SEED memory's stored.emotion every step
  reproduces the seed-only-floor (injection-gate) Δep0 vector at every cell
  swept along the GUILT decay axis (β_guilt ∈ {0.05, 0.15, 0.30, 0.50},
  β_loyalty fixed at 0.05). Max |Δcapped − Δfloor| = 7.5 pts, mean 5.6 pts,
  all inside the 2-SE N=40 band — a clean source-vs-gate isomorphism along
  the guilt axis.

  Yesterday's sweep held β_loyalty=0.05 fixed, so it only exercised the
  guardrail on the GUILT channel (the seed memory's stored.guilt decayed
  hard, stored.loyalty stayed near its encoded 0.6 value). This experiment
  reverses the swept axis: β_guilt=0.05 fixed (mild), β_loyalty swept up to
  the regime-breaking range. With the encoding template at loyalty=0.6 and
  the seed floor at loyalty=0.4, β_loyalty ≥ 0.15 forces stored.loyalty
  below the floor within an episode (factor of 0.85^12 ≈ 0.142 at β=0.15;
  0.70^12 ≈ 0.014 at β=0.30; 0.50^12 ≈ 0.0002 at β=0.50). The guardrail
  has to lift the LOYALTY channel of the seed memory under this sweep —
  exactly the test of whether the floor mechanism is channel-symmetric or
  guilt-privileged.

  Three clean outcomes:
    - HELD: capped reproduces seed_only_floor Δep0 at every β_loyalty cell
      (|Δcapped − Δfloor| ≤ ~7-8 pts, within sampling noise at N=40). The
      source-vs-gate isomorphism is channel-symmetric — the floor mechanism
      is a stored-state property of the seed memory, not a guilt-pathway
      privilege. The architectural compression from yesterday extends: a
      single per-memory floor field + one-line max guardrail handles any
      asymmetric-decay axis.
    - REFUTED: capped diverges from seed_only_floor materially on the
      loyalty-side sweep. Would suggest the injection-time floor table
      privileges the guilt channel via a pathway that isn't captured by
      stored-state restoration — perhaps because the recall gate
      (guilt_recall_strength_tag_aware) classifies by GUILT-class tags
      ({seed, failure, timeout}) and uses the source's guilt channel via
      γ·|emotion|, but the literal-stored injection pathway pumps all
      five dims into agent emotion. If the recall pathway is the
      bottleneck along the guilt axis but not the loyalty axis, the
      source-vs-gate equivalence would be one-sided.
    - PARTIAL: capped tracks at mild loyalty asymmetry but diverges at the
      extreme β_loyalty=0.50 cell. Would point to a recall-side asymmetry
      that becomes visible only when the seed memory's loyalty channel
      is entirely cleared.

Sandbox usage:
  Re-uses the seed_refresh_capped_on_recall hook added by exp_seed_refresh_capped
  (2026-05-19). No further extension required. All defaults preserve prior
  experiment behavior.

Design (mirrors exp_seed_refresh_capped exactly, swept axis swapped):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_guilt=0.05 fixed,
  β_loyalty ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10.

  Tag-aware RECALL is ON in every arm — same as yesterday, isolates the
  source-state contribution while holding the recall gate fixed.

  Three modes (same as yesterday):
    inject_mode = "off"                  — baseline (no injection floor, no
                                            source refresh).
    inject_mode = "seed_only_floor"      — tag_aware_injection=True with the
                                            floor table pruned to {seed}.
    inject_mode = "seed_refresh_capped"  — seed_refresh_capped_on_recall=True
                                            with the legacy literal-stored
                                            injection path; NO injection
                                            floor table — the floor lives on
                                            the seed memory itself.

  The capped mode uses the SAME numeric floor values as the seed_only_floor
  table — emotion.TAG_FLOORS_DEFAULT['seed']. That isomorphism is the point
  of the experiment.

  N_AGENTS = 40 per cell (same as yesterday).
  Total: 3 modes × 4 cells × 40 agents × 10 episodes = 4,800 episodes.

Headline metrics:
  - ep0 rescue rate per cell × mode.
  - Δep0 (seed_only_floor − off) and Δep0 (seed_refresh_capped − off) per cell.
  - "Capped-vs-floor substitutability under loyalty decay":
      |Δep0(seed_refresh_capped) − Δep0(seed_only_floor)| per cell.
    If ≤ ~7-8 pts at every cell, the isomorphism is channel-symmetric.
  - ep5–9 mean rescue per cell × mode (long-run secondary).
  - Cross-axis comparison vs yesterday's GUILT-side capped run.
"""
import csv, os, random
from . import sandbox, memory, emotion


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "capped_floor_loyalty_sweep_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_GUILT = 0.05
BETA_LOYALTYS = [0.05, 0.15, 0.30, 0.50]
INJECT_MODES = ["off", "seed_only_floor", "seed_refresh_capped"]
CHAIN_LENGTH = 10
N_AGENTS = 40

# Same seed-only floor table used by exp_seed_only_floor.py / yesterday's run.
SEED_ONLY_FLOORS = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}

# Per-memory floor template attached to the seeded prior for the capped
# variant. Numerically identical to TAG_FLOORS_DEFAULT['seed'] — the whole
# point is to test whether moving the SAME numeric floor from the injection
# gate to the stored-state guardrail is operationally equivalent along the
# loyalty decay axis the same way it was along the guilt decay axis.
SEED_REFRESH_FLOOR = dict(emotion.TAG_FLOORS_DEFAULT["seed"])


def _decay_dict(beta_guilt, beta_loyalty):
    return {
        "survival": 0.0,
        "guilt": beta_guilt,
        "loyalty": beta_loyalty,
        "fear": 0.0,
        "curiosity": 0.0,
    }


def _outcome_to_tag(outcome):
    if outcome == "PARTNER_RESCUED":
        return "rescue"
    if outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        return "failure"
    return "timeout"


def _mode_args(mode):
    """Translate inject_mode into the (tag_aware_injection, tag_floors,
    seed_refresh_capped) triple that run_episode expects."""
    if mode == "off":
        return False, None, False
    if mode == "seed_only_floor":
        return True, SEED_ONLY_FLOORS, False
    if mode == "seed_refresh_capped":
        return False, None, True
    raise ValueError(f"Unknown inject_mode: {mode}")


def run():
    rows = []
    seed = 122000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, capped = _mode_args(inj_mode)
        for beta_l in BETA_LOYALTYS:
            decay = _decay_dict(BETA_GUILT, beta_l)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(
                    M, severity=SEVERITY, preage=15
                )
                # Tag the seeded prior AND attach the per-memory floor
                # template so the capped path can find it. Outcome memories
                # deliberately do NOT get encoding_emotion_floor — the
                # capped hook is seed-only by construction.
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
                        tag_aware_recall=True,                       # always on
                        tag_aware_injection=tag_inj,                 # swept
                        tag_floors=tag_floors,                       # swept
                        seed_refresh_capped_on_recall=capped,        # swept
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                    rows.append({
                        "inject_mode": inj_mode,
                        "beta_guilt": BETA_GUILT,
                        "beta_loyalty": beta_l,
                        "kappa": KAPPA,
                        "agent_id": agent_id,
                        "episode_idx": ep_idx,
                        "outcome": outcome,
                        "rescued": rescued,
                        "n_memories": len(M),
                        "target_switches": r["target_switches"],
                    })

    with open(OUT_RESULTS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} episode rows to {OUT_RESULTS}")


if __name__ == "__main__":
    run()
