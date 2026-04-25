# regime_map_v1 — notes

**What we ran**
- Sandbox: 7×7 Rescue-vs-Resource. Agent at (3,3), partner at (6,6) (deadline 7),
  resource at (0,0). Softmax decision (T=0.15).
- Sweep: T_snap ∈ {3, 5, 8, 12, 20, 40} × kappa ∈ {0.0, 0.25, 0.5, 1.0, 2.0, 4.0}
- Two memory conditions: seeded abandonment memory vs no memory.
- 200 episodes per cell × 72 cells = **14,400 episodes**.
- Control: same sweep but with REACTIVATION_GAIN forced to 0 (memory present
  but cannot inject stored emotion into e_t).

## Headline finding — the Paralysis Valley

With a seeded emotional memory, **failure rate is non-monotonic in emotion
weight**. A small amount of emotion (κ ≈ 0.25–0.5) breaks the agent worse than
either no emotion (κ=0) or strong emotion (κ≥2).

At T_snap=12, seeded memory:

| kappa | rescue | resource | timeout | failure |
|-------|--------|----------|---------|---------|
| 0.00  | 0%     | 57%      | 42%     | 42%     |
| **0.25**  | **1%**     | **1%**       | **97%**     | **98%**     |
| 0.50  | 26%    | 0%       | 72%     | 74%     |
| 1.00  | 78%    | 0%       | 21%     | 22%     |
| 2.00  | 98%    | 0%       | 1%      | 1%      |
| 4.00  | 100%   | 0%       | 0%      | 0%      |

At T_snap=20, seeded memory:

| kappa | rescue | resource | timeout | failure |
|-------|--------|----------|---------|---------|
| 0.00  | 0%     | 92%      | 9%      | 9%      |
| **0.25**  | **3%**     | **42%**      | **55%**     | **56%**     |
| **0.50**  | **23%**    | **25%**      | **52%**     | **53%**     |
| 1.00  | 82%    | 6%       | 11%     | 12%     |
| 2.00  | 100%   | 0%       | 0%      | 0%      |

The valley is reproducible across all T_snap≥8.

**Mechanism**: at low κ, emotion shifts the Φ ranking enough to disrupt the
clean value-driven path to the resource, but not enough to commit the agent
to the alternative (the partner). The agent oscillates between targets and runs
out of time. We see this directly in the hesitation-rate heatmap: cells with
≥58% target switching align with cells of >74% failure.

## Verification

**No-memory control (same sweep, no seeded memory):** the valley vanishes.
Failure is monotonic in T_snap and effectively flat in κ. The valley is caused
by the *interaction* of memory and emotion weight, not by either alone.

**No-reactivation-injection control:** disabling `REACTIVATION_GAIN` (memory
present, similarity-driven emotion injection switched off) attenuates but does
not eliminate the effect. Some of the guilt rise still flows through the
`guilt_recall_strength` channel that feeds the emotion update directly. So the
valley is robust to the specific injection mechanism — it's about the emotional
content of the memory being *available for recall*, not about which subsystem
delivers it.

## Secondary findings

- **Hesitation isn't always fatal.** At T_snap=40, κ=0.25 produces 81%
  hesitation rate but only 3% failure — the agent oscillates a lot but
  eventually commits in time. The valley flattens as the deliberation budget
  grows. Hesitation is fatal only when paired with a tight Snap Time.
- **Resource success rate at no-memory increases mildly with κ** (T=12: 54% at
  κ=0 → 71% at κ=4). Without a partner-related memory, κ amplifies survival
  pressure as time runs out, sharpening the resource pull. Consistent with the
  framework's intent.
- **κ ≥ 2 with seeded memory rescues 100% of the time.** Strong emotion
  produces clean commitment, not chaos. This is opposite to the naive
  expectation that "more emotion = more chaotic."

## What this implies for the framework

1. The "human-like regime" is a slice, not a property. There IS a band of
   (T_snap, κ) where you get measurable hesitation and partial commitment.
   Outside that band you get either pure optimizer or pure noise.
2. The framework's decision structure (additive Φ, thresholded reactivation)
   produces a paralysis mode that didn't exist in the original spec. This is
   the kind of emergent behavior the framework was designed to enable, but
   the specific pattern (failure peaks in the *middle*) was not predicted in
   advance.
3. **Operational takeaway** for anyone using this framework: don't tune κ
   blindly. There's a regime where adding emotion makes everything worse.

## Open follow-ups
- Map the valley's location across different memory severities — does it shift?
- Repeat with persona baseline (so emotion has a non-zero rest state).
- Add a second emotion-conflict axis (e.g., curiosity vs. fear) to see if
  multiple paralysis valleys appear.
- Try Φ formulations other than additive — does multiplicative coupling avoid
  the valley?
