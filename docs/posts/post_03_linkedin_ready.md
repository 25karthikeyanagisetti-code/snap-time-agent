# Post 3 — LinkedIn ready

> Copy the body below into LinkedIn. Attach the three images in this order:
>   1. paralysis_valley_hero.png
>   2. memory_on_vs_off.png
>   3. regime_map.png
> Hashtags + repo link go at the bottom.

---

First measurable result from my human-like AI agent project.

I expected adding emotion to a rational AI agent would gradually shift its behavior. The data said something different.

I built a small sandbox — a 7×7 grid where the agent has to choose between grabbing a resource (immediate reward, satisfies survival) and rescuing a partner in danger (no reward, but emotionally charged by a seeded "abandonment" memory).

Then I swept two parameters across 14,400 episodes:
- T_snap → how much time the agent has to think
- κ → how much emotion influences its decisions

Result: failure rate is NON-MONOTONIC in emotion weight.

A small amount of emotion makes the agent fail MORE than no emotion AND more than strong emotion.

At Snap Time = 12 with seeded memory:
- κ = 0.00 → 42% failure (rational, sometimes too slow)
- κ = 0.25 → 98% failure ← worst
- κ = 0.50 → 74% failure
- κ = 1.00 → 22% failure
- κ = 2.00 → 1% failure (commits and rescues partner)

I'm calling it the Paralysis Valley.

The mechanism is almost obvious in hindsight. A weak emotion shifts the decision pressure enough to disrupt the clean rational path, but not enough to commit to the alternative. The agent oscillates between targets and runs out of Snap Time.

I checked it with controls. With no seeded memory the valley vanishes completely — failure rate becomes flat in κ. The valley exists ONLY when emotional memory is in play.

Three regimes emerge:
- RATIONAL → κ ≈ 0 → grabs resource, ignores partner
- PARALYZED → κ ≈ 0.25–0.5 → can't decide, fails at almost everything
- COMMITTED → κ ≥ 1 → goes for partner, accepts the cost

To my knowledge this is the first time this specific failure mode has been measured inside an emotion + memory + Snap Time architecture. It mirrors a real human pattern — full commitment works, detached rationality works, the middle is where you get stuck.

It is also a warning to anyone tuning emotional or affective AI systems: you cannot sweep emotion strength linearly and expect linear behavior. There is a regime where adding feeling makes everything worse.

Next I want to map how the valley moves with memory severity, with persona baseline, and with multi-agent loyalty instead of seeded loyalty.

Code, data, full results in the repo: [link to GitHub repo]

Curious what others working on agent systems or cognitive architectures think — does the valley appear in your work too, or is this an artifact of this specific framework?

#AIResearch #AgentSystems #CognitiveArchitecture #HumanLikeAI #MachineLearning
