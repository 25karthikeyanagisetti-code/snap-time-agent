# Findings — Wave 2 (post regime_map_v1)

After the Paralysis Valley result, the natural next questions were:
1. Does the valley exist for ALL emotional intensities, or only above some
   threshold?
2. Is it a property of the additive coupling Φ = -v + κ⟨e,c⟩, or is it
   architectural — present in any reasonable Φ?
3. Can the agent escape it through forgetting? And is "active forgiveness
   during deliberation" the same as "the wound was already old"?

Three sweeps ran. All three produced findings I did not predict in advance.

---

## Finding 1 — The valley has a memory-severity threshold (~0.4)

**Sweep:** mem_severity ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} × κ ∈ {0, 0.1, 0.25, 0.5, 1, 2, 4}, T_snap=12, 200 episodes/cell.

```
sev/k     0.0   0.1  0.25   0.5   1.0   2.0   4.0
0.0       48    44    40    44    38    36    27
0.2       44    41    49    38    43    40    50
0.4       46    52    52    59    66    88    50   ← weird
0.6       41    57    79    94    60    12     0
0.8       46    70    93    90    40     4     0
1.0       46    70    98    74    23     2     0
```

Three regimes by severity:
- **severity ≤ 0.2**: no valley. Failure roughly flat in κ (~40% baseline).
  Memory exists but is too weak to perturb decisions.
- **severity ≥ 0.6**: full valley. Sharp peak at κ ≈ 0.25–0.5, drops to near-zero
  failure at κ ≥ 2 (committed rescuer).
- **severity = 0.4**: a *different* failure mode appears. Failure peak shifts
  to κ = 2.0 (88%) where the agent gets PARTNER_DEAD/TIMEOUT outcomes and almost
  never rescues. At κ = 4.0 it cleanly rescues 50% of the time.

**Why the severity = 0.4 row is interesting:** at moderate severity + strong κ,
the emotion is JUST strong enough to pull the agent off the resource path but
not strong enough to commit firmly to the rescue. The agent commits to the
partner direction *late*, missing the deadline. This is not the same valley —
it's a "late-commitment" failure mode that only exists in a narrow band of
(severity, κ) space.

**Pre-registered hypothesis was wrong.** I expected severity to scale the
valley smoothly. Instead it has a sharp threshold below which the valley does
not exist, and a transitional band that exhibits a different failure pattern.

---

## Finding 2 — The valley is killed by multiplicative coupling, but at a cost

**Sweep:** Φ_additive vs Φ_multiplicative across the same κ axis.

```
       k=0.0  k=0.1  k=0.25  k=0.5  k=1.0  k=2.0  k=4.0
add      42    73     97      73     28      1      0
mul      47    14     10       3      1      0      0
```

Multiplicative Φ = -v · (1 + κ⟨e,c⟩) is monotonic in κ. Failure rate drops
smoothly from 47% (κ=0) to 0% (κ=4). No valley.

**But:** at every κ, multiplicative chooses RESOURCE_TAKEN almost exclusively.
Partner rescue rate under multiplicative is essentially 0% across the entire κ
range. Compare additive at κ=4: 100% rescue; multiplicative at κ=4: 0% rescue.

The mathematical reason: when v is large (resource action) and κ⟨e,c⟩ > 0
(action conflicts with emotion), the term (1 + κ⟨e,c⟩) gets *larger*, making
-v·(1+...) MORE negative. The agent picks it more strongly. Multiplicative
coupling makes emotion AMPLIFY the value signal in the wrong direction for
this dilemma. It removes paralysis by removing the capacity for sacrifice.

**This is a stronger architectural claim than I expected to be able to make:**
the valley is not an artifact of additive coupling — it is the price the
additive form pays for having the capacity to override value with emotion in
the first place. There may be no Φ that gives both:
  (a) emotion can flip the action away from value, AND
  (b) no paralysis regime in between.

This is testable — try other couplings (max, soft-min, log-sum-exp).

---

## Finding 3 — Aging escapes paralysis. Active forgiveness barely does anything.

**Sweep:** preage ∈ {0, 15, 50, 100, 200} × decay ∈ {0, 0.02, 0.05, 0.10, 0.20}
× κ ∈ {0.25, 0.5, 1.0}, T_snap=12.

The headline cell is κ=0.25, where the original valley failure was 98%:

```
 preage  d=0    d=0.02  d=0.05  d=0.1  d=0.2
   0     96     96      95      96     90
  15     98     94      94      92     87
  50     40     44      36      40     44   ← cliff between 15 and 50
 100     37     42      44      46     40
 200     37     42      38      39     48
```

Two clean facts:

1. **Pre-aging the memory dramatically rescues the agent from paralysis.**
   At κ=0.25, going from preage=15 to preage=50 drops failure from 98% to
   ~40%. That is the rational baseline. The valley is gone.

2. **Per-step emotion decay (active forgiveness during the episode) has only a
   marginal effect.** Across each row, the variation between decay=0 and
   decay=0.20 is small (single digits). The agent cannot forgive its way out
   of paralysis fast enough — the deliberation horizon is too short. Aging is
   effectively a property of the prior; in-episode decay is too late.

But there is a second, less obvious finding here that matters for the
architecture:

3. **Aging flattens, it does not balance.** At κ=1.0 (the original
   "committed" regime) failure with fresh memory is 22%. At preage≥50 it
   ROSE to ~38%. So aging the memory doesn't just escape paralysis — it ALSO
   strips the committed-rescuer regime, returning the agent to neutral
   rationality. There is no preage that gives "thoughtful, sometimes commits"
   behavior. You either remember strongly enough to commit/paralyze, or you
   forget enough to be rational about everything.

This is the framework's first clear statement about *forgiveness as a tradeoff*:
forgetting the wound costs you the lesson the wound taught.

---

## What is provisionally novel here

These are claims I'd be willing to defend as not-yet-published-for-this-style-
of-architecture, not as "first ever discovered in psychology" (Yerkes-Dodson
analogs exist):

| # | Claim                                                                                                  | Evidence              |
|---|--------------------------------------------------------------------------------------------------------|-----------------------|
| 1 | The Paralysis Valley has a memory-intensity threshold below which it does not exist                    | severity_threshold.png |
| 2 | The valley is removable algebraically but only by surrendering the agent's capacity for emotional override | phi_mode_comparison.png |
| 3 | Memory aging escapes paralysis by collapsing the entire emotion-weight axis to neutral rationality (no balance regime exists) | aging_collapse.png |
| 4 | Per-step active forgiveness during deliberation does not measurably help — the horizon is too short    | forgiveness_heatmap.png |

Finding 3 is the one I think is most worth a post. It mirrors a real human
pattern (you can lose the wisdom along with the wound) and emerges purely from
the recall dynamics — nothing in the framework says "old memories shouldn't
make you commit anymore."

---

## Open questions for v3

- Is finding 2 universal? Does it hold for max-coupling, log-sum-exp, or a
  learned Φ? The free-lunch claim is strong and needs more couplings tested.
- Why exactly does severity = 0.4 produce the late-commitment failure? Need a
  per-episode trace analysis, not just outcome counts.
- Does multi-agent loyalty (real partner agent that acts) change the
  thresholds? Seeded loyalty is a stand-in.
- Does adding a small amount of intrinsic curiosity reward break the
  rational-vs-paralyzed dichotomy when memory is aged?
