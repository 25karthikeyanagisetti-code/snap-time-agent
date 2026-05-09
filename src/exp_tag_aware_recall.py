"""
Experiment 17 — Tag-Aware Recall.

Hypothesis (top of research_backlog.md, elevated 2026-05-07, promoted further
2026-05-08 after laundering_kappa_invariance pinned the decay-arithmetic
layer):
  If we modify the recall pathway so a memory's class identity is determined
  by its encoding-time tag (seed / failure / timeout / rescue) rather than by
  its currently stored emotion channels, the divergence-erosion observed in
  decay_asymmetry_reversed under asymmetric β_guilt should DISAPPEAR.

  In the 2026-05-07 audit we showed that under β_guilt ∈ {0.15, 0.30, 0.50}
  with β_loyalty=0.05, ~75–81% of failure-tagged memories have stored
  loyalty > stored guilt at end-of-ep4 — they are "valence-laundered" by the
  decay arithmetic. The 2026-05-08 κ-invariance check confirmed this happens
  identically at κ=0.5. Macro divergence@5–9 erodes from +13.3 → +3.6 → −1.5
  pts as β_guilt grows.

  guilt_recall_strength is the gateway from M into the guilt component of
  e_t (via emo_ctx['guilt_recall'] feeding GUILT_RATE in step_emotion). In
  the legacy form it asks: "is stored.guilt > 0.4?" — a current-state
  classification that flips to FALSE under laundering. The tag-aware form
  asks: "was this memory a guilt event at encoding time?" — class identity
  pinned to origin, immune to decay.

  Two clean outcomes:
    - HYPOTHESIS HELD: divergence@5–9 stays near +10–13 pts across
      β_guilt ∈ {0.05, 0.15, 0.30, 0.50} under tag-aware recall. Confirms
      laundering IS the mechanism — the type-erosion story bottoms out at
      stored.guilt no longer counting as "guilt" in the recall gate.
    - HYPOTHESIS REFUTED: divergence@5–9 still erodes under tag-aware recall
      (same +13 → ~0 → negative trajectory). Laundering is NOT the
      operative mechanism — recall-event statistics, agent position at the
      moment of recall, or another non-decay-arithmetic effect carries the
      swing.
    - SPLIT: tag-aware recall partially restores divergence (e.g. holds at
      mid-β but breaks at extreme β_guilt=0.50). Tells us laundering is one
      of two mechanisms — at extreme decay something else collapses too
      (likely the regime-break observed in decay_asymmetry_reversed where
      ep0 dropped 84% → 44%).

Sandbox extension:
  - memory.guilt_recall_strength_tag_aware: NEW function. Tag-keyed variant
    of guilt_recall_strength. Falls back to legacy stored.guilt > 0.4 when
    a memory has no 'tag' key — preserves all prior experiment behavior.
  - sandbox.run_episode now accepts tag_aware_recall (default False). When
    True, routes the in-episode guilt recall through the tag-aware variant.
    Default off — every prior experiment is byte-for-byte unchanged.

Design (matches decay_asymmetry_reversed / memory_population_audit baseline):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10.

  Two arms:
    tag_aware = False  (control — replicates the 2026-05-06 baseline)
    tag_aware = True   (treatment — routes recall through tags)

  N_AGENTS = 50 per cell to stay under 5k cap.
  Total: 2 modes × 4 cells × 50 agents × 10 episodes = 4,000 episodes.

  We tag the seeded prior as 'seed' and each outcome-encoded memory by
  outcome class, AT THE EXPERIMENT LEVEL — same instrumentation as
  exp_memory_population_audit. The sandbox itself never reads or writes
  the 'tag' field, so this stays additive.

Headline metric:
  divergence@5–9 per cell × mode. Direct comparison shows whether tag-aware
  recall preserves the symmetric-β divergence under asymmetric β_guilt.

  Secondary: ep0 rescue rate per cell × mode (regime-break check at high
  β_guilt), ep5–9 mean rescue per cell × mode (boomerang baseline).
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "tag_aware_recall_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
TAG_AWARE_MODES = [False, True]
CHAIN_LENGTH = 10
N_AGENTS = 50


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


def run():
    rows = []
    seed = 73000
    for tag_mode in TAG_AWARE_MODES:
        for beta_g in BETA_GUILTS:
            decay = _decay_dict(beta_g, BETA_LOYALTY)
            for agent_id in range(N_AGENTS):
                rng = random.Random(seed); seed += 1
                M = memory.init_store()
                sandbox._seed_abandonment_memory(
                    M, severity=SEVERITY, preage=15
                )
                # Tag the seeded prior so tag-aware recall can identify it.
                M[0]["tag"] = "seed"
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
                        tag_aware_recall=tag_mode,
                    )
                    M = r["memory_store"]
                    outcome = r["outcome"]
                    # Tag any newly-appended memory by outcome class so the
                    # NEXT episode's tag-aware recall can see its origin.
                    if len(M) > len_before:
                        M[-1]["tag"] = _outcome_to_tag(outcome)
                    rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                    rows.append({
                        "tag_aware": int(tag_mode),
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
