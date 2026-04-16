#!/usr/bin/env python3
"""
Ridge Peaks Radiating Outward at Wave Speed — 3-D Surface Animation
════════════════════════════════════════════════════════════════════
A focused 3-D visualization of a single pulsating point source sending
concentric ridge-peaks outward across a surface.  The vertical (Z) axis
encodes displacement amplitude: crests rise as ridges, troughs sink as
valleys, and the whole pattern marches outward at the wave speed v = λ·f.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KEY PHYSICS:
  • Cylindrical wave from a point source in 2-D:
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r
  • Each ridge crest satisfies  k·r − ω·t = 2π·n
    → the n-th crest is located at  r_n(t) = v·t − n·λ
  • Ridge height decays as 1/√r — energy spreads over a
    growing circumference (cylindrical spreading law).
  • The camera slowly orbits, revealing the 3-D depth of the
    concentric ridge pattern.
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
RED    = "#ff2244"   # crest ridge highlight colour
ORANGE = "#ff8833"   # equation / label colour
VIOLET = "#cc44ff"   # ring overlay colour
INDIGO = "#5566ff"   # note / accent colour
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
TOTAL_FRAMES = 120          # 6 s  — enough for ~3 full orbits of the wave
ORBIT_SPEED  = 0.6          # degrees of azimuth rotation per frame

# ─────────────────────────────────────────────────────────
#  SPATIAL GRID  (80×80 for smooth surface at good performance)
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
DAMPING    = 0.055                     # gentle spatial decay

_THETA = np.linspace(0, 2 * np.pi, 180)   # ring overlay angles
Z_LIM  = 1.6                              # vertical axis half-range
N_RINGS = 10                              # max concurrent ridge rings

# Starting camera azimuth
_AZ0   = -55.0
_ELEV  = 42.0

# ─────────────────────────────────────────────────────────
#  WAVE FUNCTIONS
# ─────────────────────────────────────────────────────────
def _R_grid():
    """Softened radial distance from the origin — avoids 1/0 at source."""
    return np.sqrt(XX ** 2 + YY ** 2) + 0.25


def u_wave(t):
    """
    Outgoing cylindrical wave:
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r

    Returns the 2-D displacement array  Z = u(x, y, t).
    The ridge crests march outward at  v = ω / k.
    Height decays as 1/√r so total energy in each ring is conserved.
    """
    R = _R_grid()
    return np.cos(K * R - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R)


def crest_radii(t, n_max=N_RINGS):
    """
    Analytic positions of ridge-crest rings at time t.
    Crest condition:  k·r − ω·t = 2π·n  →  r_n = v·t − n·λ
    Returns radii outermost-first (oldest ring first).
    """
    base   = WAVE_SPEED * t
    radii  = []
    m      = 0
    while m < 2000:
        r = base - m * WAVELENGTH
        if r < 0.05:
            break
        if r <= LIM * 1.05:
            radii.append(r)
        m += 1
    return radii[:n_max]


def ring_height(r, t):
    """Surface height at crest ring radius r at time t."""
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

# Dark, minimal pane style
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

# Ring overlay lines
RINGS = [AX.plot([], [], [], lw=1.8, color=RED, alpha=0)[0]
         for _ in range(N_RINGS)]

# Source dot — pulsates at the origin
SRC_DOT, = AX.plot([], [], [], "o", color=WHITE, ms=10, zorder=10)

# ─────────────────────────────────────────────────────────
#  TEXT OVERLAYS
# ─────────────────────────────────────────────────────────
_stroke = [pe.withStroke(linewidth=3, foreground=BG)]

T_TITLE = FIG.text(
    0.5, 0.975,
    "Ridge Peaks Radiating at Wave Speed",
    ha="center", va="top",
    color=RED, fontsize=20, fontweight="bold",
    path_effects=_stroke,
)
T_SUB = FIG.text(
    0.5, 0.925,
    "u(r,t) = cos(k·r − ω·t) · e^(−αr) / √r     |     ridge height ∝ 1/√r",
    ha="center", va="top",
    color=TEXT, fontsize=11,
    path_effects=_stroke,
)
T_EQ = FIG.text(
    0.5, 0.052,
    f"λ = {WAVELENGTH:.1f}   v = {WAVE_SPEED:.1f}   f = {FREQ:.2f} Hz   T = {PERIOD:.2f} s   "
    f"k = {K:.2f}   ω = {OMEGA:.2f}",
    ha="center", va="bottom",
    color=ORANGE, fontsize=10,
    path_effects=_stroke,
)
T_NOTE = FIG.text(
    0.5, 0.020,
    "Peak ridge = crest  |  Valley = trough  |  Red rings mark analytic crest positions",
    ha="center", va="bottom",
    color=INDIGO, fontsize=9.5, style="italic",
    path_effects=_stroke,
)

# Live readout: current wave time and outermost crest radius
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
    U = u_wave(t)
    _set_surface(U)

    # ── crest ring overlays ───────────────────────────────
    radii = crest_radii(t)
    total = max(len(radii), 1)
    for i, ring in enumerate(RINGS):
        if i < len(radii):
            r     = radii[i]
            alpha = 0.30 + 0.65 * (i + 1) / total   # innermost = brightest
            rz    = np.full(len(_THETA), ring_height(r, t))
            ring.set_data(r * np.cos(_THETA), r * np.sin(_THETA))
            ring.set_3d_properties(rz)
            ring.set_alpha(alpha)
        else:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)

    # ── source pulsation ──────────────────────────────────
    pulse = 0.5 + 0.5 * np.cos(OMEGA * t)
    SRC_DOT.set_data([0], [0])
    SRC_DOT.set_3d_properties([0.0])
    SRC_DOT.set_markersize(6 + 12 * pulse)
    SRC_DOT.set_alpha(0.65 + 0.35 * pulse)

    # ── slow camera orbit ─────────────────────────────────
    # Azimuth rotates at ORBIT_SPEED deg/frame; elevation gently bobs ±5°
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
    print("Ridge Peaks Radiating at Wave Speed — 3-D Surface")
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
        "ridge_wave_propagation.gif",
    )
    ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
    print(f"  Saved  → {OUT}")
    plt.close(FIG)
