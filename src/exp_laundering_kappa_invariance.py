"""
Experiment 16 — Laundering κ-Invariance.

Hypothesis (top of research_backlog.md, elevated 2026-05-07):
  Replicate the 2026-05-07 memory_population_audit at κ=0.5 (the boomerang
  SHOULDER) instead of κ=1.0 (the deep committed regime). The 05-07 audit
  established that asymmetric forgiveness (β_guilt > β_loyalty) "launders"
  failure-tagged memories — at β_guilt=0.15 roughly 78% of failure-tagged
  memories have stored loyalty > stored guilt at recall time, vs 0% in the
  symmetric β=0.05 cell. The mechanism is purely a property of decay
  arithmetic acting on the encoded emotion vector — it should NOT depend on
  whether the agent is in the deep-committed regime (κ=1.0) or the boomerang
  shoulder (κ=0.5).

  This run is a clean κ-invariance check on the laundering microstructure.
  Predicts: laundering rate ≈ 75–78% at β_guilt ∈ {0.15, 0.30, 0.50}
  regardless of κ. Macro behavior (ep0 rescue, divergence@5–9) may differ
  because κ=0.5 has a different baseline rescue regime, but the per-memory
  channel collapse should look identical.

Why this is the right next dial:
  - If laundering rate is κ-invariant: the 05-07 mechanism reading is
    confirmed at the level of decay arithmetic. Promotes recharge_on_recall
    as the right counter-mechanism candidate.
  - If laundering rate DEPENDS on κ: the mechanism couples to recall-event
    statistics (which memories actually fire during a low-κ episode), not
    just to the static decay equations. Pushes recall_event_trace and
    tag_aware_recall up the queue.
  - If laundering rate is κ-invariant but macro divergence INVERTS sign at
    κ=0.5 (or stays flat): it tells us the laundering microstructure is
    only one of two mechanisms in play. The other one is regime-specific.

Sandbox extension:
  None. We re-use the same instrumentation as
  exp_memory_population_audit.py — tag each encoded memory at the call
  site with 'seed' / 'rescue' / 'failure' / 'timeout' AFTER sandbox
  returns. memory.encode and the sandbox itself are untouched. This
  preserves all prior experiment behavior.

Design (matches exp_memory_population_audit exactly except for κ):
  T_snap = 12, kappa = 0.5, severity = 1.0, positive_encoding = True,
  rescue_importance = 0.7, β_loyalty = 0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length = 10, n_agents = 100.

  Snapshot points: end of episode_idx = 4 (gateway into divergence@5–9
  window) and end of episode_idx = 9 (final state of the chain).

  Total: 4 cells × 100 agents × 10 episodes = 4,000 episodes (under 5k cap).

Per-memory snapshot fields:
  - beta_guilt, beta_loyalty (cell index)
  - kappa (0.5 — for cross-experiment join with the κ=1.0 audit)
  - agent_id, ep0_outcome, ep1_outcome
  - snapshot_after_ep, mem_idx
  - tag: 'seed' | 'failure' | 'rescue' | 'timeout' (origin at encoding)
  - age, importance
  - stored guilt, loyalty, survival, fear, curiosity
  - emo_magnitude (L1 norm — the input to γ·|e| in MemoryImpact)
  - mem_class: 'guilt' if stored.guilt > stored.loyalty (current decayed
    state), 'loyalty' if reversed, 'neutral' if exact tie

Headline metrics:
  - Laundering rate per cell: % of failure-tagged memories at end-of-ep4
    where stored.loyalty > stored.guilt + ε. Compare against the κ=1.0
    audit numbers {0%, 78%, 75%, 78%}.
  - Per-agent Σ stored guilt and Σ stored loyalty per cell (channel
    collapse pattern).
  - Macro: ep0 rescue, ep5–9 mean rescue, divergence@5–9. (Boomerang at
    κ=0.5 in the symmetric β=0.05 cell was previously +1–5% at ep5–9.)
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "laundering_kappa_invariance_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")
OUT_SNAPSHOT = os.path.join(OUT_DIR, "memory_snapshot.csv")

T_SNAP = 12
KAPPA = 0.5                    # boomerang shoulder (vs 1.0 in the prior audit)
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
CHAIN_LENGTH = 10
N_AGENTS = 100
SNAPSHOT_EPS = [4, 9]


def _decay_dict(beta_guilt, beta_loyalty):
    return {
        "survival": 0.0,
        "guilt": beta_guilt,
        "loyalty": beta_loyalty,
        "fear": 0.0,
        "curiosity": 0.0,
    }


def _classify_current(em):
    """Classify a memory by its CURRENT (decayed) stored emotion."""
    g = em.get("guilt", 0.0)
    l = em.get("loyalty", 0.0)
    if g > l + 1e-9:
        return "guilt"
    if l > g + 1e-9:
        return "loyalty"
    return "neutral"


def _emag(em):
    return sum(abs(v) for v in em.values())


def _outcome_to_tag(outcome):
    if outcome == "PARTNER_RESCUED":
        return "rescue"
    if outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        return "failure"
    return "timeout"


def run():
    rows = []
    snap_rows = []
    # Different seed base than the κ=1.0 audit to avoid identical RNG paths.
    seed = 71000
    for beta_g in BETA_GUILTS:
        decay = _decay_dict(beta_g, BETA_LOYALTY)
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            # Tag the seeded prior so we can distinguish it from agent-encoded
            # memories at snapshot time.
            M[0]["tag"] = "seed"
            ep0_outcome = None
            ep1_outcome = None
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
                )
                M = r["memory_store"]
                outcome = r["outcome"]
                # Tag any newly-appended memory with its outcome class.
                if len(M) > len_before:
                    M[-1]["tag"] = _outcome_to_tag(outcome)
                rescued = 1 if outcome == "PARTNER_RESCUED" else 0
                if ep_idx == 0:
                    ep0_outcome = outcome
                if ep_idx == 1:
                    ep1_outcome = outcome
                rows.append({
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
                if ep_idx in SNAPSHOT_EPS:
                    for m_idx, mem in enumerate(M):
                        em = mem["emotion"]
                        snap_rows.append({
                            "beta_guilt": beta_g,
                            "beta_loyalty": BETA_LOYALTY,
                            "kappa": KAPPA,
                            "agent_id": agent_id,
                            "ep0_outcome": ep0_outcome,
                            "ep1_outcome": ep1_outcome,
                            "snapshot_after_ep": ep_idx,
                            "mem_idx": m_idx,
                            "tag": mem.get("tag", "untagged"),
                            "age": mem["age"],
                            "importance": mem["importance"],
                            "guilt": em.get("guilt", 0.0),
                            "loyalty": em.get("loyalty", 0.0),
                            "survival": em.get("survival", 0.0),
                            "fear": em.get("fear", 0.0),
                            "curiosity": em.get("curiosity", 0.0),
                            "emo_magnitude": _emag(em),
                            "mem_class": _classify_current(em),
                        })
    with open(OUT_RESULTS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    with open(OUT_SNAPSHOT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=snap_rows[0].keys())
        w.writeheader(); w.writerows(snap_rows)
    print(f"Wrote {len(rows)} episode rows to {OUT_RESULTS}")
    print(f"Wrote {len(snap_rows)} memory snapshot rows to {OUT_SNAPSHOT}")


if __name__ == "__main__":
    run()
