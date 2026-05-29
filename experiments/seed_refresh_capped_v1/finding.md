# Finding — `seed_refresh_capped` (2026-05-19)

## Result

**HELD.** Replacing yesterday's unconditional `m.emotion := encoding_template` overwrite with `m.emotion[k] := max(stored[k], SEED_FLOOR[k])` per dim reproduces the seed-only-floor injection-floor Δep0 vector at every β_guilt cell. Max |Δcapped − Δfloor| at ep0 = **7.5 pts**; mean **5.6 pts**. Both within the 2-SE band (≈10 pts for a single rate Δ, ≈22 pts for the Δ-of-Δ) at N=40. The over-restoration pathology that broke yesterday's seed_refresh at low and mild asymmetry (−10 pts at β=0.05 and −17.5 pts at β=0.15) is fully eliminated: capped delivers +5 and +2.5 at the same two cells.

## Headline number

|Δcapped − Δfloor| at ep0 = `{7.5, 5.0, 5.0, 5.0}` pts across β_guilt ∈ `{0.05, 0.15, 0.30, 0.50}`. Yesterday's |Δrefresh − Δfloor| was `{15.0, 20.0, 10.0, 2.5}`. Max gap collapses 20.0 → 7.5; mean gap collapses 11.9 → 5.6.

## Mechanism

The seed memory participates in two pathways simultaneously: (a) the `γ·|emotion|` term inside `MemoryImpact`, which weights how loud the seed prior sounds during the recall scoring, and (b) the literal-stored injection path, which bleeds the stored emotion onto current `e_t` when reactivation crosses threshold. Both pathways read from `m.emotion` directly. So whether you apply `max(stored, floor)` at the moment of injection (the floor table) or at the moment of storage (the capped variant), the agent's Φ sees the same number by the time the action is scored.

This explains why two NUMERICALLY IDENTICAL `max(stored, floor)` operators applied at different positions in the pipeline deliver substitutable behavior — the only path from `m.emotion` to Φ goes through reads of `m.emotion`. There is no intermediate transformation that one application order applies and the other doesn't.

Yesterday's seed_refresh broke that symmetry because OVERWRITE is not the same operator as MAX. Overwrite is `m.emotion := template` unconditionally. At cells where the stored emotion has NOT yet decayed below the template (low β_guilt), overwrite *removes* signal that the agent would otherwise have. At cells where stored HAS decayed below the template (high β_guilt), overwrite restores it. The result is a sign-flipping Δep0 vector: helps at the regime-break, hurts at low asymmetry. The capped variant uses MAX, which is one-sided by construction — silent in the low-β regime, lifting in the high-β regime — and that one-sidedness exactly mirrors the floor table's behavior.

## What would falsify this interpretation

The cleanest falsifier would be a cell where the capped variant and the floor variant diverge beyond the 2-SE band at N=200. Likely candidates: (i) β_loyalty asymmetry — today's design fixes β_loyalty=0.05; a sweep at β_loyalty ∈ {0.15, 0.30} would test whether source-vs-gate isomorphism survives across the channel pair; (ii) outcome-encoded memories — today the capped hook is seed-only; attaching per-memory floors to failure-tagged outcomes is the next compression step; (iii) multi-memory cells where several priors compete and the order of `max(stored, floor)` application interacts with recall ranking.

A separate falsifier would be a long-chain effect: at chain_length=10 the seed memory's relative weight in the store is moderate, but past chain_length=20 the outcome-encoded memories dominate and the seed-only guardrail may stop being load-bearing. The ep5–9 rescue rates today are within 4.5 pts across modes (suggestive, not conclusive at N=40).

## Why this matters as a finding

The architectural payoff is concrete: the entire `TAG_FLOORS_DEFAULT` dispatch table (4 tags × 5 emotion dims = 20 numbers) and the `inject_recalled_emotion_tag_aware` code path collapse into a single per-memory `floor` field set at encoding time and a one-line `max(stored, floor)` guardrail applied at the source. No per-tag dispatch, no injection-time logic, no special-cased recall path. This is the second consecutive compression step in the floor-mechanism chain: 2026-05-12 compressed the floor TABLE to a single seed entry; today compresses the floor APPLICATION POINT from injection-time dispatch to encoding-time attachment.

In framework terms, the mechanism that closes the β_guilt=0.50 ep0 collapse is now reducible to a property of individual memories — a small piece of state each memory carries with it. That moves the architecture closer to a clean "memories age, but the seed knows its own floor" abstraction.

## Follow-up experiments (queued)

- `capped_floor_loyalty_sweep` — replicate at β_loyalty ∈ {0.15, 0.30} with β_guilt=0.05 fixed, testing channel symmetry.
- `capped_floor_outcome_attach` — attach per-memory floors to FAILURE-tagged and RESCUE-tagged outcome memories at encoding time; drop the corresponding tag entries from `TAG_FLOORS_DEFAULT`. Tests whether the source-application strategy extends from the seed (which is created once) to outcomes (which are encoded every episode).
- `capped_floor_n200` — replicate today's β=0.05 cell at N=200 to tighten the 7.5-pt max gap and confirm the substitutability claim against statistical noise.
- `capped_floor_long_chain` — run capped vs floor at chain_length=30 to test whether the equivalence survives past the chain horizon where outcome encodings dominate the store.

## Files

- `experiments/seed_refresh_capped_v1/README.md` — scannable summary
- `experiments/seed_refresh_capped_v1/finding.md` — this document
- `experiments/seed_refresh_capped_v1/results.csv` — 4,800 episode rows
- `experiments/seed_refresh_capped_v1/seed_refresh_capped.png` — Δep0 + substitutability chart
- `src/exp_seed_refresh_capped.py` — runner
- `src/sandbox.py` — new param `seed_refresh_capped_on_recall` (off by default)
