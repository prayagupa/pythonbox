#!/usr/bin/env python3
"""
Universe Expansion — 3-D Animation
═══════════════════════════════════
An educational visualization of how the universe has expanded since the Big
Bang, including Hubble's Law, the cosmic web, and dark-energy acceleration.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE BIG IDEA (Hubble, 1929 / Friedmann, 1922):
  Every galaxy in the universe is moving AWAY from every other
  galaxy — not because they are flying through space, but because
  SPACE ITSELF is stretching.  The farther apart two galaxies are,
  the faster they appear to recede from each other.
  This is described by  v = H₀ × d  (Hubble's Law).
  Since 1998 we know dark energy is causing the expansion to
  ACCELERATE — galaxies are speeding up, not slowing down!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Scene 0 — Title / Big Bang flash
  Scene 1 — Hubble Flow: 3-D galaxy recession (v = H₀ d)
  Scene 2 — Cosmic Web: dark-matter filaments light up
  Scene 3 — Dark Energy: expansion accelerates
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
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401 — registers 3-D proj
from mpl_toolkits.mplot3d.art3d import Line3DCollection
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
#  COLOUR PALETTE  (deep-space look)
# ─────────────────────────────────────────────────────────
BG      = "#03030e"    # near-black background
TEXT    = "#dde8ff"    # soft white
CYAN    = "#00d4ff"    # accent / titles
GOLD    = "#ffd700"    # galaxy colour
ORANGE  = "#ff7733"    # Big Bang burst
PINK    = "#ff66cc"    # filament / dark energy
GREEN   = "#44ff88"    # explanatory text
WHITE   = "#ffffff"
DIM     = "#2a2a5a"    # dimmed axis panes

# ─────────────────────────────────────────────────────────
#  TIMING
# ─────────────────────────────────────────────────────────
FPS          = 22
SCENE_FRAMES = [45, 80, 75, 80, 55]      # frames per scene
CUMULATIVE   = list(np.cumsum([0] + SCENE_FRAMES))
TOTAL_FRAMES = sum(SCENE_FRAMES)

# ─────────────────────────────────────────────────────────
#  GALAXY SEED  (fixed positions in "comoving" coordinates)
# ─────────────────────────────────────────────────────────
np.random.seed(2024)
N_GAL    = 200                               # total galaxy count
# comoving positions — uniform in a sphere of radius 1
_phi     = np.random.uniform(0, 2 * np.pi, N_GAL)
_cos_th  = np.random.uniform(-1, 1, N_GAL)
_sin_th  = np.sqrt(1 - _cos_th**2)
_r_raw   = np.random.uniform(0, 1, N_GAL) ** (1 / 3)   # uniform volume
COM_X    = _r_raw * _sin_th * np.cos(_phi)
COM_Y    = _r_raw * _sin_th * np.sin(_phi)
COM_Z    = _r_raw * _cos_th
COM_R    = _r_raw                             # 0 … 1

# galaxy "luminosity" — brighter near centre
GAL_SIZE = (15 + 40 * np.exp(-3 * COM_R**2)).clip(8, 55)
GAL_ALPHA= (0.5 + 0.5 * np.exp(-2 * COM_R)).clip(0.3, 1.0)

# ─────────────────────────────────────────────────────────
#  BACKGROUND STAR FIELD (decorative, fixed)
# ─────────────────────────────────────────────────────────
N_STARS   = 350
STAR_X    = np.random.uniform(-1.8, 1.8, N_STARS)
STAR_Y    = np.random.uniform(-1.8, 1.8, N_STARS)
STAR_Z    = np.random.uniform(-1.8, 1.8, N_STARS)
STAR_S    = np.random.uniform(1, 5, N_STARS)
STAR_A    = np.random.uniform(0.2, 0.7, N_STARS)
STAR_PHASE= np.random.uniform(0, 2 * np.pi, N_STARS)

# ─────────────────────────────────────────────────────────
#  COSMIC WEB EDGES  (nearest-neighbour pairs)
# ─────────────────────────────────────────────────────────
def build_web(max_edges=320, max_dist_com=0.35):
    """Return index pairs (i,j) for galaxies close in comoving space."""
    pairs = []
    for i in range(N_GAL):
        for j in range(i + 1, N_GAL):
            d = np.sqrt((COM_X[i]-COM_X[j])**2 +
                        (COM_Y[i]-COM_Y[j])**2 +
                        (COM_Z[i]-COM_Z[j])**2)
            if d < max_dist_com:
                pairs.append((i, j, d))
        if len(pairs) > max_edges * 3:
            break
    pairs.sort(key=lambda x: x[2])
    return [(p[0], p[1]) for p in pairs[:max_edges]]

WEB_PAIRS = build_web()

# ─────────────────────────────────────────────────────────
#  SCALE FACTOR  a(t)  — piecewise cosmic history
# ─────────────────────────────────────────────────────────
def scale_factor(t_norm):
    """
    t_norm ∈ [0, 1] → scale factor a ∈ [0, ~2.5]

    Rough three-epoch model:
      0.00–0.10  Radiation domination :  a ∝ t^(1/2)
      0.10–0.55  Matter domination    :  a ∝ t^(2/3)
      0.55–1.00  Dark energy          :  a ∝ exp(H_Λ · (t - t_Λ))

    All pieces joined so a is continuous.
    """
    t   = np.asarray(t_norm, dtype=float)
    a   = np.zeros_like(t)

    t1, t2 = 0.10, 0.55

    # Radiation era
    m0 = t < t1
    a[m0] = (t[m0] / t1) ** 0.5

    # Matter era  (join at t1 where a=1)
    m1 = (t >= t1) & (t < t2)
    a[m1] = ((t[m1] - t1) / (t2 - t1) * 0.9 + 1.0) ** (2/3)

    # Dark-energy era  (exponential acceleration, joins at t2)
    a_t2 = ((0.9) + 1.0) ** (2/3)        # ≈ 1.57
    H_L  = 1.8
    m2 = t >= t2
    a[m2] = a_t2 * np.exp(H_L * (t[m2] - t2))

    return a


# Build a lookup table once — we'll index into it per frame
T_NORM_ALL = np.linspace(0, 1, TOTAL_FRAMES)
A_ALL      = scale_factor(T_NORM_ALL)

# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────
def fade_in(t_norm, delay=0.0, speed=8.0):
    """Return an alpha in [0,1] that rises smoothly from `delay`."""
    return float(np.clip((t_norm - delay) * speed, 0.0, 1.0))


def style_3d(ax, title="", elev=25, azim=0, lim=None):
    """Apply consistent deep-space styling to a 3-D axes."""
    if lim is None:
        lim = 1.6
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_facecolor(BG)
    ax.xaxis.pane.fill = True;  ax.xaxis.pane.set_facecolor(DIM + "55")
    ax.yaxis.pane.fill = True;  ax.yaxis.pane.set_facecolor(DIM + "55")
    ax.zaxis.pane.fill = True;  ax.zaxis.pane.set_facecolor(DIM + "55")
    ax.xaxis.pane.set_edgecolor(DIM)
    ax.yaxis.pane.set_edgecolor(DIM)
    ax.zaxis.pane.set_edgecolor(DIM)
    ax.tick_params(colors=TEXT, labelsize=7)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.zaxis.label.set_color(TEXT)
    ax.set_xlabel("x  (Gly)", fontsize=7, labelpad=4)
    ax.set_ylabel("y  (Gly)", fontsize=7, labelpad=4)
    ax.set_zlabel("z  (Gly)", fontsize=7, labelpad=4)
    ax.grid(True, color=CYAN + "22", linewidth=0.4)
    ax.view_init(elev=elev, azim=azim)
    if title:
        ax.set_title(title, color=CYAN, fontsize=11, pad=10,
                     fontweight="bold")


def galaxy_positions(a):
    """Physical positions = comoving × scale-factor."""
    return COM_X * a, COM_Y * a, COM_Z * a


def hubble_speed(a, v_fac=0.55):
    """Recession speed proxy in [0,1] for colour mapping."""
    return np.clip(COM_R * a * v_fac, 0, 1)


# ─────────────────────────────────────────────────────────
#  FIGURE SETUP
# ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 8.5), facecolor=BG)

# ══════════════════════════════════════════════════════════
#  MAIN UPDATE FUNCTION
# ══════════════════════════════════════════════════════════
def update(frame):
    fig.clf()
    fig.patch.set_facecolor(BG)

    # Determine current scene and local t ∈ [0,1]
    scene = 0
    for s, (lo, hi) in enumerate(zip(CUMULATIVE[:-1], CUMULATIVE[1:])):
        if lo <= frame < hi:
            scene = s
            t = (frame - lo) / max(hi - lo - 1, 1)
            break

    a_now = float(A_ALL[frame])   # current scale factor

    # ──────────────────────────────────────────────────────
    # SCENE 0 — Title  /  Big Bang flash
    # ──────────────────────────────────────────────────────
    if scene == 0:
        ax = fig.add_subplot(111, facecolor=BG)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

        # Starburst glow rings emanating from centre
        n_rings = 7
        for i in range(n_rings):
            r_max  = 0.48
            r_ring = t * r_max * (i + 1) / n_rings
            alpha  = max(0, 0.7 - t * 0.9 - i * 0.08)
            circ = plt.Circle((0.5, 0.5), r_ring,
                               color=ORANGE, fill=False,
                               linewidth=3 - i * 0.3, alpha=alpha)
            ax.add_patch(circ)

        # Random spark particles flying outward from the Big Bang
        np.random.seed(0)
        n_sparks = 120
        ang   = np.random.uniform(0, 2 * np.pi, n_sparks)
        speed = np.random.uniform(0.1, 1.0, n_sparks)
        r     = t * speed * 0.5
        sx    = 0.5 + r * np.cos(ang)
        sy    = 0.5 + r * np.sin(ang)
        cols  = plt.cm.plasma(speed)
        valid = (sx > 0) & (sx < 1) & (sy > 0) & (sy < 1)
        ax.scatter(sx[valid], sy[valid],
                   c=cols[valid], s=(8 + 20 * (1 - t * speed[valid])),
                   alpha=np.clip(0.9 - t * 0.5, 0.1, 1.0), zorder=5)

        # Central explosion flash
        flash_r = 0.06 + t * 0.12
        flash_a = max(0, 1 - t * 1.8)
        circ2 = plt.Circle((0.5, 0.5), flash_r, color=WHITE,
                            fill=True, alpha=flash_a, zorder=10)
        ax.add_patch(circ2)

        # Title text
        ax.text(0.5, 0.78,
                "🌌  Universe Expansion",
                ha="center", va="center", fontsize=30, fontweight="bold",
                color=CYAN, alpha=fade_in(t, delay=0.25, speed=5),
                transform=ax.transAxes,
                path_effects=[pe.withStroke(linewidth=4, foreground=BG)])

        ax.text(0.5, 0.68,
                "From the Big Bang to Dark Energy Acceleration",
                ha="center", va="center", fontsize=14,
                color=TEXT, alpha=fade_in(t, delay=0.40, speed=5),
                transform=ax.transAxes)

        ax.text(0.5, 0.18,
                "Space itself is stretching — every galaxy races away from every other.",
                ha="center", va="center", fontsize=11,
                color=GREEN, alpha=fade_in(t, delay=0.55, speed=4),
                transform=ax.transAxes, style="italic")

        ax.text(0.5, 0.10,
                "v  =  H₀ × d   (Hubble's Law, 1929)",
                ha="center", va="center", fontsize=13, fontweight="bold",
                color=GOLD, alpha=fade_in(t, delay=0.70, speed=4),
                transform=ax.transAxes)

    # ──────────────────────────────────────────────────────
    # SCENE 1 — Hubble Flow  (3-D recession)
    # ──────────────────────────────────────────────────────
    elif scene == 1:
        ax = fig.add_subplot(111, projection="3d", facecolor=BG)

        # Slowly twinkling background stars
        twinkle = 0.4 + 0.3 * np.sin(STAR_PHASE + frame * 0.18)
        ax.scatter(STAR_X, STAR_Y, STAR_Z,
                   s=STAR_S, c=WHITE,
                   alpha=np.clip(twinkle * STAR_A, 0, 0.55),
                   zorder=0, depthshade=False)

        # Galaxy positions expand with scale factor
        gx, gy, gz = galaxy_positions(a_now)
        v_speed     = hubble_speed(a_now)          # 0…1, for colour

        # Colour galaxies by recession speed (blue=slow → red=fast)
        colours = plt.cm.cool(1 - v_speed)
        ax.scatter(gx, gy, gz,
                   c=colours, s=GAL_SIZE,
                   alpha=GAL_ALPHA, zorder=5, depthshade=True)

        # Draw Hubble-flow arrows for a subset of galaxies
        arrow_mask = COM_R > 0.35
        arrow_idx  = np.where(arrow_mask)[0][::6]
        for i in arrow_idx:
            length = 0.18 * a_now * COM_R[i]
            ax.quiver(gx[i], gy[i], gz[i],
                      COM_X[i] * length, COM_Y[i] * length, COM_Z[i] * length,
                      color=PINK, alpha=0.55, linewidth=0.8,
                      arrow_length_ratio=0.4)

        # Scale-factor label
        ax.text2D(0.03, 0.96,
                  f"Scale factor  a(t) = {a_now:.2f}",
                  transform=ax.transAxes,
                  color=GOLD, fontsize=11, fontweight="bold", va="top")

        ax.text2D(0.03, 0.89,
                  "Each arrow shows a galaxy\nreceding through space.\n\n"
                  "Farther galaxies move FASTER —\nthat is Hubble's Law!",
                  transform=ax.transAxes,
                  color=GREEN, fontsize=9.5, va="top")

        lim = max(1.0, a_now * 1.15)
        style_3d(ax,
                 title="Scene 1 — Hubble Flow: v = H₀ × d",
                 elev=28,
                 azim=-40 + t * 90,
                 lim=lim)

    # ──────────────────────────────────────────────────────
    # SCENE 2 — Cosmic Web
    # ──────────────────────────────────────────────────────
    elif scene == 2:
        ax = fig.add_subplot(111, projection="3d", facecolor=BG)

        # Background stars
        twinkle = 0.4 + 0.3 * np.sin(STAR_PHASE + frame * 0.14)
        ax.scatter(STAR_X, STAR_Y, STAR_Z,
                   s=STAR_S, c=WHITE,
                   alpha=np.clip(twinkle * STAR_A, 0, 0.50),
                   zorder=0, depthshade=False)

        gx, gy, gz = galaxy_positions(a_now)

        # --- Filaments (cosmic web) light up progressively ---
        n_visible = int(t * len(WEB_PAIRS))
        segs = []
        for idx, (i, j) in enumerate(WEB_PAIRS[:n_visible]):
            segs.append([(gx[i], gy[i], gz[i]),
                          (gx[j], gy[j], gz[j])])

        if segs:
            lc = Line3DCollection(segs,
                                  colors=CYAN + "60",
                                  linewidths=0.6,
                                  alpha=0.45,
                                  zorder=2)
            ax.add_collection(lc)

        # Galaxy nodes — glow brighter at filament intersections
        degree = np.zeros(N_GAL)
        for i, j in WEB_PAIRS[:n_visible]:
            degree[i] += 1
            degree[j] += 1
        node_size = GAL_SIZE + degree * 3

        ax.scatter(gx, gy, gz,
                   c=GOLD, s=node_size,
                   alpha=GAL_ALPHA, zorder=5, depthshade=True)

        ax.text2D(0.03, 0.96,
                  f"Scale factor  a(t) = {a_now:.2f}",
                  transform=ax.transAxes,
                  color=GOLD, fontsize=11, fontweight="bold", va="top")

        ax.text2D(0.03, 0.89,
                  "Glowing threads = dark matter\nfilaments connecting galaxies.\n\n"
                  "This 'Cosmic Web' is the\nlargest structure in nature!",
                  transform=ax.transAxes,
                  color=GREEN, fontsize=9.5, va="top")

        lim = max(1.0, a_now * 1.15)
        style_3d(ax,
                 title="Scene 2 — The Cosmic Web",
                 elev=30,
                 azim=50 + t * 100,
                 lim=lim)

    # ──────────────────────────────────────────────────────
    # SCENE 3 — Dark Energy Acceleration
    # ──────────────────────────────────────────────────────
    elif scene == 3:
        # Split layout: 3-D view (left) + a(t) curve (right)
        ax3d = fig.add_subplot(121, projection="3d", facecolor=BG)
        ax2d = fig.add_subplot(122, facecolor=BG)

        # --- 3-D panel ---
        gx, gy, gz = galaxy_positions(a_now)

        # Filaments — show full web, fading slightly
        segs = [[(gx[i], gy[i], gz[i]), (gx[j], gy[j], gz[j])]
                for i, j in WEB_PAIRS]
        lc = Line3DCollection(segs, colors=CYAN + "40",
                               linewidths=0.5, alpha=0.35, zorder=1)
        ax3d.add_collection(lc)

        # Galaxies — colour ramps from gold → pink as expansion speeds up
        blend = np.clip(t * 1.2, 0, 1)
        gold_rgb  = np.array([1.0, 0.843, 0.0])
        pink_rgb  = np.array([1.0, 0.4, 0.8])
        node_col  = (1 - blend) * gold_rgb + blend * pink_rgb
        ax3d.scatter(gx, gy, gz,
                     color=tuple(node_col),
                     s=GAL_SIZE * (1 + blend * 0.5),
                     alpha=GAL_ALPHA, zorder=5, depthshade=True)

        # Pulsing acceleration arrows — thicker and more energetic
        arrow_idx = np.where(COM_R > 0.4)[0][::5]
        alen = 0.22 * a_now * COM_R
        for i in arrow_idx:
            ax3d.quiver(gx[i], gy[i], gz[i],
                        COM_X[i] * alen[i], COM_Y[i] * alen[i], COM_Z[i] * alen[i],
                        color=PINK, alpha=0.7 + 0.3 * np.sin(frame * 0.3),
                        linewidth=1.2, arrow_length_ratio=0.35)

        ax3d.text2D(0.04, 0.96,
                    f"a(t) = {a_now:.2f}",
                    transform=ax3d.transAxes,
                    color=PINK, fontsize=10, fontweight="bold", va="top")

        lim = max(1.0, a_now * 1.1)
        style_3d(ax3d,
                 title="Scene 3 — Dark Energy Acceleration",
                 elev=25,
                 azim=-30 + t * 110,
                 lim=lim)

        # --- 2-D panel: scale-factor history ---
        ax2d.set_facecolor(BG)
        ax2d.tick_params(colors=TEXT, labelsize=8)
        for spine in ax2d.spines.values():
            spine.set_edgecolor(DIM)

        t_history = np.linspace(0, T_NORM_ALL[frame], 300)
        a_history = scale_factor(t_history)

        # Shade the three eras
        ax2d.axvspan(0,    0.10, alpha=0.12, color=ORANGE, label="Radiation era")
        ax2d.axvspan(0.10, 0.55, alpha=0.10, color=CYAN,   label="Matter era")
        ax2d.axvspan(0.55, 1.00, alpha=0.10, color=PINK,   label="Dark energy era")

        ax2d.plot(t_history, a_history, color=GOLD, lw=2.2, zorder=5)
        ax2d.scatter([T_NORM_ALL[frame]], [a_now],
                     color=PINK, s=90, zorder=10,
                     edgecolors=WHITE, linewidths=1.5)

        ax2d.set_xlim(0, 1)
        ax2d.set_ylim(0, a_history.max() * 1.15)
        ax2d.set_xlabel("Cosmic Time  (normalised)", color=TEXT, fontsize=9)
        ax2d.set_ylabel("Scale Factor  a(t)", color=TEXT, fontsize=9)
        ax2d.set_title("Expansion History", color=CYAN,
                       fontsize=10, fontweight="bold")

        legend = ax2d.legend(fontsize=8, facecolor=BG,
                              labelcolor=TEXT, framealpha=0.7,
                              loc="upper left")

        # Annotate dark energy slope
        a_de = fade_in(t, delay=0.3, speed=5)
        ax2d.text(0.72, 0.38,
                  "🌑 Dark Energy\naccelerates\nexpansion!",
                  ha="center", va="center", fontsize=9,
                  color=PINK, alpha=a_de,
                  transform=ax2d.transAxes,
                  bbox=dict(boxstyle="round,pad=0.4",
                            facecolor=BG, edgecolor=PINK, alpha=0.7))

        fig.text(0.5, 0.01,
                 "Discovered 1998 (Nobel Prize 2011) — something is pushing space apart faster and faster!",
                 ha="center", fontsize=9, color=GREEN, alpha=fade_in(t, delay=0.5))

    # ──────────────────────────────────────────────────────
    # SCENE 4 — Key Takeaways
    # ──────────────────────────────────────────────────────
    elif scene == 4:
        ax = fig.add_subplot(111, facecolor=BG)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

        # Slow particle drift background
        np.random.seed(99)
        np.random.seed(99)
        n_bg = 180
        bx = np.random.uniform(0, 1, n_bg)
        by = np.random.uniform(0, 1, n_bg)
        bs = np.random.uniform(2, 8, n_bg)
        ba = np.random.uniform(0.08, 0.25, n_bg)
        ax.scatter(bx, by, s=bs, c=CYAN, alpha=ba * (0.7 + 0.3 * np.sin(frame * 0.1)),
                   zorder=0)

        ax.text(0.5, 0.94,
                "✅  Key Takeaways",
                ha="center", va="top", fontsize=22, fontweight="bold",
                color=CYAN, alpha=fade_in(t, speed=6),
                transform=ax.transAxes)

        bullets = [
            ("🌌  Expanding Universe",
             "Space itself stretches — galaxies aren't flying through space, space grows between them."),
            ("📏  Hubble's Law  v = H₀ × d",
             "Recession speed is proportional to distance.  Farther ↔ faster.  Measured in km/s/Mpc."),
            ("🕸️  Cosmic Web",
             "Dark matter filaments form a vast web of galaxy clusters, sheets, and voids."),
            ("🌑  Dark Energy  (≈ 68 % of universe)",
             "An unknown repulsive energy overcoming gravity and accelerating the expansion."),
            ("🏆  Nobel Prize 2011",
             "Perlmutter, Schmidt & Riess proved acceleration using distant Type Ia supernovae."),
        ]

        for i, (title, desc) in enumerate(bullets):
            y_title = 0.80 - i * 0.145
            y_desc  = y_title - 0.055
            a = fade_in(t, delay=0.07 + i * 0.10, speed=7)
            ax.text(0.05, y_title, title,
                    ha="left", va="center", fontsize=13, fontweight="bold",
                    color=GOLD, alpha=a, transform=ax.transAxes)
            ax.text(0.05, y_desc, desc,
                    ha="left", va="center", fontsize=10.5,
                    color=TEXT, alpha=a, transform=ax.transAxes)

        ax.text(0.5, 0.032,
                "The universe is ~13.8 billion years old and still accelerating — destination: unknown.",
                ha="center", va="bottom", fontsize=11,
                color=PINK, style="italic",
                alpha=fade_in(t, delay=0.75, speed=5),
                transform=ax.transAxes)

    return []


# ══════════════════════════════════════════════════════════
#  BUILD & SAVE
# ══════════════════════════════════════════════════════════
print("Building Universe Expansion animation …")
print(f"  Total frames : {TOTAL_FRAMES}")
print(f"  Duration     : {TOTAL_FRAMES / FPS:.1f} s  @ {FPS} fps")

ani = FuncAnimation(
    fig,
    update,
    frames=TOTAL_FRAMES,
    interval=int(1000 / FPS),
    blit=False,
    repeat=True,
)

# Save GIF next to this script (mirrors spacetime_curvature.py pattern)
_here    = os.path.dirname(os.path.abspath(__file__))
_out_gif = os.path.join(_here, "universe_expansion.gif")

print(f"\nSaving GIF → {_out_gif}")
print("(this may take ~30 s …)")
ani.save(_out_gif,
         writer=PillowWriter(fps=FPS),
         dpi=90)
print("GIF saved ✓")

print("\n▶  Opening interactive window — close it to exit.")
plt.tight_layout()
plt.show()
