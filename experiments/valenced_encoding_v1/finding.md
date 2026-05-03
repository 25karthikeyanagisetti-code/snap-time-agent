# Valenced Encoding — finding

**Date:** 2026-05-02
**Experiment:** `src/exp_valenced_encoding.py`
**Episodes run:** 2,000 (2 conditions × 100 agents × 10 chained episodes)

## Hypothesis

> Encoding loyalty memories on RESCUE (not just guilt on failure) restores
> behavioral types. The population should DIVERGE — agents who happen to
> rescue early should encode a positive memory and remain rescue-prone, while
> agents who fail should encode guilt and stay paralyzed.

Operationally: turn `positive_encoding` OFF (only encode guilt-on-failure) vs
ON (encode loyalty-on-rescue AND guilt-on-failure — the Wave-3 default), at
κ=1.0 in the committed regime, chained 10 episodes.

## Result — hypothesis FAILED in the opposite direction

The loyalty-on-rescue channel doesn't restore behavioral types — it
**accelerates the Homogenization Collapse**. Turning it OFF preserves the
committed-rescuer regime measurably better.

### Headline numbers

| metric                                          |  OFF  |  ON   |
|-------------------------------------------------|------:|------:|
| ep0 rescue rate (clean prior, no carry yet)     | 80.0% | 83.0% |
| ep1 rescue rate (after first carry)             | 65.0% | 28.0% |
| ep9 rescue rate (after 10 chained episodes)     | **28.0%** | **15.0%** |
| divergence @ ep5–9, conditional on ep1 outcome  | −2.2 pts | **−10.0 pts** |

Two things are striking:

1. **Turning OFF positive encoding nearly doubles ep9 rescue rate** (28% vs
   15%). The system is healthier without the loyalty-on-rescue channel.

2. **The divergence is NEGATIVE under both conditions** — agents who rescued
   in episode 1 are *less* likely to rescue in episodes 5–9 than agents who
   failed in episode 1. There are no behavioral types here. There is, if
   anything, an anti-type: a successful rescue early in the chain seems to
   reduce later rescue rate, especially with positive encoding ON.

I'm calling this **The Loyalty Boomerang**: encoding a loyalty-charged memory
after a successful rescue contributes more to the collapse than to behavioral
differentiation. The positive-valence "good outcome" channel that was meant to
balance the negative-valence "regret" channel turns out to make the system
worse.

## Mechanism (interpretation)

The seeded abandonment prior already injects ~0.6 loyalty + ~0.9 guilt into
the agent at episode 0. With κ=1.0, those are loud enough to reliably commit
to the partner. When the agent then SUCCEEDS, positive_encoding=ON adds
*another* loyalty-charged memory to the store. By episode 5 the agent's
memory population is dominated by accumulated partner-oriented memories —
which raise the conflict cost of every action that isn't perfectly aligned
with the partner. At softmax temperature 0.15, this slightly randomizes
action selection, increasing miss rate. Each miss adds a guilt-charged memory,
deepening the bias.

In the OFF condition, only failures encode. The memory store grows MORE
SLOWLY, so the seeded prior continues to dominate longer, and the agent stays
in its committed regime. Asymmetric (negative-only) memory encoding turns out
to be a stabilizer.

## What this implies for the broader question

The Wave-3 finding (Homogenization Collapse) and the 2026-05-01
selective_encoding null already argued that the framework cannot produce
behavioral types via outcome encoding. This experiment goes further: the
*direction* of encoding asymmetry matters, and the framework's default
(both-sided encoding) is the *worst* of the three configurations tested so
far. The natural follow-ups:

1. **Asymmetric severity gates** — use different importance for rescue-side
   vs failure-side encoding. Maybe loyalty needs to be encoded with much
   lower importance to avoid memory-population takeover.
2. **Bounded memory store** — cap the store size with LRU/least-impact
   eviction. The mechanism above depends on unbounded accumulation.
3. **Decay asymmetry** — apply faster decay to loyalty memories than guilt
   memories. Forgiveness for self, not for others.

These have been added to the backlog.

## Files

- `src/exp_valenced_encoding.py` — experiment driver
- `src/sandbox.py` — added `positive_encoding=True` parameter to
  `run_episode()` (default preserves all prior experiment behavior)
- `experiments/valenced_encoding_v1/results.csv` — 2,000 rows
- `experiments/valenced_encoding_v1/valenced_encoding.png` — 2-panel chart
