# Research backlog

The daily scheduled task pops the top item off this list, implements it, runs it, and commits the result. If this list is empty, the daily task generates a fresh hypothesis from the most recent findings.

## Format

Each item is a single bullet with: `<short_name>` — one-sentence hypothesis — what to vary — what to measure.

---

## Queued

- `valenced_encoding` — Encoding loyalty memories on RESCUE (not just guilt on failure) restores behavioral types. Vary: positive_encoding ∈ {off, on}. Measure: rescue rate vs initial-rescue-outcome correlation over chained episodes.
- `signed_threshold_encoding` — Asymmetric gates (different τ for guilt-charged vs loyalty-charged outcomes) sort the population. Vary: τ_guilt ∈ {0.3, 0.7}, τ_loyalty ∈ {0.3, 0.7}. Measure: divergence@ep9 at κ=1.0. (Follow-up to selective_encoding null.)
- `prior_dilution_rate` — At high encoding-gate τ, the seeded abandonment prior dominates indefinitely. Vary: prior preage ∈ {0, 5, 15, 30, 60}. Measure: rescue@ep9 at τ=0.7. (Follow-up to selective_encoding null.)
- `memory_consolidation` — Periodic pruning of low-impact memories preserves the committed-rescuer regime. Vary: prune_interval ∈ {1, 3, 5, 10}, prune_threshold ∈ {0.05, 0.15, 0.3}. Measure: rescue rate at episode 9 vs episode 0 across κ.
- `dynamic_kappa` — Annealing κ from high to low across episodes prevents paralysis early then allows rationality late. Vary: schedule ∈ {constant, linear_decay, step_decay}. Measure: failure rate trajectory across 10 episodes.
- `multi_memory` — Two seeded memories (loyalty AND guilt) cancel out — agent reverts to value-greedy. Vary: number of seeded memories ∈ {0, 1, 2, 3}. Measure: failure rate at κ=0.25.
- `memory_capacity` — A bounded memory store (LRU eviction) breaks the Homogenization Collapse. Vary: capacity ∈ {3, 5, 10, ∞}. Measure: rescue rate variance across initial conditions.
- `partner_deadline_sweep` — The Paralysis Valley shifts with the partner deadline. Vary: deadline ∈ {3, 5, 7, 10, 15}. Measure: κ_min of the failure peak.
- `noise_typology` — Different noise types (Gaussian on emotion vs uniform on Φ vs softmax temperature) have qualitatively different rescue effects. Vary: noise_target ∈ {emotion, phi, temperature}. Measure: failure rate at κ=0.5.
- `agent_memory_seed` — Letting the agent encode its OWN early-episode memory before the seeded one shifts the valley. Vary: warmup_episodes ∈ {0, 1, 3, 5}. Measure: failure rate distribution.
- `conflict_geometry` — A 3-objective sandbox (rescue + resource + escape) produces a different paralysis pattern than 2-objective. Build mini-sandbox; measure failure across κ.

## Done (most recent at top)

- 2026-05-01: selective_encoding — magnitude-gated outcome encoding does NOT prevent the Homogenization Collapse; produces a U-shape (max divergence@ep9 = 11.5 pts at τ=0.3, 0 pts at τ≥0.5).
