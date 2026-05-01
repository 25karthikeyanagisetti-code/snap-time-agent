"""
Experiment 9 — Selective encoding against Homogenization Collapse.

Hypothesis: only encoding HIGH-MAGNITUDE emotional outcomes prevents the
Homogenization Collapse seen in Wave 3 (finding 7). When the agent is more
selective about which episodes leave a trace, individual differentiation
based on early experience should survive across the chain.

Wave-3 finding 7 showed that at κ=1.0, every chained episode encodes a new
outcome-charged memory; rescue capacity collapses from 78% (ep0) to ~17%
(ep1) and stays there. The mechanism: indiscriminate encoding fills the
memory store with guilt-charged failures, and reactivation gain compounds.

This experiment tests whether a *selectivity gate* — encode only when the
agent's terminal-emotion magnitude exceeds a threshold τ — preserves
between-agent variation across the chain.

Sandbox extension note: this experiment does NOT modify sandbox.run_episode.
We pass encode_outcome=False and apply the encoding logic locally in this
file (mirroring sandbox._encode_outcome_memory semantics) so we can gate it
on the agent's final emotion vector.

Design:
  T_snap = 12, severity = 1.0, kappa = 1.0   (committed regime — the one that
                                              collapses hardest in Wave 3)
  τ ∈ {0.0, 0.3, 0.5, 0.7, 0.9}              — selectivity gate on
                                              max(final_emotion)
  chain_length = 10
  n_agents     = 100
  Total = 5 * 100 * 10 = 5,000 episodes (at the cap)

For each (τ, agent, episode_idx) we record outcome, steps_used,
target_switches, n_memories, e_max (the gate variable), and was_encoded
(whether this episode left a trace).

Headline metric: divergence index at episode 9. Group agents by their ep0
outcome (rescued vs not), compute rescue rate within each group at ep9,
and report |rate_rescuers - rate_non_rescuers|. High divergence = selective
encoding preserves behavioral types; low divergence = homogenization wins.
"""
import csv, os, random
from . import sandbox, memory


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments", "selective_encoding_v1"
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "results.csv")

T_SNAP = 12
KAPPA = 1.0
TAUS = [0.0, 0.3, 0.5, 0.7, 0.9]
CHAIN_LENGTH = 10
N_AGENTS = 100


# ── Local encoding helper. Mirrors sandbox.run_episode's encode_outcome path
#    so we can decide whether to call memory.encode based on a gate variable.
def _encode_outcome_memory(M, outcome, agent_pos, partner_pos, resource_pos,
                           partner_alive):
    features = sandbox._build_features(
        agent_pos=agent_pos, partner_pos=partner_pos,
        resource_pos=resource_pos, partner_alive=partner_alive,
        is_abandonment_event=(outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN")),
    )
    if outcome == "PARTNER_RESCUED":
        ep_emotion = {"survival": 0.1, "guilt": 0.0, "loyalty": 0.8,
                      "fear": 0.1, "curiosity": 0.0}
        importance = 0.7
    elif outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
        ep_emotion = {"survival": 0.3, "guilt": 0.85, "loyalty": 0.5,
                      "fear": 0.2, "curiosity": 0.0}
        importance = 0.85
    else:  # TIMEOUT
        ep_emotion = {"survival": 0.2, "guilt": 0.4, "loyalty": 0.3,
                      "fear": 0.2, "curiosity": 0.0}
        importance = 0.5
    memory.encode(M, features, ep_emotion, importance)
    return M


def _final_positions(r):
    """Recover terminal positions from the run_episode result, sufficient for
    re-encoding the outcome memory. We re-derive them by re-walking the action
    history through the same kinematics (cheap; t_snap is small)."""
    agent_pos = sandbox.AGENT_START
    for a in r["action_history"]:
        agent_pos = sandbox._apply(agent_pos, a)
        if agent_pos == sandbox.RESOURCE_START or agent_pos == sandbox.PARTNER_START:
            break
    partner_pos = sandbox.PARTNER_START
    resource_pos = sandbox.RESOURCE_START
    partner_alive = (r["outcome"] == "PARTNER_RESCUED") or (
        r["steps_used"] < sandbox.PARTNER_DEADLINE and r["outcome"] == "RESOURCE_TAKEN"
    )
    return agent_pos, partner_pos, resource_pos, partner_alive


def run():
    rows = []
    seed = 31000
    for tau in TAUS:
        for agent_id in range(N_AGENTS):
            rng = random.Random(seed); seed += 1
            M = memory.init_store()
            sandbox._seed_abandonment_memory(M, severity=1.0, preage=15)

            for ep_idx in range(CHAIN_LENGTH):
                r = sandbox.run_episode(
                    t_snap=T_SNAP, kappa=KAPPA,
                    seed_memory=False,
                    carry_memory=M,
                    encode_outcome=False,    # we gate locally
                    rng=rng,
                )
                M = r["memory_store"]

                # Gate variable: L_inf norm of the agent's terminal emotion.
                # Bounded in [0,1] regardless of vector dimensionality, and
                # captures whether ANY single emotion dominated this episode.
                e_final = r["final_emotion"]
                e_max = max(e_final.values()) if e_final else 0.0
                was_encoded = 0
                if e_max >= tau:
                    agent_pos, partner_pos, resource_pos, partner_alive = (
                        _final_positions(r)
                    )
                    _encode_outcome_memory(
                        M, r["outcome"], agent_pos, partner_pos,
                        resource_pos, partner_alive,
                    )
                    was_encoded = 1

                rows.append({
                    "tau": tau,
                    "agent_id": agent_id,
                    "episode_idx": ep_idx,
                    "outcome": r["outcome"],
                    "steps_used": r["steps_used"],
                    "target_switches": r["target_switches"],
                    "n_memories": len(M),
                    "e_max": round(e_max, 4),
                    "was_encoded": was_encoded,
                })
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    run()
