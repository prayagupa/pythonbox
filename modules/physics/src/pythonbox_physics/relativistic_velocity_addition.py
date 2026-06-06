#!/usr/bin/env python3
"""
Relativistic Velocity Addition — Animation
══════════════════════════════════════════════════════════════════════════════

In everyday life you just add speeds: if a train moves at 60 mph and you walk
forward at 3 mph inside it, you move at 63 mph relative to the platform.

Einstein said: *no*.  The true formula is:

          u + v
  w  =  ─────────
         1 + uv/c²

Consequence: stack a THOUSAND rockets, each firing at 0.99 c in its own
rest frame — the combined speed still never reaches c.  Speed of light is
not a barrier to crash into; it is an asymptote you approach forever.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Panel A (top)   : Boost-by-boost speed bars — classical vs relativistic
  Panel B (bot-L) : Velocity-addition law curves and live tracking dot
  Panel C (bot-R) : Lorentz γ factor showing time dilation / mass-energy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run:    python modules/physics/src/pythonbox_physics/relativistic_velocity_addition.py
Output: modules/physics/src/pythonbox_physics/relativistic_velocity_addition.gif
"""

import os

import numpy as np
import matplotlib

# macOS-friendly backend fallback (mirrors spacetime_curvature.py)
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _test_plt  # noqa: F401
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.animation import FuncAnimation, PillowWriter

# ── parameters ─────────────────────────────────────────────────────────────────
C          = 1.0    # speed of light (natural units)
BOOST_BETA = 0.60   # each rocket fires at this fraction of c in its own frame
N_BOOSTS   = 12     # number of successive boosts to animate
FPS        = 22     # frames per second
FPSTEP     = FPS    # frames spent animating each individual boost bar
HOLD       = FPS * 3  # extra hold frames at the end

# ── velocity-addition formulae ────────────────────────────────────────────────
def rel_add(u: float, v: float) -> float:
    """Einstein velocity-addition formula (c = 1)."""
    return (u + v) / (1.0 + u * v)


def lorentz_gamma(beta: float) -> float:
    """Lorentz factor γ = 1/√(1−β²)."""
    return 1.0 / np.sqrt(max(1.0 - beta ** 2, 1e-14))


# precompute speed sequences
classical    = [0.0]
relativistic = [0.0]
for _ in range(N_BOOSTS):
    classical.append(classical[-1] + BOOST_BETA)
    relativistic.append(rel_add(relativistic[-1], BOOST_BETA))

# ── colour palette ────────────────────────────────────────────────────────────
DARK_BG     = "#07071a"
PANEL_BG    = "#0c0c26"
GRID_COL    = "#1c1c44"
COL_CLASSIC = "#ff5040"
COL_RELATIV = "#44bbff"
COL_C_LINE  = "#ffd740"
COL_TEXT    = "#dde8ff"
COL_DIM     = "#7788aa"

plt.rcParams.update({
    "figure.facecolor": DARK_BG,
    "text.color":       COL_TEXT,
    "axes.facecolor":   PANEL_BG,
    "axes.edgecolor":   GRID_COL,
    "axes.labelcolor":  COL_TEXT,
    "xtick.color":      COL_TEXT,
    "ytick.color":      COL_TEXT,
    "grid.color":       GRID_COL,
    "grid.linewidth":   0.6,
    "font.family":      "DejaVu Sans",
})

# ── figure / grid ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 9))
gs  = fig.add_gridspec(
    2, 2,
    height_ratios=[1.7, 1],
    hspace=0.52, wspace=0.34,
    left=0.07, right=0.97, top=0.90, bottom=0.08,
)
ax_bars  = fig.add_subplot(gs[0, :])
ax_curve = fig.add_subplot(gs[1, 0])
ax_gamma = fig.add_subplot(gs[1, 1])

fig.suptitle(
    "⚡   Relativistic Velocity Addition   ⚡",
    fontsize=17, fontweight="bold", y=0.96,
    path_effects=[pe.withStroke(linewidth=4, foreground=DARK_BG)],
)

# ── Panel A — boost bars ──────────────────────────────────────────────────────
BAR_XLIM = 2.7
ax_bars.set_facecolor(PANEL_BG)
ax_bars.set_xlim(-0.05, BAR_XLIM)
ax_bars.set_ylim(-0.65, N_BOOSTS - 0.35)
ax_bars.set_xlabel("Speed  (units of  c)", fontsize=10)
ax_bars.set_yticks([])
ax_bars.set_title(
    f"Each rocket fires at  β = {BOOST_BETA}c  in its own rest frame"
    f"  ·  {N_BOOSTS} successive boosts",
    fontsize=10.5, pad=6,
)
ax_bars.grid(axis="x", alpha=0.25)

# speed-of-light wall
ax_bars.axvline(1.0, color=COL_C_LINE, lw=2.5, ls="--", zorder=8)
ax_bars.text(1.03, N_BOOSTS - 0.65, "c", color=COL_C_LINE,
             fontsize=15, fontweight="bold", va="top", zorder=9)

# create bar rectangles
bar_cls, bar_rel = [], []
for i in range(N_BOOSTS):
    yc = i + 0.14
    yr = i - 0.14
    bc = ax_bars.barh(yc, 0, height=0.26, color=COL_CLASSIC, alpha=0.90)[0]
    br = ax_bars.barh(yr, 0, height=0.26, color=COL_RELATIV, alpha=0.90)[0]
    ax_bars.text(-0.03, i, f"#{i + 1}", color=COL_DIM,
                 ha="right", va="center", fontsize=8.5)
    bar_cls.append(bc)
    bar_rel.append(br)

lp_c = mpatches.Patch(color=COL_CLASSIC, label="Classical   w = u + v")
lp_r = mpatches.Patch(color=COL_RELATIV,
                       label="Relativistic   w = (u+v) / (1 + uv/c²)")
ax_bars.legend(handles=[lp_c, lp_r], loc="lower right", fontsize=9,
               facecolor="#111130", edgecolor=GRID_COL)

info_box = ax_bars.text(
    1.12, N_BOOSTS - 0.4, "",
    color=COL_TEXT, fontsize=9.5, va="top", ha="left",
    bbox=dict(boxstyle="round,pad=0.5",
              facecolor="#111130", edgecolor=GRID_COL, alpha=0.88),
)

# ── Panel B — addition-law curves ────────────────────────────────────────────
v_arr = np.linspace(0.0, 0.999, 700)
w_cls = v_arr + BOOST_BETA
w_rel = np.array([rel_add(BOOST_BETA, v) for v in v_arr])

ax_curve.set_facecolor(PANEL_BG)
ax_curve.plot(v_arr, w_cls, color=COL_CLASSIC, lw=1.9, label="Classical")
ax_curve.plot(v_arr, w_rel, color=COL_RELATIV, lw=2.3, label="Relativistic")
ax_curve.axhline(1.0, color=COL_C_LINE, lw=1.8, ls="--")
ax_curve.axvline(1.0, color=COL_C_LINE, lw=1.8, ls="--", label="c")
ax_curve.fill_between(v_arr, w_rel, w_cls, alpha=0.09, color=COL_CLASSIC)
ax_curve.set_xlim(0, 1.12)
ax_curve.set_ylim(0, 2.15)
ax_curve.set_xlabel("Current speed  v/c", fontsize=9)
ax_curve.set_ylabel(f"After adding β = {BOOST_BETA} c", fontsize=9)
ax_curve.set_title("Velocity Addition Law", fontsize=10)
ax_curve.legend(fontsize=8.5, facecolor="#111130", edgecolor=GRID_COL)
ax_curve.grid(True, alpha=0.3)

dot_cls_c, = ax_curve.plot([], [], "o", color=COL_CLASSIC, ms=10, zorder=10,
                            markeredgecolor="white", markeredgewidth=0.7)
dot_rel_c, = ax_curve.plot([], [], "o", color=COL_RELATIV, ms=10, zorder=10,
                            markeredgecolor="white", markeredgewidth=0.7)

# ── Panel C — Lorentz γ ───────────────────────────────────────────────────────
β_arr = np.linspace(0.0, 0.9999, 700)
γ_arr = 1.0 / np.sqrt(1 - β_arr ** 2)

ax_gamma.set_facecolor(PANEL_BG)
ax_gamma.plot(β_arr, γ_arr, color=COL_RELATIV, lw=2.3)
ax_gamma.fill_between(β_arr, 1, γ_arr, alpha=0.08, color=COL_RELATIV)
ax_gamma.axvline(1.0, color=COL_C_LINE, lw=1.8, ls="--")
ax_gamma.axhline(1.0, color=COL_DIM, lw=0.8, ls=":")
ax_gamma.set_xlim(0, 1.05)
ax_gamma.set_ylim(0.5, 16)
ax_gamma.set_xlabel("Speed  β = v/c", fontsize=9)
ax_gamma.set_ylabel("Lorentz factor  γ", fontsize=9)
ax_gamma.set_title("Time dilation  ·  Length contraction  ·  Mass-energy", fontsize=10)
ax_gamma.grid(True, alpha=0.3)

gamma_dot, = ax_gamma.plot([], [], "o", color=COL_RELATIV, ms=10, zorder=10,
                            markeredgecolor="white", markeredgewidth=0.7)
gamma_lbl  = ax_gamma.text(
    0.05, 13.5, "",
    color=COL_TEXT, fontsize=9,
    bbox=dict(boxstyle="round,pad=0.4",
              facecolor="#111130", edgecolor=GRID_COL, alpha=0.88),
)

# ── animation ─────────────────────────────────────────────────────────────────
TOTAL_FRAMES = N_BOOSTS * FPSTEP + HOLD


def _active_and_frac(frame: int):
    """Return (active_step_index, fill_fraction) for a given frame."""
    if frame >= N_BOOSTS * FPSTEP:           # hold phase
        return N_BOOSTS - 1, 1.0
    step = frame // FPSTEP
    frac = (frame % FPSTEP) / FPSTEP
    return step, frac


def update(frame: int):
    active, frac = _active_and_frac(frame)
    step_shown = active + 1  # 1-based count of completed boosts (approx)

    # — bars —
    for i in range(N_BOOSTS):
        if i < active:
            bar_cls[i].set_width(classical[i + 1])
            bar_rel[i].set_width(relativistic[i + 1])
        elif i == active:
            bar_cls[i].set_width(classical[i + 1] * frac)
            bar_rel[i].set_width(relativistic[i + 1] * frac)
        # i > active: stays at 0

    # — info box —
    vc = classical[step_shown]
    vr = relativistic[step_shown]
    over_c = "  ⚠ > c !" if vc > 1.0 else ""
    # relativistic speed as a percentage of c
    pct = vr / C * 100
    info_box.set_text(
        f"After {step_shown} boost{'s' if step_shown > 1 else ''}:\n"
        f"  Classical :    {vc:.3f} c{over_c}\n"
        f"  Relativistic : {vr:.6f} c  ({pct:.2f}% of c)\n"
        f"  Gap from c :   {1.0 - vr:.6f} c"
    )

    # — addition-curve dots —
    prev_r = relativistic[active]          # speed before current boost
    dot_cls_c.set_data([prev_r], [classical[active + 1]])
    dot_rel_c.set_data([prev_r], [relativistic[active + 1]])

    # — γ dot —
    beta = relativistic[step_shown]
    gamma = lorentz_gamma(beta)
    gamma_dot.set_data([beta], [min(gamma, 15.5)])
    gamma_lbl.set_text(
        f"β  = {beta:.6f} c\n"
        f"γ  = {gamma:.3f}\n"
        f"Δt = {1/gamma:.4f} × t₀"
    )

    return (bar_cls + bar_rel
            + [dot_cls_c, dot_rel_c, gamma_dot, gamma_lbl, info_box])


ani = FuncAnimation(
    fig, update,
    frames=TOTAL_FRAMES,
    interval=1000 // FPS,
    blit=True,
)

# ── save ──────────────────────────────────────────────────────────────────────
out_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "relativistic_velocity_addition.gif",
)
print(f"Rendering {TOTAL_FRAMES} frames at {FPS} fps …")
ani.save(out_path, writer=PillowWriter(fps=FPS))
print(f"✓  Saved  →  {out_path}")
plt.show()
