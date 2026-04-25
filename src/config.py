"""
Default hyperparameters for the snap-time-agent framework.

These are the *defaults*. Sweep drivers in experiments/ override the values
they care about. Keep this file frozen-ish; new experiments add their own
config rather than editing here.
"""

# Emotion vector — 5 components, fixed order
EMOTION_DIMS = ["survival", "guilt", "loyalty", "fear", "curiosity"]

# Per-step homeostatic decay (pull each emotion toward 0 each step)
EMOTION_DECAY = 0.04

# Event-driven emotion update rates
SURVIVAL_RATE = 0.10    # per unit time-pressure
GUILT_RATE = 0.12       # per unit recall strength of an abandonment memory
LOYALTY_RATE = 0.10     # per step adjacent to partner
FEAR_RATE = 0.18        # per unit threat in environment
CURIOSITY_RATE = 0.06   # per unit novelty

# MemoryImpact hyperparameters
MEM_BETA = 0.05    # age decay
MEM_ALPHA = 0.40   # importance amplifier
MEM_GAMMA = 0.50   # emotion-magnitude amplifier

# Reactivation threshold — memories with impact below this don't bleed into e_t
REACTIVATION_THRESHOLD = 0.30

# How much a recalled memory's stored emotion bleeds into current e_t
REACTIVATION_GAIN = 0.15

# Default Snap Time (overridden by sweep)
T_SNAP_DEFAULT = 10

# Default emotion-weight scalar in Phi (overridden by sweep)
KAPPA_DEFAULT = 1.0
