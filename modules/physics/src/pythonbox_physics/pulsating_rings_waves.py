#!/usr/bin/env python3
"""
Pulsating Concentric Rings & Radiating Waves — 3-D Surface
═══════════════════════════════════════════════════════════
An educational 3-D visualization of wave propagation from point sources.
The vertical (Z) axis represents displacement amplitude; wavefronts appear
as concentric ridges that expand outward, decay with distance, and interfere.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE BIG IDEA (Huygens 1678 / Young 1801):
  A vibrating point source sends out CIRCULAR WAVEFRONTS in all
  directions.  In 3-D the surface height encodes displacement:
  crests are peaks, troughs are valleys, nodes are at z = 0.
  Amplitude weakens as 1/√r (cylindrical spreading in 2-D).
  Two sources create vivid interference fringes — exactly the
  physics behind Young's double-slit experiment.  Outgoing +
  reflected waves superpose into a STANDING WAVE: nodes are
  fixed rings at z = 0; antinodes pulse in place.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Scene 0 — Title splash (teaser surface at low opacity)
  Scene 1 — Single pulsating source: 3-D expanding ridges
  Scene 2 — Two-source interference: 3-D fringe pattern
  Scene 3 — Standing wave: pulsating 3-D surface, nodes at z = 0
  Scene 4 — Key Takeaways

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
#  COLOUR PALETTE  (red / orange / violet / indigo)
# ─────────────────────────────────────────────────────────
BG     = "#03030e"
TEXT   = "#dde8ff"
RED    = "#ff2244"   # bright scarlet-red  — primary ring / crest colour
ORANGE = "#ff8833"   # warm orange         — secondary source / equations
VIOLET = "#cc44ff"   # vivid violet        — interference / standing-wave rings
INDIGO = "#5566ff"   # deep indigo-blue    — notes / accent
WHITE  = "#ffffff"

# ─────────────────────────────────────────────────────────
#  WAVE COLORMAP  (deep-trough → zero → bright-crest)
# ─────────────────────────────────────────────────────────
WAVE_CMAP = LinearSegmentedColormap.from_list(
    "wave_deep",
    ["#0a0025", "#2200aa", BG, VIOLET, RED, WHITE],
    N=256,
)

# ─────────────────────────────────────────────────────────
#  TIMING
# ─────────────────────────────────────────────────────────
FPS          = 20
SCENE_FRAMES = [35, 80, 80, 75, 40]
CUMULATIVE   = list(np.cumsum([0] + SCENE_FRAMES))
TOTAL_FRAMES = sum(SCENE_FRAMES)

# ─────────────────────────────────────────────────────────
#  GRID  (reduced resolution for 3-D surface performance)
# ─────────────────────────────────────────────────────────
GRID_N = 80           # grid points per axis (80×80 surface quads)
LIM    = 5.0          # half-width of displayed region (arbitrary units)
_grid  = np.linspace(-LIM, LIM, GRID_N)
XX, YY = np.meshgrid(_grid, _grid)

# ─────────────────────────────────────────────────────────
#  WAVE PARAMETERS
# ─────────────────────────────────────────────────────────
WAVELENGTH = 1.5                      # λ  (spatial units)
K          = 2 * np.pi / WAVELENGTH   # wave-number  k = 2π/λ
WAVE_SPEED = 2.5                      # v  (units / s)
OMEGA      = WAVE_SPEED * K           # angular frequency  ω = v·k
PERIOD     = 2 * np.pi / OMEGA        # T = 2π/ω
FREQ       = OMEGA / (2 * np.pi)      # f = ω/(2π)
DAMPING    = 0.060                    # spatial exponential decay  (1/e ≈ 17 units)

SRC_A = np.array([-1.6, 0.0])        # left source  (Scene 2)
SRC_B = np.array([+1.6, 0.0])        # right source (Scene 2)

_THETA = np.linspace(0, 2 * np.pi, 120)   # ring drawing angles
Z_LIM  = 1.8                              # vertical axis half-range

# ─────────────────────────────────────────────────────────
#  WAVE FIELD FUNCTIONS
# ─────────────────────────────────────────────────────────
def _R(cx=0.0, cy=0.0):
    """Softened radial distance from (cx, cy) — avoids 1/0 at the source."""
    return np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2) + 0.25


def u_single(t, cx=0.0, cy=0.0):
    """
    Outgoing circular wave from source at (cx, cy):
        u(r, t) = cos(k·r − ω·t) · exp(−α·r) / √r
    Surface height = displacement amplitude.
    The 1/√r factor models energy conservation in 2-D (cylindrical spreading).
    """
    R = _R(cx, cy)
    return np.cos(K * R - OMEGA * t) * np.exp(-DAMPING * R) / np.sqrt(R)


def u_two_source(t):
    """
    Linear superposition of two outgoing waves from SRC_A and SRC_B.
    Tall 3-D peaks where crests reinforce; flat lanes where crest meets trough.
    """
    return u_single(t, *SRC_A) + u_single(t, *SRC_B)


def u_standing(t):
    """
    Standing wave: superpose outgoing + reflected wave.
        outgoing:  cos(k·r − ω·t)
        reflected: cos(k·r + ω·t)
        sum:       2·cos(k·r)·cos(ω·t)
    The entire surface breathes uniformly in/out; node rings stay at z = 0.
    """
    R   = _R()
    amp = 2.0 * np.cos(K * R) * np.exp(-DAMPING * R) / np.sqrt(R)
    return amp * np.cos(OMEGA * t)


# ─────────────────────────────────────────────────────────
#  WAVEFRONT CREST RADII  at time t
# ─────────────────────────────────────────────────────────
def crest_radii(t, n_rings=8):
    """
    Positions of outgoing wavefront crests at time t.
    Crest condition:  k·R − ω·t = 2π·n  →  R = v·t − m·λ  (m = 0, 1, 2, …)

    The ring born most recently (m=0) is closest to the source
    and has the largest amplitude; older rings are dimmer.
    Returns up to n_rings radii in descending order (outermost first).
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
    return radii[:n_rings]   # outermost (oldest) first


def _ring_z_single(r, t, cx=0.0, cy=0.0):
    """Wave surface height at crest ring radius r from source (cx, cy) at time t."""
    R = r + 0.25   # matches _R at exact ring radius
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

# Clean dark look: hide pane fills and grid lines
AX.xaxis.pane.fill = False
AX.yaxis.pane.fill = False
AX.zaxis.pane.fill = False
AX.xaxis.pane.set_edgecolor(BG)
AX.yaxis.pane.set_edgecolor(BG)
AX.zaxis.pane.set_edgecolor(BG)
AX.grid(False)
AX.set_xticks([])
AX.set_yticks([])
AX.set_zticks([])
AX.set_proj_type("persp")

# Fixed oblique viewing angle — good balance of depth and plan view
AX.view_init(elev=38, azim=-60)

# Mutable container for the surface (removed and recreated each frame)
SURF = [None]

# Concentric ring overlays — 3-D curves riding the wave surface
N_RINGS = 10
RINGS   = [AX.plot([], [], [], lw=1.6, color=VIOLET, alpha=0)[0]
           for _ in range(N_RINGS)]

# Source marker dots (3-D)
SRC1_DOT, = AX.plot([], [], [], "o", color=WHITE,  ms=9, zorder=10)
SRC2_DOT, = AX.plot([], [], [], "o", color=ORANGE, ms=9, zorder=10)

# Global text (figure-level, always on top)
_stroke = [pe.withStroke(linewidth=3, foreground=BG)]

T_TITLE = FIG.text(0.5, 0.975, "", ha="center", va="top",
                   color=RED, fontsize=21, fontweight="bold",
                   path_effects=_stroke)
T_SUB   = FIG.text(0.5, 0.920, "", ha="center", va="top",
                   color=TEXT, fontsize=11, linespacing=1.55,
                   path_effects=_stroke)
T_EQ    = FIG.text(0.5, 0.050, "", ha="center", va="bottom",
                   color=ORANGE, fontsize=10,
                   path_effects=_stroke)
T_NOTE  = FIG.text(0.5, 0.020, "", ha="center", va="bottom",
                   color=INDIGO, fontsize=9.5, style="italic",
                   path_effects=_stroke)

# ─────────────────────────────────────────────────────────
#  HELPER UTILITIES
# ─────────────────────────────────────────────────────────
def clear_text():
    for t in (T_TITLE, T_SUB, T_EQ, T_NOTE):
        t.set_text("")


def clear_rings():
    for ring in RINGS:
        ring.set_data([], [])
        ring.set_3d_properties([])
        ring.set_alpha(0)


def _set_surface(U, alpha=0.88):
    """Remove old surface and plot a new one from displacement array U."""
    if SURF[0] is not None:
        SURF[0].remove()
    a = float(np.clip(alpha, 0.02, 1.0))   # avoid degenerate alpha
    SURF[0] = AX.plot_surface(
        XX, YY, U,
        cmap=WAVE_CMAP, vmin=-1.2, vmax=1.2,
        alpha=a,
        antialiased=False,
        linewidth=0,
        rcount=GRID_N, ccount=GRID_N,
    )


def draw_rings_from(t, cx=0.0, cy=0.0, color=RED, n=N_RINGS):
    """
    Draw 3-D ring overlays at the wave surface height of each crest ring.
    Newest ring (innermost) is brightest; oldest (outermost) is dimmest,
    matching the 1/√r amplitude decay.
    """
    radii = crest_radii(t, n_rings=n)
    total = max(len(radii), 1)
    for i, ring in enumerate(RINGS):
        if i < len(radii):
            r     = radii[i]
            alpha = 0.25 + 0.65 * (i + 1) / total
            rx    = cx + r * np.cos(_THETA)
            ry    = cy + r * np.sin(_THETA)
            rz    = np.full(len(_THETA), _ring_z_single(r, t, cx, cy))
            ring.set_data(rx, ry)
            ring.set_3d_properties(rz)
            ring.set_alpha(alpha)
            ring.set_color(color)
        else:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)


def fade_in(fi, total, delay=0.0, speed=6.0):
    """Smooth fade from 0→1 starting at delay fraction of the scene."""
    t = fi / max(total - 1, 1)
    return float(np.clip((t - delay) * speed, 0.0, 1.0))


# ─────────────────────────────────────────────────────────
#  SCENE 0  —  Title splash
# ─────────────────────────────────────────────────────────
def scene0_title(fi):
    f = fade_in(fi, SCENE_FRAMES[0])
    clear_text()
    SRC1_DOT.set_data([], [])
    SRC1_DOT.set_3d_properties([])
    SRC2_DOT.set_data([], [])
    SRC2_DOT.set_3d_properties([])

    t_slow = fi / FPS * 0.65
    U = u_single(t_slow) * 0.5
    _set_surface(U, alpha=max(0.02, f * 0.65))

    # Teaser rings rising from the surface
    radii = crest_radii(t_slow, n_rings=N_RINGS)
    total = max(len(radii), 1)
    for i, ring in enumerate(RINGS):
        if i < len(radii):
            r     = radii[i]
            alpha = f * 0.4 * (i + 1) / total
            rz    = np.full(len(_THETA), _ring_z_single(r, t_slow) * 0.5)
            ring.set_data(r * np.cos(_THETA), r * np.sin(_THETA))
            ring.set_3d_properties(rz)
            ring.set_alpha(alpha)
            ring.set_color(INDIGO)
        else:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)

    T_TITLE.set_text("Pulsating Rings\n& Radiating Waves")
    T_TITLE.set_alpha(f)
    T_SUB.set_text("3-D view: vertical axis = displacement amplitude")
    T_SUB.set_alpha(f * 0.85)
    T_NOTE.set_text("Huygens  1678  •  Young  1801  •  v = λ · f")
    T_NOTE.set_alpha(f * 0.7)


# ─────────────────────────────────────────────────────────
#  SCENE 1  —  Single pulsating source
# ─────────────────────────────────────────────────────────
def scene1_single(fi):
    f = fade_in(fi, SCENE_FRAMES[1])
    t = fi / FPS
    clear_text()
    SRC2_DOT.set_data([], [])
    SRC2_DOT.set_3d_properties([])

    U = u_single(t)
    _set_surface(U)

    # Ring overlays ride the wave surface
    draw_rings_from(t, 0.0, 0.0, RED)

    pulse = 0.5 + 0.5 * np.cos(OMEGA * t)
    SRC1_DOT.set_data([0], [0])
    SRC1_DOT.set_3d_properties([0.0])
    SRC1_DOT.set_markersize(7 + 11 * pulse)
    SRC1_DOT.set_color(WHITE)
    SRC1_DOT.set_alpha(0.65 + 0.35 * pulse)

    T_TITLE.set_text("Single Pulsating Source — 3-D")
    T_TITLE.set_alpha(f)
    T_SUB.set_text(
        "Ridge peaks = wavefront crests expanding at  v = λ · f\n"
        "Surface height = displacement  |  Peak height decays as  1/√r"
    )
    T_SUB.set_alpha(f)
    T_EQ.set_text(
        f"λ = {WAVELENGTH:.1f}  |  v = {WAVE_SPEED:.1f}  |"
        f"  f = {FREQ:.2f} Hz  |  T = {PERIOD:.2f} s"
    )
    T_EQ.set_alpha(f)
    T_NOTE.set_text("Peak ridge = crest  |  Valley = trough  |  Red curves trace wavefronts on surface")
    T_NOTE.set_alpha(f)


# ─────────────────────────────────────────────────────────
#  SCENE 2  —  Two-source interference
# ─────────────────────────────────────────────────────────
def scene2_interference(fi):
    f = fade_in(fi, SCENE_FRAMES[2])
    t = fi / FPS
    clear_text()

    U = u_two_source(t)
    _set_surface(U)

    # Split ring slots between S₁ and S₂
    half   = N_RINGS // 2
    radii  = crest_radii(t, n_rings=half)
    total  = max(len(radii), 1)
    for i in range(N_RINGS):
        is_b  = i >= half
        src   = SRC_B if is_b else SRC_A
        color = ORANGE if is_b else VIOLET
        idx   = i - half if is_b else i
        if idx < len(radii):
            r     = radii[idx]
            alpha = 0.25 + 0.60 * (idx + 1) / total
            rx    = src[0] + r * np.cos(_THETA)
            ry    = src[1] + r * np.sin(_THETA)
            rz    = np.full(len(_THETA), _ring_z_single(r, t, src[0], src[1]))
            RINGS[i].set_data(rx, ry)
            RINGS[i].set_3d_properties(rz)
            RINGS[i].set_alpha(alpha)
            RINGS[i].set_color(color)
        else:
            RINGS[i].set_data([], [])
            RINGS[i].set_3d_properties([])
            RINGS[i].set_alpha(0)

    pulse = 0.5 + 0.5 * np.cos(OMEGA * t)
    SRC1_DOT.set_data([SRC_A[0]], [SRC_A[1]])
    SRC1_DOT.set_3d_properties([0.0])
    SRC1_DOT.set_markersize(7 + 9 * pulse)
    SRC1_DOT.set_color(VIOLET)
    SRC1_DOT.set_alpha(1.0)

    SRC2_DOT.set_data([SRC_B[0]], [SRC_B[1]])
    SRC2_DOT.set_3d_properties([0.0])
    SRC2_DOT.set_markersize(7 + 9 * pulse)
    SRC2_DOT.set_color(ORANGE)
    SRC2_DOT.set_alpha(1.0)

    T_TITLE.set_text("Two-Source Interference — 3-D")
    T_TITLE.set_alpha(f)
    T_SUB.set_text(
        "Tall peaks = constructive (S₁ + S₂ crests align)\n"
        "Flat lanes = destructive (crest meets trough, z ≈ 0)"
    )
    T_SUB.set_alpha(f)
    T_NOTE.set_text("Same physics as Young's double-slit experiment  (1801)")
    T_NOTE.set_alpha(f)


# ─────────────────────────────────────────────────────────
#  SCENE 3  —  Standing wave
# ─────────────────────────────────────────────────────────
def scene3_standing(fi):
    f = fade_in(fi, SCENE_FRAMES[3])
    t = fi / FPS
    clear_text()
    SRC2_DOT.set_data([], [])
    SRC2_DOT.set_3d_properties([])

    # Standing-wave surface — entire field breathes in/out
    U = u_standing(t)
    _set_surface(U)

    # Node rings pinned at z = 0 (they never move)
    pulse = abs(np.cos(OMEGA * t))
    for i, ring in enumerate(RINGS):
        R_node = (np.pi / 2 + i * np.pi) / K      # node ring radius
        if R_node > LIM * 1.05:
            ring.set_data([], [])
            ring.set_3d_properties([])
            ring.set_alpha(0)
        else:
            ring.set_data(R_node * np.cos(_THETA), R_node * np.sin(_THETA))
            ring.set_3d_properties(np.zeros(len(_THETA)))   # always z = 0
            # Brightest at zero-crossings of cos(ωt), where spatial pattern is clearest
            ring.set_alpha(0.30 + 0.50 * (1.0 - pulse))
            ring.set_color(VIOLET)

    SRC1_DOT.set_data([0], [0])
    SRC1_DOT.set_3d_properties([0.0])
    SRC1_DOT.set_markersize(6 + 14 * pulse)
    SRC1_DOT.set_color(WHITE)
    SRC1_DOT.set_alpha(0.55 + 0.45 * pulse)

    T_TITLE.set_text("Standing Wave — 3-D")
    T_TITLE.set_alpha(f)
    T_SUB.set_text(
        "Outgoing + reflected wave → node rings fixed at z = 0\n"
        "u(r, t) = 2·cos(k·r)·cos(ω·t) — whole surface breathes in/out"
    )
    T_SUB.set_alpha(f)
    T_EQ.set_text(
        "Node rings (z = 0 always):  k·R = π/2 + n·π  →  R_n = (2n+1)·λ/4"
    )
    T_EQ.set_alpha(f)
    T_NOTE.set_text(
        "Violet rings = permanent nodes at z = 0  |  Surface between rings pulsates ±max"
    )
    T_NOTE.set_alpha(f)


# ─────────────────────────────────────────────────────────
#  SCENE 4  —  Key Takeaways
# ─────────────────────────────────────────────────────────
def scene4_summary(fi):
    f = fade_in(fi, SCENE_FRAMES[4])
    t = fi / FPS * 0.40
    clear_text()
    SRC2_DOT.set_data([], [])
    SRC2_DOT.set_3d_properties([])

    U = u_single(t) * 0.45
    _set_surface(U, alpha=0.70)
    draw_rings_from(t, 0.0, 0.0, RED)

    SRC1_DOT.set_data([0], [0])
    SRC1_DOT.set_3d_properties([0.0])
    SRC1_DOT.set_markersize(7)
    SRC1_DOT.set_color(WHITE)
    SRC1_DOT.set_alpha(0.5)

    # Shift subtitle lower + shrink to fit 4 lines
    T_SUB.set_position((0.5, 0.900))
    T_SUB.set_fontsize(10.5)

    T_TITLE.set_text("Key Takeaways")
    T_TITLE.set_alpha(f)
    T_SUB.set_text(
        "①  Ridge peaks radiate outward at wave speed  v = λ · f\n"
        "②  Peak height decays as  1/√r  — energy conservation in 2-D\n"
        "③  Two sources create constructive / destructive interference in 3-D\n"
        "④  Standing waves: fixed node rings (z = 0), pulsating antinodes"
    )
    T_SUB.set_alpha(f * 0.9)
    T_EQ.set_text(
        "v = ω / k     |     λ = 2π / k     |     f = ω / (2π)     |     T = 1 / f"
    )
    T_EQ.set_alpha(f)
    T_NOTE.set_text("Pulsating Rings & Radiating Waves  •  3-D Wave Surface Visualization")
    T_NOTE.set_alpha(f)


# ─────────────────────────────────────────────────────────
#  ANIMATION DISPATCH
# ─────────────────────────────────────────────────────────
_SCENE_FNS = [scene0_title, scene1_single, scene2_interference,
              scene3_standing, scene4_summary]


def update(frame):
    # Restore T_SUB position at the start of each frame to undo scene 4 tweaks
    T_SUB.set_position((0.5, 0.920))
    T_SUB.set_fontsize(11)

    scene = next(
        s for s in range(len(SCENE_FRAMES))
        if CUMULATIVE[s] <= frame < CUMULATIVE[s + 1]
    )
    fi = frame - CUMULATIVE[scene]
    _SCENE_FNS[scene](fi)
    return []


# ─────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Pulsating Rings & Radiating Waves — 3-D Surface")
    print(f"  Grid   : {GRID_N}×{GRID_N}")
    print(f"  Frames : {TOTAL_FRAMES}  ({TOTAL_FRAMES / FPS:.1f} s @ {FPS} fps)")
    print(f"  λ={WAVELENGTH}  v={WAVE_SPEED}  f={FREQ:.3f} Hz  T={PERIOD:.3f} s")
    print("  Rendering animation … (may take ~60–120 s for 3-D surface)")

    ani = FuncAnimation(
        FIG, update,
        frames=TOTAL_FRAMES,
        interval=1000 // FPS,
        blit=False,
    )

    OUT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "pulsating_rings_waves.gif",
    )
    ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
    print(f"  Saved  → {OUT}")
    plt.close(FIG)
