#!/usr/bin/env python3
"""
Standing Wave — Pulsating Rings in 3-D
═══════════════════════════════════════
A focused 3-D visualization of a cylindrical standing wave formed by the
superposition of an outgoing and a reflected wave from the same source.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KEY PHYSICS:
  • Outgoing wave:   cos(k·r − ω·t) / √r · e^(−αr)
  • Reflected wave:  cos(k·r + ω·t) / √r · e^(−αr)
  • Standing wave:   2·cos(k·r)·cos(ω·t) / √r · e^(−αr)

  The entire 3-D surface BREATHES uniformly in/out:
    – At  cos(ω·t) = ±1  the surface peaks/valleys are maximum.
    – At  cos(ω·t) =  0  the whole surface collapses to z = 0.

  NODE RINGS  (always z = 0):
    k·r = π/2 + n·π  →  r_n = (2n+1)·λ/4
  These rings never move; the surface pulsates between them.

  A slow camera orbit lets you see the 3-D ring-and-valley
  structure from all angles.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dependencies (all in requirements.txt): numpy, matplotlib
"""

import os
import warnings
import numpy as np

import matplotlib
# macOS-friendly backend fallback chain (mirrors spacetime_curvature.py)
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _test_plt  # noqa: F401
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────────────────
BG     = "#03030e"
TEXT   = "#dde8ff"
RED    = "#ff2244"
ORANGE = "#ff8833"
VIOLET = "#cc44ff"   # node-ring colour
INDIGO = "#5566ff"
WHITE  = "#ffffff"

# ─────────────────────────────────────────────────────────
#  WAVE COLORMAP  (deep trough → zero → bright crest)
# ─────────────────────────────────────────────────────────
WAVE_CMAP = LinearSegmentedColormap.from_list(
    "wave_deep",
    ["#0a0025", "#2200aa", BG, VIOLET, RED, WHITE],
    N=256,
)

# ─────────────────────────────────────────────────────────
#  ANIMATION PARAMETERS
# ─────────────────────────────────────────────────────────
FPS          = 20
TOTAL_FRAMES = 120          # 6 s  — ~3.5 full breathing cycles
ORBIT_SPEED  = 0.5          # deg/frame camera orbit

# ─────────────────────────────────────────────────────────
#  SPATIAL GRID
# ─────────────────────────────────────────────────────────
GRID_N = 80
LIM    = 5.0
_grid  = np.linspace(-LIM, LIM, GRID_N)
XX, YY = np.meshgrid(_grid, _grid)

# ─────────────────────────────────────────────────────────
#  WAVE PARAMETERS
# ─────────────────────────────────────────────────────────
WAVELENGTH = 1.5
K          = 2 * np.pi / WAVELENGTH
WAVE_SPEED = 2.5
OMEGA      = WAVE_SPEED * K
PERIOD     = 2 * np.pi / OMEGA
FREQ       = OMEGA / (2 * np.pi)
DAMPING    = 0.055

_THETA  = np.linspace(0, 2 * np.pi, 180)
Z_LIM   = 1.8
N_NODES = 10    # max node rings to draw

# Camera start
_AZ0  = -55.0
_ELEV = 40.0


# ─────────────────────────────────────────────────────────
#  WAVE FUNCTION
# ─────────────────────────────────────────────────────────
def _R_grid():
    """Softened radial distance from the origin."""
    return np.sqrt(XX ** 2 + YY ** 2) + 0.25


def u_standing(t):
    """
    Cylindrical standing wave:
        u(r, t) = 2·cos(k·r)·cos(ω·t) · exp(−α·r) / √r

    The spatial envelope  2·cos(k·r)/√r  is fixed in space.
    The temporal factor  cos(ω·t)  causes the whole surface to
    breathe uniformly: maximum at t = n·T, zero at t = (n+½)·T.
    """
    R   = _R_grid()
    amp = 2.0 * np.cos(K * R) * np.exp(-DAMPING * R) / np.sqrt(R)
    return amp * np.cos(OMEGA * t)


def node_radii():
    """
    Analytic positions of permanent node rings.
    Node condition:  k·r = π/2 + n·π  →  r_n = (2n+1)·λ/4
    Returns all node radii within the display domain.
    """
    nodes = []
    n = 0
    while True:
        r = (np.pi / 2 + n * np.pi) / K
        if r > LIM * 1.05:
            break
        nodes.append(r)
        n += 1
    return nodes


# ─────────────────────────────────────────────────────────
#  FIGURE  &  3-D AXES
# ─────────────────────────────────────────────────────────
FIG = plt.figure(figsize=(10, 10), facecolor=BG)
FIG.subplots_adjust(left=0, right=1, top=1, bottom=0)

AX = FIG.add_axes([0.02, 0.06, 0.96, 0.86], projection="3d")
AX.set_facecolor(BG)
AX.set_xlim(-LIM, LIM)
AX.set_ylim(-LIM, LIM)
AX.set_zlim(-Z_LIM, Z_LIM)

for axis in (AX.xaxis, AX.yaxis, AX.zaxis):
    axis.pane.fill = False
    axis.pane.set_edgecolor(BG)
AX.grid(False)
AX.set_xticks([])
AX.set_yticks([])
AX.set_zticks([])
AX.set_proj_type("persp")
AX.view_init(elev=_ELEV, azim=_AZ0)

# Surface container
SURF = [None]

# Node ring overlays — violet, permanently at z = 0
_NODE_R = node_radii()
NODE_RINGS = [AX.plot([], [], [], lw=1.8, color=VIOLET, alpha=0)[0]
              for _ in _NODE_R]

# Source dot
SRC_DOT, = AX.plot([], [], [], "o", color=WHITE, ms=10, zorder=10)

# ─────────────────────────────────────────────────────────
#  TEXT OVERLAYS
# ─────────────────────────────────────────────────────────
_stroke = [pe.withStroke(linewidth=3, foreground=BG)]

T_TITLE = FIG.text(
    0.5, 0.975,
    "Standing Wave — Pulsating 3-D Rings",
    ha="center", va="top",
    color=RED, fontsize=20, fontweight="bold",
    path_effects=_stroke,
)
T_SUB = FIG.text(
    0.5, 0.925,
    "u(r,t) = 2·cos(k·r)·cos(ω·t)·e^(−αr)/√r     |     node rings fixed at z = 0",
    ha="center", va="top",
    color=TEXT, fontsize=11,
    path_effects=_stroke,
)
T_EQ = FIG.text(
    0.5, 0.052,
    f"λ = {WAVELENGTH:.1f}   v = {WAVE_SPEED:.1f}   f = {FREQ:.2f} Hz   T = {PERIOD:.2f} s"
    f"   nodes at  r_n = (2n+1)·λ/4",
    ha="center", va="bottom",
    color=ORANGE, fontsize=10,
    path_effects=_stroke,
)
T_NOTE = FIG.text(
    0.5, 0.020,
    "Violet rings = permanent node circles (z = 0 always)  |  "
    "Surface between them breathes ±max",
    ha="center", va="bottom",
    color=INDIGO, fontsize=9.5, style="italic",
    path_effects=_stroke,
)

# Live readout: phase of the oscillation
T_TIME = FIG.text(
    0.04, 0.88, "",
    ha="left", va="top",
    color=TEXT, fontsize=9.5,
    path_effects=_stroke,
)


# ─────────────────────────────────────────────────────────
#  HELPER: rebuild surface
# ─────────────────────────────────────────────────────────
def _set_surface(U):
    if SURF[0] is not None:
        SURF[0].remove()
    SURF[0] = AX.plot_surface(
        XX, YY, U,
        cmap=WAVE_CMAP, vmin=-1.2, vmax=1.2,
        alpha=0.90,
        antialiased=False,
        linewidth=0,
        rcount=GRID_N, ccount=GRID_N,
    )


# ─────────────────────────────────────────────────────────
#  ANIMATION UPDATE
# ─────────────────────────────────────────────────────────
def update(frame):
    t     = frame / FPS
    pulse = np.cos(OMEGA * t)   # −1 … +1

    # ── standing wave surface ────────────────────────────
    U = u_standing(t)
    _set_surface(U)

    # ── node rings: always at z = 0, brighten near zero-crossing ──
    # Node rings are most visible when the antinodes collapse (pulse ≈ 0)
    node_alpha = 0.35 + 0.55 * (1.0 - abs(pulse))
    for ring, r_node in zip(NODE_RINGS, _NODE_R):
        ring.set_data(r_node * np.cos(_THETA), r_node * np.sin(_THETA))
        ring.set_3d_properties(np.zeros(len(_THETA)))
        ring.set_alpha(node_alpha)

    # ── source dot ────────────────────────────────────────
    src_pulse = abs(pulse)
    SRC_DOT.set_data([0], [0])
    SRC_DOT.set_3d_properties([0.0])
    SRC_DOT.set_markersize(6 + 14 * src_pulse)
    SRC_DOT.set_alpha(0.55 + 0.45 * src_pulse)

    # ── slow camera orbit ─────────────────────────────────
    azim = _AZ0 + frame * ORBIT_SPEED
    elev = _ELEV + 6.0 * np.sin(2 * np.pi * frame / TOTAL_FRAMES)
    AX.view_init(elev=elev, azim=azim)

    # ── live phase readout ────────────────────────────────
    phase_deg = (OMEGA * t % (2 * np.pi)) * 180 / np.pi
    T_TIME.set_text(
        f"t = {t:.2f} s\n"
        f"ω·t = {phase_deg:.0f}°\n"
        f"cos(ω·t) = {pulse:+.2f}\n"
        f"nodes: {len(_NODE_R)}"
    )

    return []


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Standing Wave — Pulsating 3-D Rings")
    print(f"  Grid   : {GRID_N}×{GRID_N}")
    print(f"  Frames : {TOTAL_FRAMES}  ({TOTAL_FRAMES / FPS:.1f} s @ {FPS} fps)")
    print(f"  λ={WAVELENGTH}  v={WAVE_SPEED}  f={FREQ:.3f} Hz  T={PERIOD:.3f} s")
    print(f"  Node rings: {len(_NODE_R)} at radii {[f'{r:.2f}' for r in _NODE_R]}")
    print("  Rendering … (orbiting camera, ~60–90 s)")

    ani = FuncAnimation(
        FIG, update,
        frames=TOTAL_FRAMES,
        interval=1000 // FPS,
        blit=False,
    )

    OUT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "standing_wave_rings_3d.gif",
    )
    ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
    print(f"  Saved  → {OUT}")
    plt.close(FIG)
