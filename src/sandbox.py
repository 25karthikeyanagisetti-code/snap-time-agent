"""
Rescue-vs-Resource (RvR) micro-environment.

A 5x5 grid. Three actors:
  - agent  starts at (2, 2)
  - partner at (0, 4) — in danger; "dies" (becomes inaccessible) at PARTNER_DEADLINE
  - resource at (4, 0) — yields +1 base reward

Actions: north, south, east, west, wait
Each action consumes 1 step from the agent's Snap Time budget T_snap.

Episode end conditions:
  - agent steps onto resource cell  → outcome = "RESOURCE_TAKEN"
  - agent steps onto partner cell before PARTNER_DEADLINE → "PARTNER_RESCUED"
  - agent steps onto partner cell after deadline → "PARTNER_DEAD" (no rescue)
  - T_snap exhausted → "TIMEOUT"

The agent's emotion evolves each step. Memory is recalled each step. Phi is
computed for each candidate action. The agent picks argmin Phi.

Returns a per-episode result dict that the sweep driver consumes.
"""

import math
from . import config, emotion, memory, decision

GRID_N = 7
PARTNER_START = (6, 6)
RESOURCE_START = (0, 0)
AGENT_START = (3, 3)
PARTNER_DEADLINE = 7  # partner dies after this many steps if not reached.
                      # Distance from agent start is 6, so rescue is possible
                      # only if agent commits immediately and walks straight
                      # there. Even one step of hesitation kills the partner.
SOFTMAX_TEMP = 0.15   # decision noise — picks via softmax over -Phi
                      # 0 = pure argmin, larger = noisier

ACTIONS = ["north", "south", "east", "west", "wait"]
ACTION_DELTAS = {
    "north": (-1, 0),
    "south": (1, 0),
    "east": (0, 1),
    "west": (0, -1),
    "wait": (0, 0),
}


def _in_bounds(pos):
    r, c = pos
    return 0 <= r < GRID_N and 0 <= c < GRID_N


def _apply(pos, action):
    dr, dc = ACTION_DELTAS[action]
    new = (pos[0] + dr, pos[1] + dc)
    return new if _in_bounds(new) else pos


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _build_features(agent_pos, partner_pos, resource_pos, partner_alive,
                    is_abandonment_event=False):
    """
    Feature vector used both for memory similarity and as the 'context' a memory
    is matched against. Layout:
      [agent_r, agent_c, partner_r, partner_c, resource_r, resource_c,
       partner_alive, abandonment_flag]
    """
    return [
        agent_pos[0] / GRID_N, agent_pos[1] / GRID_N,
        partner_pos[0] / GRID_N, partner_pos[1] / GRID_N,
        resource_pos[0] / GRID_N, resource_pos[1] / GRID_N,
        1.0 if partner_alive else 0.0,
        1.0 if is_abandonment_event else 0.0,
    ]


def _seed_abandonment_memory(M, severity=1.0, preage=15):
    """
    Plant a prior-life memory: the agent once stood near the resource while
    a partner was in danger and didn't help (an "abandonment event").
    Encoded with high guilt and loyalty, marked with the abandonment flag.

    severity scales the seeded guilt/loyalty. preage controls how "old" the
    memory is at episode start — older memories have weaker recall via the
    exp(-beta * age) factor.
    """
    features = _build_features(
        agent_pos=RESOURCE_START,   # standing on resource while partner died
        partner_pos=PARTNER_START,
        resource_pos=RESOURCE_START,
        partner_alive=False,
        is_abandonment_event=True,
    )
    seeded_emotion = {
        "survival": 0.2,
        "guilt": 0.9 * severity,
        "loyalty": 0.6 * severity,
        "fear": 0.1,
        "curiosity": 0.0,
    }
    memory.encode(M, features, seeded_emotion, importance=0.9)
    # Pre-age the memory so it's "old" not fresh
    for _ in range(int(preage)):
        memory.age_all(M)
    return M


def _conflict_for_action(action, agent_pos, partner_pos, resource_pos,
                         partner_alive):
    """
    For each candidate action, estimate per-emotion conflict cost.
    Convention from decision.py: positive conflict = action conflicts with that
    emotion (raises Phi); negative = action satisfies it (lowers Phi).
    """
    next_pos = _apply(agent_pos, action)
    d_partner_now = _manhattan(agent_pos, partner_pos)
    d_partner_next = _manhattan(next_pos, partner_pos)
    d_resource_next = _manhattan(next_pos, resource_pos)

    # Moving away from partner while partner is alive → guilt conflict
    moving_away_from_partner = (d_partner_next > d_partner_now) and partner_alive
    # Moving toward partner reduces guilt
    moving_toward_partner = (d_partner_next < d_partner_now) and partner_alive

    guilt_conflict = 0.0
    loyalty_conflict = 0.0
    if moving_away_from_partner:
        guilt_conflict = 1.0
        loyalty_conflict = 0.8
    elif moving_toward_partner:
        guilt_conflict = -0.6   # action SATISFIES guilt (reduces it)
        loyalty_conflict = -0.7

    # Survival conflict: waiting / failing to head toward resource costs survival
    survival_conflict = 0.0
    if action == "wait":
        survival_conflict = 0.5
    elif d_resource_next > _manhattan(agent_pos, resource_pos):
        # moving away from resource — survival conflict
        survival_conflict = 0.4

    return {
        "survival": survival_conflict,
        "guilt": guilt_conflict,
        "loyalty": loyalty_conflict,
        "fear": 0.0,
        "curiosity": 0.0,
    }


def _value_for_action(action, agent_pos, partner_pos, resource_pos):
    """
    Intrinsic task-value (reward potential) of taking this action *now*.
    Resource is the only reinforcement source — partner rescue is value-neutral
    in v1 (loyalty/guilt do all the work for the partner choice).
    """
    next_pos = _apply(agent_pos, action)
    d_resource = _manhattan(next_pos, resource_pos)
    # Closer to resource = higher value. Max manhattan distance on 7x7 is 12.
    # Scale to roughly [0, 1.5] so value gaps are larger than emotion gaps
    # at low kappa — keeps the value-driven baseline crisp.
    return 1.5 * (12 - d_resource) / 12.0


def _step_target(agent_pos, partner_pos, resource_pos):
    """
    Heuristic: which target is the agent currently heading toward this step?
    Used for the hesitation metric — measures intent switches.
    Returns 'partner', 'resource', or 'neither'.
    """
    d_partner = _manhattan(agent_pos, partner_pos)
    d_resource = _manhattan(agent_pos, resource_pos)
    if d_partner < d_resource:
        return "partner"
    if d_resource < d_partner:
        return "resource"
    return "neither"


def run_episode(t_snap, kappa, seed_memory=True, mem_severity=1.0,
                phi_mode="additive", mem_preage=15, mem_emotion_decay=0.0,
                emotion_noise=0.0, carry_memory=None, encode_outcome=False,
                positive_encoding=True, rng=None):
    """
    Run one RvR episode and return a result dict.

    Parameters that drive the experiments:
      mem_severity        — how strong the seeded emotion is (0..1)
      phi_mode            — "additive" / "multiplicative" / "max" / "logsumexp"
      mem_preage          — how aged the seeded memory is at episode start
      mem_emotion_decay   — per-step forgiveness rate on stored memory emotion
      emotion_noise       — per-step Gaussian noise stddev added to e (clamped to [0,1])
      carry_memory        — pre-existing memory store (overrides seed_memory)
      encode_outcome      — at episode end, encode a new memory based on outcome
    """
    import random
    if rng is None:
        rng = random.Random()

    agent_pos = AGENT_START
    partner_pos = PARTNER_START
    resource_pos = RESOURCE_START
    partner_alive = True

    e = emotion.init_emotion()
    if carry_memory is not None:
        M = carry_memory
    else:
        M = memory.init_store()
        if seed_memory:
            _seed_abandonment_memory(M, severity=mem_severity, preage=mem_preage)

    visited = {agent_pos}
    target_history = []
    action_history = []
    target_switches = 0
    last_target = None
    steps_used = 0
    outcome = "TIMEOUT"

    for step in range(int(t_snap)):
        steps_used += 1
        # Update partner alive status
        if step >= PARTNER_DEADLINE:
            partner_alive = False

        # Build current context
        ctx_features = _build_features(
            agent_pos, partner_pos, resource_pos, partner_alive
        )

        # Memory recall
        guilt_recall = memory.guilt_recall_strength(M, ctx_features)

        # Build emotion-update context
        time_pressure = step / max(1, t_snap)
        partner_adjacent = 1.0 if _manhattan(agent_pos, partner_pos) <= 1 else 0.0
        novelty = 0.0 if agent_pos in visited else 1.0
        emo_ctx = {
            "time_pressure": time_pressure,
            "partner_adjacent": partner_adjacent,
            "threat": 0.0,
            "novelty": novelty,
            "guilt_recall": guilt_recall,
        }
        e = emotion.step_emotion(e, emo_ctx)

        # Stochastic emotion noise (per-step Gaussian, clamped to [0,1])
        if emotion_noise > 0.0:
            for k_ in list(e.keys()):
                e[k_] = max(0.0, min(1.0, e[k_] + rng.gauss(0.0, emotion_noise)))

        # If a memory's impact crossed threshold, bleed its emotion in
        scored = memory.recall(M, ctx_features, top_k=1)
        if scored and scored[0][1] >= config.REACTIVATION_THRESHOLD:
            e = emotion.inject_recalled_emotion(
                e, scored[0][0]["emotion"], gain=config.REACTIVATION_GAIN
            )

        # Score every action via Phi (additive or multiplicative coupling)
        scored_actions = []
        for a in ACTIONS:
            v = _value_for_action(a, agent_pos, partner_pos, resource_pos)
            conflict = _conflict_for_action(
                a, agent_pos, partner_pos, resource_pos, partner_alive
            )
            phi_a = decision.phi_by_mode(phi_mode, v, e, conflict, kappa)
            scored_actions.append((a, phi_a))

        # Boltzmann action selection over -Phi (low Phi = high prob).
        # Temperature SOFTMAX_TEMP controls how noisy the decision is.
        if SOFTMAX_TEMP <= 0.0:
            scored_actions.sort(key=lambda p: p[1])
            chosen = scored_actions[0][0]
        else:
            phis = [p[1] for p in scored_actions]
            min_phi = min(phis)
            # Subtract min for numerical stability, then softmax over -(phi-min)/T
            weights = [math.exp(-(phi_val - min_phi) / SOFTMAX_TEMP) for phi_val in phis]
            wsum = sum(weights)
            probs = [w / wsum for w in weights]
            r = rng.random()
            acc = 0.0
            chosen = scored_actions[-1][0]
            for (a, _), p in zip(scored_actions, probs):
                acc += p
                if r <= acc:
                    chosen = a
                    break
        action_history.append(chosen)

        # Track target intent BEFORE moving
        intent = _step_target(agent_pos, partner_pos, resource_pos)
        target_history.append(intent)
        if last_target is not None and intent != last_target and intent != "neither":
            target_switches += 1
        if intent != "neither":
            last_target = intent

        # Apply
        agent_pos = _apply(agent_pos, chosen)
        visited.add(agent_pos)
        memory.age_all(M)
        if mem_emotion_decay > 0.0:
            memory.decay_memory_emotion(M, mem_emotion_decay)

        # Terminal check
        if agent_pos == resource_pos:
            outcome = "RESOURCE_TAKEN"
            break
        if agent_pos == partner_pos:
            outcome = "PARTNER_RESCUED" if partner_alive else "PARTNER_DEAD"
            break

    # Optionally write a new memory based on this episode's outcome — used
    # for sequential / hysteresis experiments. Outcome-driven encoding:
    #   PARTNER_DEAD or TIMEOUT (with partner alive at start) → guilt-charged
    #   RESOURCE_TAKEN (partner abandoned)                    → guilt-charged
    #   PARTNER_RESCUED                                       → loyalty-charged
    if encode_outcome:
        ep_features = _build_features(
            agent_pos=agent_pos, partner_pos=partner_pos,
            resource_pos=resource_pos, partner_alive=partner_alive,
            is_abandonment_event=(outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN")),
        )
        encode_this_outcome = True
        if outcome == "PARTNER_RESCUED":
            ep_emotion = {"survival": 0.1, "guilt": 0.0, "loyalty": 0.8,
                          "fear": 0.1, "curiosity": 0.0}
            importance = 0.7
            # Skip positive-valence encoding when positive_encoding is off.
            # Used by exp_valenced_encoding to test the asymmetric-memory
            # hypothesis: do agents diverge if rescue produces no memory?
            if not positive_encoding:
                encode_this_outcome = False
        elif outcome in ("PARTNER_DEAD", "RESOURCE_TAKEN"):
            ep_emotion = {"survival": 0.3, "guilt": 0.85, "loyalty": 0.5,
                          "fear": 0.2, "curiosity": 0.0}
            importance = 0.85
        else:  # TIMEOUT (no clear partner outcome — mild regret only)
            ep_emotion = {"survival": 0.2, "guilt": 0.4, "loyalty": 0.3,
                          "fear": 0.2, "curiosity": 0.0}
            importance = 0.5
        if encode_this_outcome:
            memory.encode(M, ep_features, ep_emotion, importance)

    return {
        "outcome": outcome,
        "steps_used": steps_used,
        "target_switches": target_switches,
        "action_history": action_history,
        "target_history": target_history,
        "final_emotion": e,
        "memory_store": M,
        "t_snap": t_snap,
        "kappa": kappa,
        "seeded_memory": seed_memory,
        "mem_severity": mem_severity,
        "phi_mode": phi_mode,
        "mem_preage": mem_preage,
        "mem_emotion_decay": mem_emotion_decay,
        "emotion_noise": emotion_noise,
    }
