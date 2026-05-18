# Finding — Seed-Refresh Bypass (PARTIAL: held at headline cell, refuted off-headline)

**Date:** 2026-05-18 · **Experiment:** `exp_seed_refresh` ·
**Episodes:** 4,800 (3 modes × 4 β_guilt cells × 40 agents × 10 episodes)

## Result

The floor-table-bypass hypothesis HOLDS at the regime-breaking cell
(β_guilt=0.50) where Δrefresh and Δfloor agree to 2.5 pts (within
sampling noise). It is REFUTED at low and mild asymmetry where the source-
refresh mechanism over-corrects by 10–20 pts.

| β_guilt | Δfloor (pts) | Δrefresh (pts) | \|Δr − Δf\| (pts) |
|---:|---:|---:|---:|
| 0.05 | +5.0  | **−10.0** | 15.0 |
| 0.15 | +2.5  | **−17.5** | 20.0 |
| 0.30 | −2.5  | +7.5      | 10.0 |
| 0.50 | +37.5 | +40.0     | **2.5** |

The narrow "yes, the floor table is non-essential" story collapses once
you look across the asymmetry sweep instead of just at the cell that
motivated the chain.

## Mechanism — why the two diverge off-headline

The seed memory's stored.guilt after 15 steps of preage:

- β_guilt = 0.05 → `0.9 · 0.95^15 ≈ 0.42`
- β_guilt = 0.15 → `0.9 · 0.85^15 ≈ 0.077`
- β_guilt = 0.30 → `0.9 · 0.70^15 ≈ 0.0042`
- β_guilt = 0.50 → `0.9 · 0.50^15 ≈ 0.0000275`

The SEED_FLOOR template injects guilt=0.6. `max(stored, floor)` therefore
yields:

- β_g=0.05: max(0.42, 0.6) = 0.6 → effective injection lifts stored.guilt
  by 0.18 above its natural value.
- β_g=0.50: max(≈0, 0.6) = 0.6 → effective injection lifts by ~0.6 (the
  whole gap).

The floor's max() is a **conditional restoration** — it intervenes only
when stored has fallen below 0.6. At symmetric β_guilt, the seeded prior
is still mostly intact, so the floor is mostly inert.

`seed_refresh` is unconditional — it overwrites stored.guilt back to 0.9
at every step, irrespective of how much natural decay has happened. At
β_g=0.05 the refresh injects guilt=0.9 on a memory that would have
naturally held guilt=0.42 — a 2.14× over-restoration relative to the
floor's max-gated 0.6.

The compounding pathway has two arms:

1. **Injection amplitude.** When the seed memory reactivates above
   threshold, the injection adds gain × stored.guilt to the agent's
   current emotion. Refresh delivers gain×0.9; floor delivers gain×0.6;
   legacy literal-stored injection delivers gain×0.42.
2. **Impact-time recall strength.** `MemoryImpact ∝ exp(γ · |emotion|)`.
   With γ=0.50 and stored.guilt going from 0.42 to 0.9 (and stored.loyalty
   from ~0.28 to 0.6), `|emotion|` rises from ~0.85 to 1.8 — `exp(0.5 ·
   0.95) = 1.61`× boost to recall strength on every step.

Result at β_g=0.05: the agent gets injected with a stronger guilt template
on every step AND the prior fires MORE OFTEN (higher impact crossing the
threshold more readily). Both arms push toward over-guilt-loading —
ep0 collapses 10 pts below the OFF baseline.

At β_g=0.50, both the floor's max() and the refresh's overwrite saturate
at the encoding template — there is no headroom for the refresh to over-
correct because the stored value has already laundered to zero. The two
mechanisms converge by construction.

## What would falsify the "over-correction at low β_guilt" interpretation

- **Floor at full encoding magnitude.** If we lift SEED_FLOOR.guilt from
  0.6 to 0.9 (i.e. make the floor match the encoding template), the floor
  should now reproduce the seed_refresh over-correction at low β_guilt.
  If it does, the over-correction is purely about magnitude, not the
  max-vs-overwrite operator. If the floor at 0.9 still helps where
  refresh hurts, there's an operator-level difference (max gates EVERY
  step; refresh fires unconditionally regardless of stored).
- **One-shot refresh at episode start.** Refresh stored.emotion to the
  encoding template once at ep0 step 0, then let natural decay take over.
  If this matches the floor's signal at every cell, the per-step
  rejuvenation is what causes the over-correction. If it still over-
  corrects, the issue is the larger magnitude itself.
- **N=200 replicate at β_guilt=0.05 and 0.15.** The 10-pt and 17.5-pt
  refresh penalties at N=40 sit just outside the 2-SE band (~11 pts).
  A tighter replicate would confirm or shrink these signals.

## Follow-up experiments queued

The findings open three concrete next moves:

1. **`seed_refresh_capped`** — change the refresh from
   `m["emotion"] = encoding` to `m["emotion"] = {k: max(stored[k],
   floor[k])}` using SEED_FLOOR. Predicts: matches seed_only_floor at all
   four cells. If yes, the operative mechanism is **"max-guardrail
   applied to the seed"** — and the floor-table mechanism can be
   dropped to a single per-memory `floor` field, no tag table needed.
2. **`seed_refresh_b50_n200`** — replicate β_guilt=0.50 at N=200 to
   tighten the 2.5-pt substitutability claim. The OFF baseline this run
   (40.0%) is 17.5 pts below the 2026-05-12 N=40 reading (57.5%), so
   either the cell is intrinsically noisy at N=40 (likely) or there's a
   genuine seed-pattern effect across the chain. N=200 resolves it.
3. **`seed_refresh_kappa_sweep`** — replicate at κ ∈ {0.5, 2.0}. The
   over-correction story predicts: at κ=2.0 (already-saturated-committed
   regime) the refresh penalty grows — additional prior locks the agent
   deeper. At κ=0.5 (boomerang shoulder) the refresh penalty shrinks
   because ep0 rescue is already low and the dynamic range is compressed.

## How this fits the project arc

The chain from `tag_aware_injection` (2026-05-11) → `seed_only_floor`
(2026-05-12) → `seed_only_floor_b30_n200` (2026-05-13) was progressively
collapsing the per-tag floor TABLE down to a single seed-template
intervention. This run pushes one step further and asks whether the
floor MECHANISM (max-at-injection) is also reducible — to a source-level
emotion refresh.

It is not. The max() guardrail is the smallest sufficient mechanism. The
correct minimal construct for this layer of the framework is "the seed
memory carries a per-channel injection floor, applied at recall time."
The four-entry tag table can go; the per-channel floor on the seed
cannot.
