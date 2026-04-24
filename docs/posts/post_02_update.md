# Post 2 — Update: contextual reactivation

> The update that introduced `sim(context, memory)` into MemoryImpact.

---

Update on my research into human-like AI agents.

Two months ago I shared an idea about moving AI from optimizing answers to
modeling behavior over time — introducing emotion vectors, memory aging, and
bounded autonomy (Snap Time). Over the past few weeks while refining the
framework, one interesting observation emerged during testing:

**Memory decay alone does not produce human-like behavior. Contextual
reactivation does.**

Humans don't simply forget because time passes. Old memories that seem
"forgotten" can suddenly influence decisions again when a similar situation
appears.

**Updated memory model**

```
MemoryImpact = exp(-β·age) · exp(α·importance) · exp(γ·|emotion|) · sim(context, memory)
```

Meaning: memories fade with age, important events persist longer, emotional
memories remain influential, similar situations reactivate old memories.

This small addition produced noticeably more human-like decision dynamics in
simulations. Agents sometimes hesitated before acting, reconsidered decisions,
and revived old emotional context in similar scenarios. Behavior started looking
less like reward optimization and more like experience-driven decision making.

I still strongly believe the next frontier in AI isn't just bigger models —
it's agents that behave like humans over time, with memory, emotion, conflict,
and imperfection.
