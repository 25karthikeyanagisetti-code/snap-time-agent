"""
Experiment 14 — Decay Asymmetry REVERSED ("forgive self too").

Hypothesis (top of research_backlog.md, set by 2026-05-05):
  Reverse the 2026-05-05 sweep — hold β_loyalty=0.05 fixed and sweep
  β_guilt ∈ {0.05, 0.15, 0.30, 0.50}. If the divergence-inversion observed
  in decay_asymmetry_v1 is mediated by a "loyalty cushion vs guilt
  counterweight" mechanism, this reversal should produce the OPPOSITE
  pattern: positive divergence GROWS as the guilt-side stored emotion is
  cleared faster.

Why this is the right next dial:
  - 2026-05-02 valenced_encoding showed +rescue encoding cuts ep5–9 mean
    rescue from 28% (OFF) to 15% (ON, importance=0.7). The Loyalty
    Boomerang.
  - 2026-05-04 loyalty_importance_floor null ruled out per-encoding
    importance as the lever (range 2.4 pts across rescue_importance).
  - 2026-05-05 decay_asymmetry showed the headline mean-rescue stat is
    structurally locked at ~19–21% across β_loyalty ∈ {0.05, …, 0.50}
    while divergence@5–9 *inverts sign monotonically* from +13.3 pts to
    −18.8 pts.
  - The interpretation in finding_v3 of that result was: "asymmetric
    forgiveness erases consequence-of-early-outcome by clearing the
    rescue-memory loyalty cushion while the failure-memory guilt
    counterweight persists, so ep1-rescuers no longer differ from
    ep1-failers in late-chain emotion gain."
  - That interpretation predicts a clean, signed contrast: faster guilt
    decay should CONFIRM type formation if the cushion-vs-counterweight
    framing is right (positive divergence grows monotonically), or NULL it
    out if both channels matter symmetrically and the inversion was just
    "any imbalance erases history" rather than directional.

This is the cleanest single falsifier of the 2026-05-05 interpretation.
A symmetric inversion (positive→negative again) under reversed asymmetry
would mean the mechanism is "imbalance breaks differentiation" rather
than "guilt persistence overrides loyalty cushion." Either result is
informative.

Sandbox extension:
  None. memory.decay_memory_emotion already accepts per-dim dict; the
  sandbox path was wired up in exp_decay_asymmetry. We only invert which
  of the two dims is held at the slow control rate.

Design (committed-regime cell where the boomerang lives):
  T_snap = 12, kappa = 1.0, severity = 1.0
  positive_encoding = True   (the regime that exhibits the boomerang)
  rescue_importance = 0.7    (default — match valenced/floor/decay baseline)
  chain_length = 10
  n_agents     = 100

  Cells (β_loyalty fixed at 0.05 throughout — the REVERSE of the prior sweep):
    A: β_guilt = 0.05   (symmetric mild decay — control; matches the
                         decay_asymmetry symmetric cell exactly. Should
                         reproduce ep5–9 ≈ 20.8% mean and divergence ≈
                         +13.3 pts within sampling noise.)
    B: β_guilt = 0.15   (asymmetric, guilt fades 3× faster)
    C: β_guilt = 0.30   (asymmetric, guilt fades 6× faster)
    D: β_guilt = 0.50   (extreme asymmetry, guilt cleared in ~2 steps)

  Total = 4 * 100 * 10 = 4,000 episodes (well under 5k cap).

Headline metric:
  divergence@5–9 across the four cells.

  - If divergence GROWS monotonically (e.g. +13 → +20 → +30 → +40 pts):
    cushion-vs-counterweight interpretation is supported. The 2026-05-05
    inversion was directional, and faster guilt decay STRENGTHENS
    experience-driven type formation.
  - If divergence INVERTS again (e.g. +13 → +5 → −10 → −20): the
    mechanism is "imbalance erases history" — symmetry, not direction —
    and the prior finding was misinterpreted in finding_v3.
  - If divergence stays flat near +13: guilt-side decay does NOT carry the
    weight; the inversion was driven exclusively by loyalty-side decay.
  - If mean rescue rate climbs (toward 28% OFF baseline): guilt-side decay
    is also a lever for the headline ep5–9 mean — a NEW positive result on
    the boomerang.

Secondary metrics:
  - ep0 rescue rate (sanity — should be near committed-regime ~70–80%)
  - mean memory store size at ep9 (should be 11 in every cell — store
    geometry is unchanged; only stored emotion is modulated)

Plausible failure modes worth naming up front:
  - INVERTED REPRO: divergence inverts in the same direction as the prior
    sweep — implies the inversion is symmetric in asymmetry-magnitude, not
    in sign of the asymmetry. The 2026-05-05 mechanism story is wrong.
  - NULL on divergence: stays near the +13 baseline. Implies guilt-decay
    is a much weaker lever than loyalty-decay; the prior 32-pt swing was
    one-sided.
  - HEADLINE LIFT: ep5–9 mean climbs above the locked ~20% band. Would be
    the first intervention to puncture the boomerang — would change the
    framing of findings_v3 substantially.
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "decay_asymmetry_reversed_v1",
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
SEVERITY = 1.0
RESCUE_IMP = 0.7
BETA_LOYALTY = 0.05
BETA_GUILTS = [0.05, 0.15, 0.30, 0.50]
CHAIN_LENGTH = 10
N_AGENTS = 100


def _decay_dict(beta_guilt, beta_loyalty):
    """
    Build the per-dim decay rate dict. Other emotion dims get rate=0 (no
    decay) so we isolate the guilt-vs-loyalty contrast — same convention as
    exp_decay_asymmetry.
    """
    return {
        "survival": 0.0,
        "guilt": beta_guilt,
        "loyalty": beta_loyalty,
        "fear": 0.0,
        "curiosity": 0.0,
    }


def run():
    rows = []
    seed = 62000
    for beta_g in BETA_GUILTS:
        decay = _decay_dict(beta_g, BETA_LOYALTY)
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=SEVERITY, preage=15)
            for ep_idx in range(CHAIN_LENGTH):
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
                rows.append({
                    "beta_guilt": beta_g,
                    "beta_loyalty": BETA_LOYALTY,
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": r["outcome"],
                    "rescued": 1 if r["outcome"] == "PARTNER_RESCUED" else 0,
                    "n_memories": len(M),
                    "target_switches": r["target_switches"],
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
