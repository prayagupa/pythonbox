#!/usr/bin/env python3
"""
Pulsating Rings & Radiating Waves — Title Splash (3-D)
═══════════════════════════════════════════════════════
A standalone 3-D title card animation that fades in over a gently
expanding wave surface, with teaser ring overlays emerging from the
surface as the title text and credits appear.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WHAT YOU SEE:
  • A slow-moving cylindrical wave surface (run at 0.65× speed)
    fades in from black — the 3-D ridge-and-valley landscape
    of a single pulsating source.
  • Indigo teaser rings rise from the surface, tracing the
    analytic crest positions  r_n = v·t − n·λ.
  • Title, subtitle, and credit line fade in smoothly.
  • The camera holds a fixed oblique view so the 3-D depth is
    immediately apparent.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Huygens  1678  •  Young  1801  •  v = λ · f

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
VIOLET = "#cc44ff"
INDIGO = "#5566ff"   # teaser ring colour
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
TOTAL_FRAMES = 70           # 3.5 s — long enough for a clean fade-in hold
TIME_SCALE   = 0.65         # slow the wave so the surface feels calm

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

# Fixed camera — no orbit on the title card
_AZ0  = -60.0
_ELEV = 38.0


# ─────────────────────────────────────────────────────────
#  WAVE FUNCTIONS
# ─────────────────────────────────────────────────────────
def _R_grid():
    """Softened radial distance from the origin."""
    return np.sqrt(XX ** 2 + YY ** 2) + 0.25


def u_single(t):
    """
    Outgoing cylindrical wave:
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r
    Run at TIME_SCALE speed so the surface evolves slowly on the title card.
    """
    R = _R_grid()
    return np.cos(K * R - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R)


def crest_radii(t, n_max=N_RINGS):
    """
    Analytic crest-ring radii:  r_n = v·t − n·λ  (outermost first).
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
    """Surface displacement at crest ring radius r."""
    R = r + 0.25
    return float(np.cos(K * r - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R))


# ─────────────────────────────────────────────────────────
#  FADE HELPER
# ─────────────────────────────────────────────────────────
def fade_in(frame, total, delay=0.0, speed=5.0):
    """Smooth 0 → 1 fade starting at `delay` fraction of the animation."""
    t = frame / max(total - 1, 1)
    return float(np.clip((t - delay) * speed, 0.0, 1.0))


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

# Teaser ring overlays — indigo, ride the (scaled) surface
RINGS = [AX.plot([], [], [], lw=1.6, color=INDIGO, alpha=0)[0]
         for _ in range(N_RINGS)]

# ─────────────────────────────────────────────────────────
#  TEXT OVERLAYS
# ─────────────────────────────────────────────────────────
_stroke = [pe.withStroke(linewidth=3, foreground=BG)]

T_TITLE = FIG.text(
    0.5, 0.975,
    "Pulsating Rings\n& Radiating Waves",
    ha="center", va="top",
    color=RED, fontsize=26, fontweight="bold",
    linespacing=1.4,
    path_effects=_stroke,
)
T_SUB = FIG.text(
    0.5, 0.900,
    "3-D view: vertical axis = displacement amplitude",
    ha="center", va="top",
    color=TEXT, fontsize=12,
    path_effects=_stroke,
)
T_NOTE = FIG.text(
    0.5, 0.025,
    "Huygens  1678  •  Young  1801  •  v = λ · f",
    ha="center", va="bottom",
    color=INDIGO, fontsize=10, style="italic",
    path_effects=_stroke,
)
T_EQ = FIG.text(
    0.5, 0.055,
    f"λ = {WAVELENGTH:.1f}   v = {WAVE_SPEED:.1f}   f = {FREQ:.2f} Hz   T = {PERIOD:.2f} s",
    ha="center", va="bottom",
    color=ORANGE, fontsize=10,
    path_effects=_stroke,
)

# Initialise all text as invisible — faded in during update()
for txt in (T_TITLE, T_SUB, T_NOTE, T_EQ):
    txt.set_alpha(0)


# ─────────────────────────────────────────────────────────
#  HELPER: rebuild surface
# ─────────────────────────────────────────────────────────
def _set_surface(U, alpha):
    if SURF[0] is not None:
        SURF[0].remove()
    a = float(np.clip(alpha, 0.02, 1.0))
    SURF[0] = AX.plot_surface(
        XX, YY, U,
        cmap=WAVE_CMAP, vmin=-1.2, vmax=1.2,
        alpha=a,
        antialiased=False,
        linewidth=0,
        rcount=GRID_N, ccount=GRID_N,
    )


# ─────────────────────────────────────────────────────────
#  ANIMATION UPDATE
# ─────────────────────────────────────────────────────────
def update(frame):
    f      = fade_in(frame, TOTAL_FRAMES, delay=0.0, speed=4.0)
    t_slow = frame / FPS * TIME_SCALE

    # ── wave surface fades in ─────────────────────────────
    U = u_single(t_slow) * 0.55   # scale amplitude for a calm title look
    _set_surface(U, alpha=max(0.02, f * 0.72))

    # ── teaser rings rise with the surface ────────────────
    radii = crest_radii(t_slow)
    total = max(len(radii), 1)
    for i, ring in enumerate(RINGS):
        if i < len(radii):
            r     = radii[i]
            alpha = f * 0.45 * (i + 1) / total
            rz    = np.full(len(_THETA), ring_height(r, t_slow) * 0.55)
            ring.set_data(r * np.cos(_THETA), r * np.sin(_THETA))
            ring.set_3d_properties(rz)
            ring.set_alpha(alpha)
        else:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)

    # ── text fades in at staggered delays ────────────────
    T_TITLE.set_alpha(f)
    T_SUB.set_alpha(fade_in(frame, TOTAL_FRAMES, delay=0.15, speed=4.5) * 0.90)
    T_EQ.set_alpha(fade_in(frame, TOTAL_FRAMES, delay=0.30, speed=4.5) * 0.85)
    T_NOTE.set_alpha(fade_in(frame, TOTAL_FRAMES, delay=0.45, speed=4.5) * 0.75)

    return []


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Pulsating Rings & Radiating Waves — Title Splash (3-D)")
    print(f"  Grid   : {GRID_N}×{GRID_N}")
    print(f"  Frames : {TOTAL_FRAMES}  ({TOTAL_FRAMES / FPS:.1f} s @ {FPS} fps)")
    print(f"  λ={WAVELENGTH}  v={WAVE_SPEED}  f={FREQ:.3f} Hz  T={PERIOD:.3f} s")
    print("  Rendering … (~30–60 s)")

    ani = FuncAnimation(
        FIG, update,
        frames=TOTAL_FRAMES,
        interval=1000 // FPS,
        blit=False,
    )

    OUT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pulsating_rings_title_splash_3d.gif",
    )
    ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
    print(f"  Saved  → {OUT}")
    plt.close(FIG)
