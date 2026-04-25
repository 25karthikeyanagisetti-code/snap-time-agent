# Findings — Wave 3

40,200 new episodes across four sweeps. Three positive findings, one
informative negative result. The most surprising result is the one I least
expected to see — chained agents COLLAPSE in rescue capacity within a single
episode of memory accumulation.

---

## Finding 5 — No-free-lunch confirmed across four Φ couplings

**Sweep:** {additive, multiplicative, max, logsumexp(β=4)} × κ ∈ {0, 0.1,
0.25, 0.5, 1, 2, 4} at T_snap=12, severity=1.0, 200 episodes/cell.

```
        mode  | metric  | k=0   k=0.1  k=0.25  k=0.5  k=1.0  k=2.0  k=4.0
   additive   | fail    | 43    74    94      76     22      1      0
              | rescue  |  0     0     1      24     78     99    100
   multiplica | fail    | 48    22     6       4      1      0      0
              | rescue  |  0     0     0       0      0      0      0
   max        | fail    | 48    55    78      96     98    100     99
              | rescue  |  0     0     0       0      1      0      1
   logsumexp  | fail    | 44    60    70      86     98     94     60
              | rescue  |  0     0     0       0      2      6     40
```

Each coupling has a **distinct pathology**:

- **Additive**: paralysis valley + clean commitment at high κ (the original)
- **Multiplicative**: NO valley, but NEVER rescues (value-greedy at all κ)
- **Max** (winner-take-all): valley deepens MONOTONICALLY into permanent
  paralysis — never escapes, even at κ=4 (99% failure). Single-emotion
  domination is catastrophic.
- **Logsumexp** (soft-max, β=4): valley + partial rescue (40% at κ=4),
  worse at all middle-κ than additive

**No coupling tested gave both:** (a) no paralysis regime, AND (b) a regime
where the agent reliably rescues. The space of valley-vs-rescue trade-offs
has at least these four corners, and none of them is in the "good" quadrant.

This is a stronger statement than wave 2 could make. The valley is not an
artifact of one coupling form — it is a property of the broader class of
"emotion-modulated value scoring with a Snap Time horizon." Different forms
buy off the valley with different costs (no commitment, permanent paralysis,
slow rescue). None remove it for free.

**Caveat:** I have not tested learned Φ (e.g. a small NN). That remains the
free-est-lunch candidate. But the pattern across hand-crafted Φ is clear.

---

## Finding 6 — Stochastic resonance is local, not global (informative null)

**Sweep:** emotion_noise σ ∈ {0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4} × κ ∈
{0, 0.25, 0.5, 1, 2}, T_snap=12, severity=1.0.

I expected per-step Gaussian noise on the emotion vector to act like
stochastic resonance — kicking the agent out of the oscillation that drives
paralysis.

What actually happened:
- At κ=0.25 (deep valley bottom): essentially no effect across noise levels
  (94% → 90% failure). The agent was too deep in the valley for noise to
  perturb the leader-action.
- At κ=0.5 (valley shoulder): noise materially helped — rescue rate climbed
  from 21% to 36%, failure dropped from 79% to 63%.
- At κ=1.0+: noise mildly DEGRADED performance (committed regime).

**The valley has a depth that matters.** Noise is enough to flip the action
when Φ-differences are small (the shoulders), but not enough at the bottom
where the emotion-driven Φ surface has a deep, stable basin. This is a
useful negative result: you can't perturb your way out of strong paralysis.

---

## Finding 7 — Self-memory homogenizes the population (the headline)

**Sweep:** chains of 10 episodes per agent, 100 agents per κ ∈ {0.25, 0.5,
1.0}, memory carries across episodes, episodic outcome is encoded into the
memory store after each episode.

I designed this expecting **divergence**: agents that happen to rescue in
episode 1 should encode a strong loyalty memory and become more rescue-prone
in episode 5; agents that abandoned in episode 1 should become more
abandonment-prone. Like personality formation from early experience.

The data showed something quite different:

**Episode-1 outcome barely predicts episode 5–9 outcomes.** At κ=0.25,
agents that rescued in ep 1 fail 60% later vs 75% for agents that timed out
— a 15-point gap that washes out further down the chain.

**More striking: at κ=1.0 (the committed regime), rescue capacity COLLAPSES
within a single episode.**

```
Population at κ=1.0:           ep0  ep1  ep5  ep9
  RESCUED (PARTNER_RESCUED):   78%  17%  14%  17%
  FAILED  (TIMEOUT/PDEAD):     20%  82%  70%  79%
```

Episode 0 is fresh-memory: 78% of agents rescue the partner (the original
committed regime). Episode 1, after one outcome-encoded memory has been
appended, rescue collapses to 17% and stays there for the rest of the chain.

Same pattern, less dramatic, at κ=0.5: rescue 22% → 1-5%.

**The mechanism, looking at the encoder:** every episode that doesn't
end in PARTNER_RESCUED encodes a guilt-charged memory (importance 0.85). So
the memory store fills up with progressively more guilt-charged episodes,
reactivation gain compounds, the agent's emotion gets pulled toward the
seeded pattern more often, and it can no longer commit to either action
cleanly. Even initially-successful rescuers accumulate failure memories
fast and join the failure attractor.

There is no individual differentiation in this framework. All initial
conditions converge to the same stable behavioral state: chronic rescue
failure with intermittent resource grabs.

**Why this matters as a finding:** in human terms, this is the architecture
saying "you cannot become a person through experience here — experience
flattens you toward the average, regardless of what you do." That's a real
failure of the framework. Building toward human-like behavior REQUIRES
either (a) selective memory encoding, (b) emotional valence learning that
distinguishes good from bad outcomes, or (c) a memory-store population
mechanism (consolidation, decay-by-success) that doesn't exist yet.

It is also a warning for any agent system built on cumulative memory: if
your memory grows faster than your ability to weight it correctly, the agent
regresses to a behavioral attractor independent of what it actually
experienced.

---

## Finding 8 — The valley narrows and shifts right with deliberation time

**Sweep:** T_snap ∈ {8, 12, 20} × κ ∈ {0.000, 0.025, …, 1.000} (41 points),
high-resolution, 200 episodes/cell.

```
T_snap = 8:   peak fail = 100% at κ=0.20, width(>50%) = 0.700
T_snap = 12:  peak fail =  98% at κ=0.28, width(>50%) = 0.625
T_snap = 20:  peak fail =  63% at κ=0.35, width(>50%) = 0.200
```

Three structural facts emerge from the high-resolution scan:

1. The peak-failure κ shifts RIGHT as T_snap grows (0.20 → 0.28 → 0.35).
   More time means moderate-strength emotion can still be overcome, but
   slightly stronger emotion captures the agent for longer.
2. The peak HEIGHT drops with T_snap (100% → 98% → 63%). More time = more
   chances to commit, less likely to time out clean.
3. The WIDTH of the >50%-failure regime SHRINKS dramatically (0.7 → 0.625 →
   0.2). At T_snap=20 the valley is sharp and narrow; at T_snap=8 it is
   broad and almost everything fails.

The valley NEVER vanishes within the swept range. Even at T_snap=20, a 63%
peak persists — there is no amount of deliberation time tested that
eliminates paralysis. The valley shape is a function of the architecture,
not of compute budget.

---

## What is provisionally novel here

| # | Claim | Evidence |
|---|-------|----------|
| 5 | No-free-lunch across four Φ couplings: each form has a distinct pathology, none gives no-paralysis AND rescue | couplings_zoo.png |
| 6 | Stochastic resonance is local: noise rescues at the valley shoulder but not at the bottom | resonance_curve.png |
| 7 | Self-memory homogenizes the population — committed-regime rescue capacity collapses within ONE episode of outcome encoding | hysteresis_collapse.png |
| 8 | The valley narrows and shifts right with T_snap but never vanishes | phase_boundary.png |

Finding 7 is the strongest candidate for a post. It mirrors a real
psychological puzzle (why don't repeated good experiences accumulate into
robust character?), and the mechanism is observable inside the framework.

---

## Open questions for v4

- Does selective memory encoding (only encode "consequential" outcomes) prevent
  the homogenization? Test: encode_outcome only when |emotion change| > τ.
- Does the homogenization survive in a multi-agent setting where the partner
  is real (acts on its own)? The rescued vs not-rescued asymmetry might
  matter more if the partner can express gratitude or absence.
- Can a learned Φ break no-free-lunch? Train a small policy with reward =
  rescue_count - paralysis_count and see if the resulting Φ avoids both.
- Is there a memory-store SIZE at which performance degrades? Test sweep on
  pre-stocked memory of N=1, 5, 20, 100 random outcome memories.
