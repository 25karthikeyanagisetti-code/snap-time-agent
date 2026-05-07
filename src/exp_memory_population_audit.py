"""
Experiment 15 — Memory Population Audit (Instrumentation).

Hypothesis (top of research_backlog.md, elevated 2026-05-06):
  Snapshot the M store at ep5 by cell. Count loyalty-class vs guilt-class
  memories and their |emotion| magnitudes. Resolves whether the symmetric
  vs asymmetric divergence-erosion observed in decay_asymmetry and
  decay_asymmetry_reversed is mediated by per-class memory weight, as
  predicted in the original cushion-vs-counterweight reading and partially
  retained in finding_v3's "imbalance erases differentiation" framing.

Why this is the right next dial:
  - 2026-05-05 decay_asymmetry: divergence@5–9 inverts +13.3 → −18.8 pts as
    β_loyalty grows from 0.05 to 0.50 (β_guilt fixed at 0.05).
  - 2026-05-06 decay_asymmetry_reversed: divergence drifts to ~0 across
    β_guilt ∈ {0.05, 0.15, 0.30}, then β_guilt=0.50 breaks the regime
    entirely (ep0 84% → 44%). Two falsifications of the directional reading.
  - Both findings are CONSISTENT with "per-class memory weight in the
    γ·|emotion| recall term mediates the divergence erosion" — but neither
    DIRECTLY MEASURES the per-class weight. This run does, by snapshotting
    the M store and decomposing by class.

Sandbox extension:
  None to memory.py / sandbox.py. We tag each encoded memory at the call
  site (in this experiment file only) by attaching a "tag" key to the dict
  AFTER sandbox.run_episode returns. memory.encode itself is untouched.
  This preserves all prior experiment behavior.

Design (matches decay_asymmetry_reversed exactly, plus instrumentation):
  T_snap=12, kappa=1.0, severity=1.0, positive_encoding=True,
  rescue_importance=0.7, β_loyalty=0.05 fixed,
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}, chain_length=10, n_agents=100.

  Snapshot points: end of episode_idx=4 (gateway into the divergence@5–9
  window) and end of episode_idx=9 (final state of the chain).

  Total: 4,000 episodes (under 5k cap).

Per-memory snapshot fields:
  - beta_guilt, beta_loyalty (cell index)
  - agent_id, ep0_outcome, ep1_outcome (for divergence-class splits)
  - snapshot_after_ep, mem_idx
  - tag: 'seed' | 'failure' | 'rescue' | 'timeout' (origin at encoding)
  - age, importance
  - stored guilt, loyalty, survival, fear, curiosity
  - emo_magnitude (L1 norm — directly enters γ·|e| in recall weight)
  - mem_class: 'guilt' if stored.guilt > stored.loyalty, 'loyalty' if
    stored.loyalty > stored.guilt, 'neutral' otherwise (current-state class)

Headline metrics:
  Mean per-agent stored |emotion| summed within tag-class, at end-of-ep4:
    W_guilt(cell)   = Σ |e| over memories with tag ∈ {seed, failure}
    W_loyalty(cell) = Σ |e| over memories with tag = rescue
  Plus the ratio W_guilt / W_loyalty per cell.

  - If W_guilt collapses monotonically as β_guilt grows AND that collapse
    correlates with the divergence-erosion observed in
    decay_asymmetry_reversed: confirms per-class weight as the mediator.
  - If W_guilt is flat across cells (e.g. because the seeded prior keeps
    being the dominant guilt source and its weight is set by other
    levers): refutes the per-class-weight reading; some other mediator
    (timing of recall, position of agent at recall) is the operative
    variable. Pushes recall_event_trace up the queue.

Plausible findings worth naming up front:
  - CONFIRM: W_guilt drops monotonically with β_guilt by 1–2 orders of
    magnitude; ratio W_guilt/W_loyalty inverts cleanly.
  - SPLIT-PARTIAL: W_guilt drops as expected, but the magnitude is too
    small to plausibly drive the observed divergence-erosion (i.e.
    W_loyalty also drops because most of |e| is shared dims like loyalty
    on failure memories).
  - REFUTE: W_guilt is flat. Per-class weight is NOT the operative
    variable. Something else (e.g. recall timing, context similarity at
    deliberation steps) carries the swing.
  - REGIME ARTIFACT: W_loyalty itself collapses in the β_guilt=0.50 cell
    because few rescue memories get encoded (ep0 collapse means fewer
    early rescues to encode). This would confirm the
    decay_asymmetry_reversed regime-break reading.
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "memory_population_audit_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_RESULTS = os.path.join(OUT_DIR, "results.csv")
OUT_SNAPSHOT = os.path.join(OUT_DIR, "memory_snapshot.csv")

T_SNAP = 12
KAPPA = 1.0
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
    seed = 63000
    for beta_g in BETA_GUILTS:
        decay = _decay_dict(beta_g, BETA_LOYALTY)
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            # Tag the seeded prior so we can distinguish it later.
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
