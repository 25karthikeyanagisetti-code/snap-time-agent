# Post 3 — First measurable result: the Paralysis Valley

> Draft for LinkedIn. Reports what we actually measured in
> `experiments/regime_map_v1/`. Heatmaps + curves attach as images.

---

**First real result from the human-like AI agent project.**

I expected adding emotion to a rational agent would gradually shift its
behavior. The data says something else.

I built a small sandbox — a 7×7 grid where the agent has to choose between
grabbing a resource (immediate reward, satisfies survival) and rescuing a
partner in danger (no reward, but emotionally charged by a seeded "abandonment"
memory). Then I swept two parameters:

- `T_snap` — the agent's deliberation window
- `κ` — how much emotion is allowed to influence its decisions

14,400 episodes. The result was not what I expected.

**Failure rate is NON-MONOTONIC in emotion weight.**

At T_snap = 12 with a seeded memory:

```
κ = 0.00 → 42% failure  (rational, sometimes runs out of time)
κ = 0.25 → 98% failure  ← worst possible
κ = 0.50 → 74% failure
κ = 1.00 → 22% failure
κ = 2.00 →  1% failure  (committed, always rescues partner)
```

A small amount of emotion makes the agent fail MORE than no emotion AND more
than strong emotion. There's a "Paralysis Valley" between κ = 0.25 and κ = 0.5
where the agent can't commit to anything. It hesitates, switches targets,
oscillates, and runs out of Snap Time.

The mechanism is mechanical and almost obvious in hindsight: a weak emotion
shifts the decision pressure enough to disrupt the clean rational path, but
not enough to commit to the emotional alternative. The agent ends up in an
indecision attractor where every step gets re-evaluated.

I checked this with two controls. With no seeded memory, the valley vanishes
completely — failure becomes flat in κ, controlled only by T_snap. With memory
present but with the recall-injection mechanism disabled, the valley shrinks
but doesn't disappear — the emotional content of the memory matters even when
the injection pathway is removed.

**Why this matters**

If the goal is to build agents that behave like people, this is the first
piece of evidence that the framework reproduces a real human pattern: people
also fail worst at intermediate emotional engagement. Full commitment works.
Detached rationality works. The middle is where you get stuck.

It's also a warning to anyone tuning emotional/affective systems: you can't
sweep emotion strength linearly and expect linear behavior. There's a regime
where adding feeling makes everything worse.

**What's next**

I want to know if the Paralysis Valley moves with memory severity, with persona
baseline, with the shape of the Φ coupling. And whether the same valley appears
in multi-agent scenarios where loyalty is reciprocal instead of seeded.

Code, data, and full results in the repo.

[Repo link goes here once pushed to GitHub]
