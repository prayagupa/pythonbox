#!/usr/bin/env python3
"""
Lorenz Attractor — Pure Visual
==============================
A colour-gradient animation of the Lorenz strange attractor in 3-D.
No axes, no labels, no text — just the glowing trajectory against black.

Colour palette: dark-red → orange → yellow → bright-green
  (oldest tail segments = deep red, newest = vivid green)

The double-wing butterfly skeleton is drawn as a barely-visible ghost so
the full geometry is readable from frame one; the animated tail sweeps
through it with a two-layer glow effect (thick soft bloom + sharp core).

Run:
    python src/main/python/physics/lorenz_attractor_visual.py

Output: lorenz_attractor_visual.gif  (same directory as this script)

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
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3-D projection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from pathlib import Path

# ── Output path ───────────────────────────────────────────────────────────────
OUT_PATH: Path = Path(__file__).parent / "lorenz_attractor_visual.gif"

# ── Lorenz parameters (classic chaotic regime) ────────────────────────────────
SIGMA: float = 10.0
RHO: float = 28.0
BETA: float = 8.0 / 3.0

# ── Integration parameters ────────────────────────────────────────────────────
DT: float = 0.005
N_STEPS: int = 14_000
STEPS_PER_FRAME: int = 12
N_FRAMES: int = N_STEPS // STEPS_PER_FRAME
FPS: int = 30

# ── Visual parameters ─────────────────────────────────────────────────────────
T_TAIL: int = 240          # tail length in frames
BG: str = "#060608"        # near-black background

# Gradient: deep crimson → red → orange → yellow
CMAP: LinearSegmentedColormap = LinearSegmentedColormap.from_list(
    "fire_to_yellow",
    [
        "#5a0000",   # very dark red  (oldest / fading)
        "#cc1100",   # vivid red
        "#ff4400",   # red-orange
        "#ff8800",   # amber-orange
        "#ffdd00",   # golden-yellow
        "#ffee66",   # pale yellow (newest / head)
    ],
)

# Camera
AZ_START: float = 28.0
AZ_DRIFT: float = 0.14    # degrees per frame
ELEV: float = 20.0


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
    return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


# ── Pre-compute trajectory ────────────────────────────────────────────────────
print("Pre-computing Lorenz trajectory …")

state = np.array([0.1, 0.0, 0.0])
traj = np.empty((N_FRAMES, 3))

for _i in range(N_FRAMES):
    for _ in range(STEPS_PER_FRAME):
        state = rk4_step(state, DT)
    traj[_i] = state
    if _i % 100 == 0:
        print(f"  frame {_i}/{N_FRAMES}")

print(f"Pre-computation complete — {N_FRAMES} frames ready.")

# ── Figure & axes setup ───────────────────────────────────────────────────────
fig = plt.figure(figsize=(10, 8), facecolor=BG)
ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection="3d")
ax.set_facecolor(BG)
ax.set_axis_off()
for _pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    _pane.fill = False
    _pane.set_edgecolor("none")
ax.grid(False)

# Axis limits
_pad = 5
ax.set_xlim(traj[:, 0].min() - _pad, traj[:, 0].max() + _pad)
ax.set_ylim(traj[:, 1].min() - _pad, traj[:, 1].max() + _pad)
ax.set_zlim(traj[:, 2].min() - _pad, traj[:, 2].max() + _pad)

# Ghost skeleton: full attractor, barely visible, tinted dark crimson
ax.plot(
    traj[:, 0], traj[:, 1], traj[:, 2],
    color="#1c0808", lw=0.45, alpha=0.55, zorder=1,
)

# Layer 1 — outer bloom (wide, soft, low alpha)
lc_bloom = Line3DCollection([], linewidths=6.0, zorder=3)
ax.add_collection3d(lc_bloom, autolim=False)

# Layer 2 — mid glow (medium width)
lc_glow = Line3DCollection([], linewidths=2.8, zorder=4)
ax.add_collection3d(lc_glow, autolim=False)

# Layer 3 — sharp core (thin, high alpha)
lc_core = Line3DCollection([], linewidths=1.0, zorder=5)
ax.add_collection3d(lc_core, autolim=False)

# Current-position dot — bright white with orange halo
dot, = ax.plot(
    [], [], [], "o",
    color="#ffffff", ms=5, zorder=6,
    markeredgecolor="#ffdd00", markeredgewidth=1.5,
)


# ── Colour helpers ────────────────────────────────────────────────────────────
def _tail_rgba(
    n_segs: int,
    alpha_min: float,
    alpha_max: float,
) -> np.ndarray:
    """Return RGBA array (n_segs, 4), oldest → newest along the gradient."""
    t = np.linspace(0.0, 1.0, max(n_segs, 1))
    rgba = CMAP(t)
    rgba[:, 3] = alpha_min + (alpha_max - alpha_min) * t
    return rgba


# ── Animation update function ─────────────────────────────────────────────────
def _update(frame: int) -> list:
    """Redraw all animated artists for the given frame index."""
    start = max(0, frame - T_TAIL)
    pts = traj[start: frame + 1]          # shape (n, 3)

    if len(pts) < 2:
        return [lc_bloom, lc_glow, lc_core, dot]

    # Build segments: shape (n-1, 2, 3)
    segs = np.stack([pts[:-1], pts[1:]], axis=1)

    bloom_colors = _tail_rgba(len(segs), alpha_min=0.00, alpha_max=0.12)
    glow_colors = _tail_rgba(len(segs), alpha_min=0.00, alpha_max=0.35)
    core_colors = _tail_rgba(len(segs), alpha_min=0.02, alpha_max=0.92)

    lc_bloom.set_segments(segs)
    lc_bloom.set_color(bloom_colors)

    lc_glow.set_segments(segs)
    lc_glow.set_color(glow_colors)

    lc_core.set_segments(segs)
    lc_core.set_color(core_colors)

    # Head dot
    dot.set_data([traj[frame, 0]], [traj[frame, 1]])
    dot.set_3d_properties([traj[frame, 2]])

    # Slowly drift the camera azimuth
    ax.view_init(elev=ELEV, azim=AZ_START + frame * AZ_DRIFT)

    return [lc_bloom, lc_glow, lc_core, dot]


# ── Render ────────────────────────────────────────────────────────────────────
print(f"Rendering {N_FRAMES} frames to GIF …")

anim = animation.FuncAnimation(
    fig, _update,
    frames=N_FRAMES,
    interval=1000 // FPS,
    blit=False,
)

anim.save(str(OUT_PATH), writer=animation.PillowWriter(fps=FPS), dpi=60)
print(f"Saved → {OUT_PATH}")
print("Displaying animation in UI window …")
plt.show()
plt.close(fig)

if __name__ == "__main__":
    pass

