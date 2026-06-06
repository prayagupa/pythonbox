#!/usr/bin/env python3
"""
Single Pulsating Source — 3-D Expanding Rings
══════════════════════════════════════════════
A focused 3-D visualization of a single vibrating point source radiating
concentric cylindrical wavefronts.  The vertical (Z) axis encodes
displacement: ridge peaks are crests, valleys are troughs, and the whole
pattern marches outward at the wave speed  v = λ · f.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KEY PHYSICS  (Huygens, 1678):
  • Outgoing cylindrical wave from a point source:
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r
  • Each red ring marks one wavefront crest, expanding at
    wave speed  v = ω / k = λ · f.
  • Crest positions (analytic):  r_n(t) = v·t − n·λ
  • Ridge height decays as 1/√r — cylindrical spreading law:
    the same energy is distributed over a growing circumference.
  • The source dot pulsates at frequency f, showing the oscillation
    that drives the outgoing wavefronts.
  • A slow camera orbit reveals the 3-D ridge-and-valley topology.
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
RED    = "#ff2244"   # wavefront ring colour
ORANGE = "#ff8833"   # equation colour
VIOLET = "#cc44ff"   # accent
INDIGO = "#5566ff"   # note colour
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
TOTAL_FRAMES = 120          # 6 s
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
Z_LIM   = 1.6
N_RINGS = 10

# Camera start
_AZ0  = -55.0
_ELEV = 42.0


# ─────────────────────────────────────────────────────────
#  WAVE FUNCTIONS
# ─────────────────────────────────────────────────────────
def _R_grid():
    """Softened radial distance from the origin — avoids 1/0 at the source."""
    return np.sqrt(XX ** 2 + YY ** 2) + 0.25


def u_single(t):
    """
    Outgoing cylindrical wave from origin:
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r

    Surface height = displacement amplitude.
    Crests (ridges) satisfy  k·r − ω·t = 2π·n  →  r_n = v·t − n·λ.
    """
    R = _R_grid()
    return np.cos(K * R - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R)


def crest_radii(t, n_max=N_RINGS):
    """
    Analytic crest-ring radii at time t.
    Crest condition:  k·r − ω·t = 2π·n  →  r_n = v·t − n·λ
    Returns up to n_max radii, outermost (oldest) first.
    """
    base  = WAVE_SPEED * t
    radii = []
    m     = 0
    while m < 2000:
        r = base - m * WAVELENGTH
        if r < 0.05:
            break
        if r <= LIM * 1.05:
            radii.append(r)
        m += 1
    return radii[:n_max]


def ring_height(r, t):
    """Displacement at crest ring radius r at time t."""
    R = r + 0.25
    return float(np.cos(K * r - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R))


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

# Surface container (replaced every frame)
SURF = [None]

# Wavefront ring overlays — red curves sitting on the surface
RINGS = [AX.plot([], [], [], lw=1.8, color=RED, alpha=0)[0]
         for _ in range(N_RINGS)]

# Pulsating source dot at the origin
SRC_DOT, = AX.plot([], [], [], "o", color=WHITE, ms=10, zorder=10)

# ─────────────────────────────────────────────────────────
#  TEXT OVERLAYS
# ─────────────────────────────────────────────────────────
_stroke = [pe.withStroke(linewidth=3, foreground=BG)]

T_TITLE = FIG.text(
    0.5, 0.975,
    "Single Pulsating Source — 3-D",
    ha="center", va="top",
    color=RED, fontsize=20, fontweight="bold",
    path_effects=_stroke,
)
T_SUB = FIG.text(
    0.5, 0.925,
    "u(r,t) = cos(k·r − ω·t) · e^(−αr) / √r     |     "
    "each red ring = one wavefront crest",
    ha="center", va="top",
    color=TEXT, fontsize=11,
    path_effects=_stroke,
)
T_EQ = FIG.text(
    0.5, 0.052,
    f"λ = {WAVELENGTH:.1f}   v = {WAVE_SPEED:.1f}   f = {FREQ:.2f} Hz   "
    f"T = {PERIOD:.2f} s   k = {K:.2f}   ω = {OMEGA:.2f}",
    ha="center", va="bottom",
    color=ORANGE, fontsize=10,
    path_effects=_stroke,
)
T_NOTE = FIG.text(
    0.5, 0.020,
    "Peak ridge = crest  |  Valley = trough  |  "
    "Ridge height ∝ 1/√r  (cylindrical spreading)  |  "
    "Crest speed = v = λ·f",
    ha="center", va="bottom",
    color=INDIGO, fontsize=9.5, style="italic",
    path_effects=_stroke,
)

# Live readout: wave time, leading crest, rings visible
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
    t = frame / FPS

    # ── wave surface ──────────────────────────────────────
    U = u_single(t)
    _set_surface(U)

    # ── crest ring overlays on the surface ────────────────
    radii = crest_radii(t)
    total = max(len(radii), 1)
    for i, ring in enumerate(RINGS):
        if i < len(radii):
            r     = radii[i]
            # innermost ring (newest) is brightest; outermost (oldest) is dimmest
            alpha = 0.25 + 0.70 * (i + 1) / total
            rz    = np.full(len(_THETA), ring_height(r, t))
            ring.set_data(r * np.cos(_THETA), r * np.sin(_THETA))
            ring.set_3d_properties(rz)
            ring.set_alpha(alpha)
        else:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)

    # ── source dot pulsates at ω ──────────────────────────
    pulse = 0.5 + 0.5 * np.cos(OMEGA * t)
    SRC_DOT.set_data([0], [0])
    SRC_DOT.set_3d_properties([0.0])
    SRC_DOT.set_markersize(7 + 12 * pulse)
    SRC_DOT.set_color(WHITE)
    SRC_DOT.set_alpha(0.65 + 0.35 * pulse)

    # ── slow camera orbit ─────────────────────────────────
    azim = _AZ0 + frame * ORBIT_SPEED
    elev = _ELEV + 5.0 * np.sin(2 * np.pi * frame / TOTAL_FRAMES)
    AX.view_init(elev=elev, azim=azim)

    # ── live readout ──────────────────────────────────────
    r_front = radii[0] if radii else 0.0
    T_TIME.set_text(
        f"t = {t:.2f} s\n"
        f"leading crest  r = {r_front:.2f}\n"
        f"rings visible  {len(radii)}"
    )

    return []


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Single Pulsating Source — 3-D Expanding Rings")
    print(f"  Grid   : {GRID_N}×{GRID_N}")
    print(f"  Frames : {TOTAL_FRAMES}  ({TOTAL_FRAMES / FPS:.1f} s @ {FPS} fps)")
    print(f"  λ={WAVELENGTH}  v={WAVE_SPEED}  f={FREQ:.3f} Hz  T={PERIOD:.3f} s")
    print("  Rendering … (orbiting camera, ~60–90 s)")

    ani = FuncAnimation(
        FIG, update,
        frames=TOTAL_FRAMES,
        interval=1000 // FPS,
        blit=False,
    )

    OUT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "single_pulsating_source_3d.gif",
    )
    ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
    print(f"  Saved  → {OUT}")
    plt.close(FIG)
