#!/usr/bin/env python3
"""
Lorenz Attractor — Animated 3-D Visualisation
==============================================
The Lorenz system is a set of three coupled ordinary differential equations
originally derived by Edward Lorenz (1963) as a simplified model of
atmospheric convection:

    dx/dt = σ (y − x)
    dy/dt = x (ρ − z) − y
    dz/dt = x y − β z

For the classic parameters σ=10, ρ=28, β=8/3 the system exhibits
*chaotic* behaviour: trajectories never repeat, and nearby initial
conditions diverge exponentially — the celebrated "butterfly effect".

What the animation shows:
  • Two trajectories launched from almost identical starting points
    (separated by ε = 1e-8) to visualise sensitive dependence.
  • A glowing "tail" of the last T_TAIL seconds emphasises the recent path.
  • The full attractor skeleton fades in as a translucent ghost so the
    viewer can appreciate the double-wing geometry.
  • A slowly rotating camera (azimuth drift) keeps the 3-D structure legible.
  • A real-time phase-space distance gauge in the corner shows when the
    two trajectories have diverged beyond any practical predictability.

Run from the repo root:
    python src/main/python/physics/lorenz_attractor.py

Output: lorenz_attractor.gif  (same directory as this script)

Dependencies: numpy, matplotlib, pillow  (all in requirements.txt)
"""

import numpy as np
import matplotlib

# ── macOS / headless backend fallback ────────────────────────────────────────
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _probe  # noqa: F401
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3-D projection
from pathlib import Path

# ── Output path ───────────────────────────────────────────────────────────────
OUT_PATH: Path = Path(__file__).parent / "lorenz_attractor.gif"

# ── Lorenz parameters (classic chaotic regime) ────────────────────────────────
SIGMA: float = 10.0
RHO: float = 28.0
BETA: float = 8.0 / 3.0

# ── Integration parameters ────────────────────────────────────────────────────
DT: float = 0.005          # RK4 time-step  [s]
N_STEPS: int = 12_000      # total integration steps
STEPS_PER_FRAME: int = 15  # solver steps advanced per animation frame
N_FRAMES: int = N_STEPS // STEPS_PER_FRAME
FPS: int = 30

# ── Visual parameters ─────────────────────────────────────────────────────────
T_TAIL: int = 180          # number of *frames* shown in the bright tail
EPSILON: float = 1e-8      # initial separation between the two trajectories

# ── Colour palette (dark space aesthetic) ─────────────────────────────────────
BG: str = "#06060f"
GHOST: str = "#1a1a3a"
COLOR_A: str = "#00e5ff"   # trajectory A — cyan
COLOR_B: str = "#ff4d6d"   # trajectory B — coral/red
DOT_A: str = "#ffffff"
DOT_B: str = "#ffdd57"
TEXT_COLOR: str = "#c8d8f0"


# ── ODE: Lorenz system ────────────────────────────────────────────────────────
def lorenz_deriv(state: np.ndarray) -> np.ndarray:
    """Return (dx/dt, dy/dt, dz/dt) for the Lorenz system."""
    x, y, z = state
    return np.array([
        SIGMA * (y - x),
        x * (RHO - z) - y,
        x * y - BETA * z,
    ])


def rk4_step(state: np.ndarray, dt: float) -> np.ndarray:
    """Single 4th-order Runge–Kutta step."""
    k1 = lorenz_deriv(state)
    k2 = lorenz_deriv(state + 0.5 * dt * k1)
    k3 = lorenz_deriv(state + 0.5 * dt * k2)
    k4 = lorenz_deriv(state + dt * k3)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


# ── Pre-compute trajectories ──────────────────────────────────────────────────
print("Pre-computing Lorenz trajectories …")

ic_a = np.array([0.1, 0.0, 0.0])
ic_b = ic_a + np.array([EPSILON, 0.0, 0.0])

# Store one point per animation frame (after STEPS_PER_FRAME RK4 steps)
traj_a = np.empty((N_FRAMES, 3))
traj_b = np.empty((N_FRAMES, 3))

state_a, state_b = ic_a.copy(), ic_b.copy()

for frame_idx in range(N_FRAMES):
    for _ in range(STEPS_PER_FRAME):
        state_a = rk4_step(state_a, DT)
        state_b = rk4_step(state_b, DT)
    traj_a[frame_idx] = state_a
    traj_b[frame_idx] = state_b
    if frame_idx % 100 == 0:
        print(f"  frame {frame_idx}/{N_FRAMES}")

print(f"Pre-computation complete — {N_FRAMES} frames ready.")

# Pre-compute phase-space separation at each frame
separation = np.linalg.norm(traj_a - traj_b, axis=1)
sep_max = separation.max()

# ── Figure & axes setup ───────────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 8), facecolor=BG)
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)

ax3d = fig.add_axes([0.0, 0.12, 0.80, 0.88], projection="3d")
ax3d.set_facecolor(BG)
ax3d.set_axis_off()
for pane in (ax3d.xaxis.pane, ax3d.yaxis.pane, ax3d.zaxis.pane):
    pane.fill = False
    pane.set_edgecolor("none")

# Ghost skeleton: plot the full attractor in a faint colour
ax3d.plot(
    traj_a[:, 0], traj_a[:, 1], traj_a[:, 2],
    color=GHOST, lw=0.35, alpha=0.35, zorder=1,
)

# Live tail lines (will be updated each frame)
line_a, = ax3d.plot([], [], [], color=COLOR_A, lw=1.0, alpha=0.85, zorder=3)
line_b, = ax3d.plot([], [], [], color=COLOR_B, lw=1.0, alpha=0.85, zorder=3)

# Current position dots
dot_a, = ax3d.plot([], [], [], "o", color=DOT_A, ms=4, zorder=5)
dot_b, = ax3d.plot([], [], [], "o", color=DOT_B, ms=4, zorder=5)

# Axis limits from full trajectory
pad = 5
x_lim = (traj_a[:, 0].min() - pad, traj_a[:, 0].max() + pad)
y_lim = (traj_a[:, 1].min() - pad, traj_a[:, 1].max() + pad)
z_lim = (traj_a[:, 2].min() - pad, traj_a[:, 2].max() + pad)
ax3d.set_xlim(*x_lim)
ax3d.set_ylim(*y_lim)
ax3d.set_zlim(*z_lim)

# ── Info overlay (top-left) ───────────────────────────────────────────────────
title_text = ax3d.text2D(
    0.03, 0.97,
    "Lorenz Attractor",
    transform=ax3d.transAxes,
    color=TEXT_COLOR, fontsize=14, fontweight="bold", va="top",
)
param_text = ax3d.text2D(
    0.03, 0.91,
    f"σ={SIGMA}  ρ={RHO}  β={BETA:.4f}",
    transform=ax3d.transAxes,
    color=TEXT_COLOR, fontsize=9, va="top", alpha=0.75,
)
time_text = ax3d.text2D(
    0.03, 0.86,
    "t = 0.000 s",
    transform=ax3d.transAxes,
    color=TEXT_COLOR, fontsize=9, va="top",
)

# ── Separation bar (right strip) ──────────────────────────────────────────────
ax_sep = fig.add_axes([0.82, 0.18, 0.06, 0.65], facecolor="#0d0d20")
ax_sep.set_xlim(0, 1)
ax_sep.set_ylim(0, 1)
ax_sep.set_xticks([])
ax_sep.set_yticks([])
for spine in ax_sep.spines.values():
    spine.set_edgecolor("#2a2a4a")

sep_bar = ax_sep.barh(0, 0, height=0.07, color="#ff4d6d", left=0)[0]
ax_sep.text(
    0.5, 1.03, "Divergence", ha="center", va="bottom",
    color=TEXT_COLOR, fontsize=7, transform=ax_sep.transAxes,
)
sep_val_text = ax_sep.text(
    0.5, -0.06, "0.00", ha="center", va="top",
    color=TEXT_COLOR, fontsize=7, transform=ax_sep.transAxes,
)

# Vertical bar chart for separation (rotated: y = fraction)
sep_bar_v = ax_sep.bar(0.5, 0, width=0.8, color="#ff4d6d", bottom=0)[0]
ax_sep.set_ylim(0, 1)

# ── Legend strip at bottom ────────────────────────────────────────────────────
ax_leg = fig.add_axes([0.0, 0.01, 0.80, 0.08], facecolor=BG)
ax_leg.set_axis_off()
ax_leg.plot([0.05, 0.12], [0.5, 0.5], color=COLOR_A, lw=2,
            transform=ax_leg.transAxes)
ax_leg.text(0.14, 0.5, "Trajectory A", color=COLOR_A, fontsize=9,
            va="center", transform=ax_leg.transAxes)
ax_leg.plot([0.32, 0.39], [0.5, 0.5], color=COLOR_B, lw=2,
            transform=ax_leg.transAxes)
ax_leg.text(0.41, 0.5,
            f"Trajectory B  (ε = {EPSILON:.0e})", color=COLOR_B,
            fontsize=9, va="center", transform=ax_leg.transAxes)

# ── Animation function ────────────────────────────────────────────────────────
AZ_START: float = 30.0
AZ_DRIFT: float = 0.18   # degrees per frame


def _update(frame: int) -> list:
    """Update artists for the given frame index."""
    start = max(0, frame - T_TAIL)

    xs_a = traj_a[start:frame + 1, 0]
    ys_a = traj_a[start:frame + 1, 1]
    zs_a = traj_a[start:frame + 1, 2]

    xs_b = traj_b[start:frame + 1, 0]
    ys_b = traj_b[start:frame + 1, 1]
    zs_b = traj_b[start:frame + 1, 2]

    line_a.set_data(xs_a, ys_a)
    line_a.set_3d_properties(zs_a)

    line_b.set_data(xs_b, ys_b)
    line_b.set_3d_properties(zs_b)

    dot_a.set_data([traj_a[frame, 0]], [traj_a[frame, 1]])
    dot_a.set_3d_properties([traj_a[frame, 2]])

    dot_b.set_data([traj_b[frame, 0]], [traj_b[frame, 1]])
    dot_b.set_3d_properties([traj_b[frame, 2]])

    t_now = frame * STEPS_PER_FRAME * DT
    time_text.set_text(f"t = {t_now:.2f} s")

    # Rotate camera
    ax3d.view_init(elev=22, azim=AZ_START + frame * AZ_DRIFT)

    # Separation gauge
    frac = min(separation[frame] / sep_max, 1.0)
    sep_bar_v.set_height(frac)
    sep_val_text.set_text(f"{separation[frame]:.2f}")

    return [line_a, line_b, dot_a, dot_b, time_text, sep_bar_v, sep_val_text]


# ── Render ────────────────────────────────────────────────────────────────────
print(f"Rendering {N_FRAMES} frames to GIF …")

anim = animation.FuncAnimation(
    fig, _update,
    frames=N_FRAMES,
    interval=1000 // FPS,
    blit=False,
)

anim.save(str(OUT_PATH), writer=animation.PillowWriter(fps=FPS))
print(f"Saved → {OUT_PATH}")
print("Displaying animation in UI window …")
plt.show()
plt.close(fig)

if __name__ == "__main__":
    pass

