"""
Experiment — Seed-Refresh Capped (max-guardrail at the source).

Hypothesis (top of research_backlog.md, queued 2026-05-18 from the
seed_refresh PARTIAL result):
  Yesterday's exp_seed_refresh tested whether OVERWRITING the seed memory's
  stored.emotion back to its encoding template every step would substitute
  for the tag-floor injection table. It HELD at the regime-breaking
  β_guilt=0.50 cell but REFUTED at low and mild asymmetry, where the
  unconditional refresh over-restored the prior and hurt ep0 by 10 pts.

  The clean diagnosis: it's not the source-refresh idea that fails — it's
  the OVERWRITE. The floor mechanism wins because max(stored, floor) is a
  one-sided guardrail: when stored is above the floor (low β_guilt) it does
  nothing; when stored has decayed below the floor (high β_guilt) it lifts.
  Overwriting forces the floor onto BOTH cases — including the cells where
  stored is healthier than the floor — and that's where ep0 collapses.

  This experiment isolates that diagnosis. It applies the SAME max(stored,
  floor) operator that emotion.inject_recalled_emotion_tag_aware uses at
  the injection gate, but moves it one step earlier — onto the stored
  emotion of the seed memory itself, at the start of every step before
  recall is computed.

  Three clean outcomes:
    - HELD: seed_refresh_capped matches seed_only_floor Δep0 at every β_guilt
      cell (within sampling noise — 2-SE ≈ 7-9 pts at N=40). The operative
      mechanism is "max-guardrail applied to the seed memory's stored state."
      The entire tag-floor injection dispatch table compresses to a single
      per-memory `floor` field at encoding time — no per-tag dispatch needed
      and no injection-time logic — and seed_refresh's β_guilt=0.05 over-
      restoration pathology is eliminated.
    - REFUTED: capped matches seed_only_floor only at the regime-breaking
      cell (mirrors raw seed_refresh's PARTIAL result). The floor operator
      at the INJECTION GATE differs from the same operator applied to the
      stored state — perhaps because the gain-multiplied injection path
      compounds differently from the recall-strength path that uses
      stored.emotion via the γ·|emotion| MemoryImpact term.
    - PARTIAL: capped matches at the regime-breaking cell AND at low
      asymmetry but diverges at mild asymmetry. Would suggest stored-state
      restoration helps at the extreme decay rates (where recall-strength
      and injection both decay heavily) but not at intermediate cells where
      one channel matters more than the other.

Sandbox extension:
  src/sandbox.py: new optional run_episode kwarg `seed_refresh_capped_on_recall`
  (default False — preserves all prior experiment behavior). When True,
  every step BEFORE recall iterates the memory store and for any memory
  carrying tag='seed' AND a per-memory 'encoding_emotion_floor' template,
  applies stored.emotion[k] = max(stored[k], floor[k]) on every emotion dim.
  The memory's age keeps ticking up — only the stored emotion floor is
  enforced.

Design (matches exp_seed_refresh_v1 exactly, with the refresh arm replaced
by capped-refresh):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10.

  Tag-aware RECALL is ON in every arm — we're isolating the source-state
  contribution while holding the recall gate fixed.

  Three modes:
    inject_mode = "off"                  — baseline (no injection floor, no
                                            source refresh). Replicates the
                                            tag_aware_recall INJ-OFF arm.
    inject_mode = "seed_only_floor"      — tag_aware_injection=True with the
                                            floor table pruned to {seed}.
                                            Replicates seed_only_floor_v1 /
                                            the headline floor arm.
    inject_mode = "seed_refresh_capped"  — seed_refresh_capped_on_recall=True
                                            with the legacy literal-stored
                                            injection path. NO injection
                                            floor table — the floor lives on
                                            the seed memory itself.

  The capped mode uses the SAME numeric floor values as the seed_only_floor
  table — emotion.TAG_FLOORS_DEFAULT['seed']. That isomorphism is the point
  of the experiment.

  We tag the seeded prior as 'seed' AND attach SEED_REFRESH_FLOOR to
  m["encoding_emotion_floor"] so the capped path can find the template at
  every step. Outcome-encoded memories are NOT given an encoding_emotion_floor
  field — so the capped hook is a no-op on them (matches the hypothesis:
  the guardrail is seed-only).

  N_AGENTS = 40 per cell (same as exp_seed_refresh_v1).
  Total: 3 modes × 4 cells × 40 agents × 10 episodes = 4,800 episodes.

Headline metrics:
  - ep0 rescue rate per cell × mode.
  - Δep0 (seed_only_floor − off) and Δep0 (seed_refresh_capped − off) per
    cell.
  - "Capped-vs-floor substitutability":
      |Δep0(seed_refresh_capped) − Δep0(seed_only_floor)| per cell.
    If ≤ ~5 pts at every cell, the two mechanisms are operationally
    interchangeable and the tag-floor dispatch can be moved entirely to
    encoding-time per-memory floor attachment.
  - ep5–9 mean rescue per cell × mode (long-run secondary).
  - For direct comparison to yesterday's PARTIAL result: pull the
    seed_refresh_v1 results and report the Δep0 vector triple
    (off → seed_only_floor → seed_refresh_capped → seed_refresh) in the
    README.
"""
import csv, os, random
from . import sandbox, memory, emotion


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "seed_refresh_capped_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
INJECT_MODES = ["off", "seed_only_floor", "seed_refresh_capped"]
CHAIN_LENGTH = 10
N_AGENTS = 40

# Same seed-only floor table used by exp_seed_only_floor.py — single entry.
SEED_ONLY_FLOORS = {"seed": emotion.TAG_FLOORS_DEFAULT["seed"]}

# Per-memory floor template attached to the seeded prior for the capped
# variant. Numerically identical to TAG_FLOORS_DEFAULT['seed'] — the whole
# point is to test whether moving the SAME numeric floor from the injection
# gate to the stored-state guardrail is operationally equivalent.
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
    seed = 119000
    for inj_mode in INJECT_MODES:
        tag_inj, tag_floors, capped = _mode_args(inj_mode)
        for beta_g in BETA_GUILTS:
            decay = _decay_dict(beta_g, BETA_LOYALTY)
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
                        "beta_guilt": beta_g,
                        "beta_loyalty": BETA_LOYALTY,
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
