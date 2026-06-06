#!/usr/bin/env python3
"""
Two-Source Interference — 3-D Surface Animation
════════════════════════════════════════════════
A focused 3-D visualization of the interference pattern produced by two
coherent point sources pulsating in phase.  The vertical (Z) axis encodes
displacement amplitude: tall peaks mark constructive interference where
two crests coincide; flat lanes mark destructive interference where a
crest meets a trough.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  KEY PHYSICS:
  • Each source emits a cylindrical outgoing wave:
        u_i(r_i, t) = cos(k·r_i − ω·t) · exp(−α·r_i) / √r_i
  • The total displacement is the linear superposition:
        u(x, y, t) = u_A(r_A, t) + u_B(r_B, t)
  • Constructive interference (tall peaks / deep valleys):
        |r_A − r_B| = 0, λ, 2λ, …   (path difference = integer wavelengths)
  • Destructive interference (flat lanes at z ≈ 0):
        |r_A − r_B| = λ/2, 3λ/2, …  (path difference = half-integer wavelengths)
  • This is exactly the physics of Young's double-slit experiment (1801).
  • A slow camera orbit reveals the 3-D fringe landscape from all angles.
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
VIOLET = "#cc44ff"   # S₁ ring colour
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

# Source positions (symmetric about the origin)
SRC_A = np.array([-1.6, 0.0])
SRC_B = np.array([+1.6, 0.0])
SOURCE_SEP = SRC_B[0] - SRC_A[0]     # 2d = 3.2 units

_THETA  = np.linspace(0, 2 * np.pi, 180)
Z_LIM   = 1.8
N_RINGS = 5      # ring slots per source

# Camera start
_AZ0  = -55.0
_ELEV = 40.0


# ─────────────────────────────────────────────────────────
#  WAVE FUNCTIONS
# ─────────────────────────────────────────────────────────
def _R(cx, cy):
    """Softened radial distance from source (cx, cy) over the grid."""
    return np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2) + 0.25


def u_source(t, cx, cy):
    """
    Outgoing cylindrical wave from source at (cx, cy):
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r
    """
    R = _R(cx, cy)
    return np.cos(K * R - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R)


def u_total(t):
    """Linear superposition of both sources — the interference pattern."""
    return u_source(t, *SRC_A) + u_source(t, *SRC_B)


def crest_radii(t, n_max=N_RINGS):
    """Analytic crest-ring radii at time t: r_n = v·t − n·λ (outermost first)."""
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


def ring_height(r, t, cx, cy):
    """Surface height of source (cx,cy) at its crest ring radius r."""
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

# Surface container
SURF = [None]

# Ring overlays: N_RINGS slots for S₁ (violet) + N_RINGS slots for S₂ (orange)
RINGS_A = [AX.plot([], [], [], lw=1.8, color=VIOLET, alpha=0)[0]
           for _ in range(N_RINGS)]
RINGS_B = [AX.plot([], [], [], lw=1.8, color=ORANGE, alpha=0)[0]
           for _ in range(N_RINGS)]

# Source dots
DOT_A, = AX.plot([], [], [], "o", color=VIOLET, ms=11, zorder=10)
DOT_B, = AX.plot([], [], [], "o", color=ORANGE, ms=11, zorder=10)

# ─────────────────────────────────────────────────────────
#  TEXT OVERLAYS
# ─────────────────────────────────────────────────────────
_stroke = [pe.withStroke(linewidth=3, foreground=BG)]

T_TITLE = FIG.text(
    0.5, 0.975,
    "Two-Source Interference — 3-D",
    ha="center", va="top",
    color=RED, fontsize=20, fontweight="bold",
    path_effects=_stroke,
)
T_SUB = FIG.text(
    0.5, 0.925,
    "u = u_S₁ + u_S₂     |     "
    "tall peaks = constructive  |  flat lanes = destructive",
    ha="center", va="top",
    color=TEXT, fontsize=11,
    path_effects=_stroke,
)
T_EQ = FIG.text(
    0.5, 0.052,
    f"λ = {WAVELENGTH:.1f}   v = {WAVE_SPEED:.1f}   f = {FREQ:.2f} Hz   "
    f"source sep 2d = {SOURCE_SEP:.1f}   "
    f"constructive: |r_A−r_B| = n·λ",
    ha="center", va="bottom",
    color=ORANGE, fontsize=10,
    path_effects=_stroke,
)
T_NOTE = FIG.text(
    0.5, 0.020,
    "Violet rings = S₁ wavefronts  |  Orange rings = S₂ wavefronts  |  "
    "Same physics as Young's double-slit (1801)",
    ha="center", va="bottom",
    color=INDIGO, fontsize=9.5, style="italic",
    path_effects=_stroke,
)

# Source labels that follow the dots (placed once, positions are fixed)
LBL_A = AX.text(SRC_A[0], SRC_A[1] - 0.8, -Z_LIM * 0.85,
                "S₁", color=VIOLET, fontsize=13, fontweight="bold",
                ha="center")
LBL_B = AX.text(SRC_B[0], SRC_B[1] - 0.8, -Z_LIM * 0.85,
                "S₂", color=ORANGE, fontsize=13, fontweight="bold",
                ha="center")

# Live readout
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
        cmap=WAVE_CMAP, vmin=-1.6, vmax=1.6,
        alpha=0.90,
        antialiased=False,
        linewidth=0,
        rcount=GRID_N, ccount=GRID_N,
    )


def _update_rings(rings, cx, cy, radii, t):
    """Place ring overlays for one source onto the superposed surface height."""
    total = max(len(radii), 1)
    for i, ring in enumerate(rings):
        if i < len(radii):
            r     = radii[i]
            alpha = 0.30 + 0.65 * (i + 1) / total
            rz    = np.full(len(_THETA), ring_height(r, t, cx, cy))
            ring.set_data(cx + r * np.cos(_THETA), cy + r * np.sin(_THETA))
            ring.set_3d_properties(rz)
            ring.set_alpha(alpha)
        else:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)


# ─────────────────────────────────────────────────────────
#  ANIMATION UPDATE
# ─────────────────────────────────────────────────────────
def update(frame):
    t = frame / FPS

    # ── superposed wave surface ───────────────────────────
    U = u_total(t)
    _set_surface(U)

    # ── ring overlays for each source ─────────────────────
    radii = crest_radii(t)
    _update_rings(RINGS_A, *SRC_A, radii, t)
    _update_rings(RINGS_B, *SRC_B, radii, t)

    # ── source dots pulsate ───────────────────────────────
    pulse = 0.5 + 0.5 * np.cos(OMEGA * t)
    for dot, src in ((DOT_A, SRC_A), (DOT_B, SRC_B)):
        dot.set_data([src[0]], [src[1]])
        dot.set_3d_properties([0.0])
        dot.set_markersize(7 + 9 * pulse)
        dot.set_alpha(1.0)

    # ── slow camera orbit ─────────────────────────────────
    azim = _AZ0 + frame * ORBIT_SPEED
    elev = _ELEV + 6.0 * np.sin(2 * np.pi * frame / TOTAL_FRAMES)
    AX.view_init(elev=elev, azim=azim)

    # ── live readout ──────────────────────────────────────
    T_TIME.set_text(
        f"t = {t:.2f} s\n"
        f"rings/source: {len(radii)}\n"
        f"2d/λ = {SOURCE_SEP / WAVELENGTH:.2f}"
    )

    return []


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Two-Source Interference — 3-D Surface")
    print(f"  Grid        : {GRID_N}×{GRID_N}")
    print(f"  Frames      : {TOTAL_FRAMES}  ({TOTAL_FRAMES / FPS:.1f} s @ {FPS} fps)")
    print(f"  λ={WAVELENGTH}  v={WAVE_SPEED}  f={FREQ:.3f} Hz  T={PERIOD:.3f} s")
    print(f"  Source sep  : 2d = {SOURCE_SEP:.1f}  ({SOURCE_SEP/WAVELENGTH:.2f} λ)")
    print("  Rendering … (orbiting camera, ~60–90 s)")

    ani = FuncAnimation(
        FIG, update,
        frames=TOTAL_FRAMES,
        interval=1000 // FPS,
        blit=False,
    )

    OUT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "two_source_interference_3d.gif",
    )
    ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
    print(f"  Saved  → {OUT}")
    plt.close(FIG)
