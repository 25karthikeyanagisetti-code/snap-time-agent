"""Visual for exp_seed_refresh: do source-refresh and seed-only-floor match
at every β_guilt cell? Two-panel: Δep0 vs β_guilt for both mechanisms, plus
the cell-wise |Δ−Δ| gap."""
import csv, os
from collections import defaultdict
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "experiments", "seed_refresh_v1", "results.csv")
PNG = os.path.join(ROOT, "experiments", "seed_refresh_v1", "seed_refresh.png")

rows = list(csv.DictReader(open(CSV)))
by = defaultdict(list)
for r in rows:
    by[(r["inject_mode"], float(r["beta_guilt"]), int(r["episode_idx"]))].append(int(r["rescued"]))

betas = [0.05, 0.15, 0.30, 0.50]
def rate(mode, b, ep):
    v = by[(mode, b, ep)]
    return sum(v)/len(v)*100

off_ep0   = [rate("off", b, 0)             for b in betas]
floor_ep0 = [rate("seed_only_floor", b, 0) for b in betas]
ref_ep0   = [rate("seed_refresh", b, 0)    for b in betas]
dfloor = [f - o for f, o in zip(floor_ep0, off_ep0)]
dref   = [r - o for r, o in zip(ref_ep0,   off_ep0)]
gap    = [abs(r - f) for r, f in zip(dref, dfloor)]

bg = "#0e131f"; pa = "#131927"; txt = "#e8edf5"; grid = "#1f2638"; accent = "#ffe2ac"
c_off = "#4a5e85"; c_floor = "#4fc3f7"; c_refresh = "#c084fc"; c_gap = "#ff6b6b"

plt.rcParams.update({
    "axes.facecolor": pa, "figure.facecolor": bg, "savefig.facecolor": bg,
    "axes.edgecolor": "#3a455e", "axes.labelcolor": txt, "xtick.color": txt,
    "ytick.color": txt, "text.color": txt, "axes.titlecolor": txt,
    "grid.color": grid, "font.family": "DejaVu Sans",
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.6),
                                gridspec_kw={"width_ratios": [1.45, 1]})

# Panel 1 — ep0 rescue rate by mode
x = list(range(len(betas)))
ax1.plot(x, off_ep0,   "o-", lw=2.4, ms=9, color=c_off,     label="OFF (no inject)")
ax1.plot(x, floor_ep0, "s-", lw=2.4, ms=9, color=c_floor,   label="seed-only floor")
ax1.plot(x, ref_ep0,   "D-", lw=2.4, ms=9, color=c_refresh, label="seed_refresh (new)")
ax1.set_xticks(x); ax1.set_xticklabels([f"{b:.2f}" for b in betas])
ax1.set_xlabel("β_guilt  (β_loyalty = 0.05 fixed)", fontsize=11)
ax1.set_ylabel("ep0 rescue rate (%)", fontsize=11)
ax1.set_title("ep0 rescue rate — three injection regimes",
              fontsize=12, color=accent, pad=10)
ax1.set_ylim(20, 95)
ax1.grid(True, alpha=0.35, linestyle="--")
ax1.legend(loc="lower left", facecolor=pa, edgecolor="#3a455e",
           labelcolor=txt, fontsize=10)

# annotate the headline cell (β_g=0.50)
ax1.annotate(f"+{dref[-1]:.0f} pts",
             xy=(3, ref_ep0[-1]), xytext=(2.55, ref_ep0[-1]+4),
             fontsize=10, color=c_refresh, fontweight="bold")
ax1.annotate(f"+{dfloor[-1]:.0f} pts",
             xy=(3, floor_ep0[-1]), xytext=(2.55, floor_ep0[-1]-7),
             fontsize=10, color=c_floor, fontweight="bold")

# Panel 2 — |Δrefresh − Δfloor| cell-wise gap
bars = ax2.bar(x, gap, color=c_gap, alpha=0.85, edgecolor=accent, lw=1.0)
ax2.set_xticks(x); ax2.set_xticklabels([f"{b:.2f}" for b in betas])
ax2.set_xlabel("β_guilt", fontsize=11)
ax2.set_ylabel("|Δrefresh − Δfloor|  (pts)", fontsize=11)
ax2.set_title("Cell-wise mechanism gap\n(0 = perfect substitutability)",
              fontsize=12, color=accent, pad=10)
ax2.set_ylim(0, max(gap)*1.25 + 3)
ax2.grid(True, alpha=0.35, linestyle="--", axis="y")
for xi, g in zip(x, gap):
    ax2.text(xi, g+0.6, f"{g:.1f}", ha="center", color=txt, fontsize=10)
ax2.axhline(5.0, color=accent, lw=1.0, linestyle=":", alpha=0.65)
ax2.text(0.05, 5.4, "  5 pt 'substitutable' band",
         color=accent, fontsize=9, alpha=0.85)

fig.suptitle(
    "Seed-refresh vs seed-only-floor — substitutable only at the "
    "regime-breaking cell",
    fontsize=13.5, color=txt, y=1.01,
)
fig.text(
    0.5, -0.04,
    "β_guilt=0.50: |Δ−Δ|=2.5 pts (substitutable).  "
    "β_guilt={0.05, 0.15}: refresh OVER-corrects by 15–20 pts.  "
    "The floor's max() guardrail is mechanism-essential off-headline.",
    ha="center", color=txt, fontsize=10, alpha=0.92,
)

plt.tight_layout()
plt.savefig(PNG, dpi=140, bbox_inches="tight", facecolor=bg)
plt.close()
print(f"Wrote {PNG}")
print(f"Δfloor   = {[round(d,1) for d in dfloor]}")
print(f"Δrefresh = {[round(d,1) for d in dref]}")
print(f"|Δ−Δ|    = {[round(g,1) for g in gap]}")
