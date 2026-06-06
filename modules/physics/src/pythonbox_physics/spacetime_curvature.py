#!/usr/bin/env python3
"""
General Relativity: Spacetime Curvature Animation
══════════════════════════════════════════════════
A high-school friendly visualization of how mass curves spacetime.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE BIG IDEA (Einstein, 1915):
  Imagine spacetime as a giant rubber sheet stretched across
  the universe.  When you place a heavy ball (a star) on it,
  the sheet bends downward.  A smaller ball (a planet) placed
  nearby will then roll toward the heavy one — NOT because
  something is pulling it, but because the sheet itself is
  curved.  THAT is gravity according to General Relativity!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Scene 0 — Title screen & Einstein's quote
  Scene 1 — Flat spacetime  (empty universe, no mass)
  Scene 2 — A massive star bends spacetime
  Scene 3 — A planet orbits along the curved path (geodesic)
  Scene 4 — Key-takeaways summary

Dependencies (all in requirements.txt): numpy, matplotlib
"""

import numpy as np
import matplotlib
# Try backends in order of reliability on macOS
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _test_plt  # noqa: F401 — probe import
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — needed for 3-D projection
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
#  COLOUR PALETTE  (deep-space look)
# ─────────────────────────────────────────────────────────
BG     = "#04040f"   # near-black background
TEXT   = "#dde8ff"   # soft white text
CYAN   = "#00d4ff"   # spacetime grid lines
ORANGE = "#ff7733"   # star (massive object)
GOLD   = "#ffd700"   # planet (small object) + labels
GREEN  = "#44ff88"   # explanatory text
PINK   = "#ff66cc"   # orbit trail / dashed path
WHITE  = "#ffffff"
GRID_C = "#0d0d2b"   # axis pane edge colour

# ─────────────────────────────────────────────────────────
#  TIMING  (change SCENE_FRAMES to make scenes longer/shorter)
# ─────────────────────────────────────────────────────────
FPS          = 20                          # frames per second
SCENE_FRAMES = [60, 90, 110, 130, 80]     # frames for each scene
CUMULATIVE   = np.cumsum([0] + SCENE_FRAMES)
TOTAL_FRAMES = sum(SCENE_FRAMES)

# ─────────────────────────────────────────────────────────
#  STAR FIELD  (decorative twinkle background for 2-D scenes)
# ─────────────────────────────────────────────────────────
np.random.seed(42)
STAR_X     = np.random.uniform(0.01, 0.99, 220)
STAR_Y     = np.random.uniform(0.01, 0.99, 220)
STAR_PHASE = np.random.uniform(0, 2 * np.pi, 220)

# ─────────────────────────────────────────────────────────
#  SPACETIME GRID  (the "rubber sheet")
# ─────────────────────────────────────────────────────────
GRID_N = 30           # number of sample points per axis
GRID_R = 3.0          # half-width of the grid (in arbitrary units)
MASS   = 1.8          # controls how deep the gravitational well is

xi = np.linspace(-GRID_R, GRID_R, GRID_N)
yi = np.linspace(-GRID_R, GRID_R, GRID_N)
X_grid, Y_grid = np.meshgrid(xi, yi)
# Distance from the centre for every grid point
R_grid = np.sqrt(X_grid**2 + Y_grid**2)
R_grid = np.maximum(R_grid, 0.35)         # never divide by zero at (0,0)


def spacetime_dip(strength):
    """
    Return the Z (height) of every grid point on the "rubber sheet".

    strength = 0  →  perfectly flat sheet  (no mass)
    strength = 1  →  fully curved          (star at centre)

    The formula  Z = -M / r  mimics the Schwarzschild gravitational
    potential: the closer you are to the mass, the deeper the dip.
    """
    Z = -strength * MASS / R_grid
    return np.clip(Z, -MASS * 2.2, 0.0)   # limit the depth so the plot looks nice


# ─────────────────────────────────────────────────────────
#  ORBITAL PATH  (how the planet moves on the curved sheet)
# ─────────────────────────────────────────────────────────
ORBIT_R      = 1.5                                   # radius of the orbit
theta_all    = np.linspace(0, 2 * np.pi, 360)        # full circle in angles


def planet_position(strength, theta):
    """
    Return (x, y, z) of the planet at orbital angle theta.
    The planet sits ON the curved rubber sheet, so its z matches the dip.
    """
    px = ORBIT_R * np.cos(theta)
    py = ORBIT_R * np.sin(theta)
    r  = max(np.sqrt(px**2 + py**2), 0.35)
    pz = -strength * MASS / r
    return px, py, pz


# ══════════════════════════════════════════════════════════
#  HELPER UTILITIES
# ══════════════════════════════════════════════════════════

def get_scene(frame):
    """
    Given a global frame number, return:
      (scene_index, local_frame_within_scene, t)
    where t goes from 0.0 at the start of the scene to 1.0 at the end.
    """
    for i, end in enumerate(CUMULATIVE[1:]):
        if frame < end:
            local = frame - CUMULATIVE[i]
            t = local / SCENE_FRAMES[i]
            return i, local, t
    # Safety: last frame of last scene
    last = len(SCENE_FRAMES) - 1
    return last, SCENE_FRAMES[last] - 1, 1.0


def fade_in(t, delay=0.0, speed=5.0):
    """
    Smoothly ramp from 0 → 1.
      delay : fraction of [0,1] before anything appears
      speed : how fast it ramps up after the delay
    """
    return float(np.clip((t - delay) * speed, 0.0, 1.0))


def style_3d_axes(ax, title_str, zlabel="Curvature  ↓"):
    """Apply consistent cosmetic settings to a 3-D axes object."""
    ax.set_xlim(-GRID_R, GRID_R)
    ax.set_ylim(-GRID_R, GRID_R)
    ax.set_zlim(-MASS * 2.4, 0.6)
    ax.set_title(title_str, color=TEXT, fontsize=13, pad=12)
    ax.set_xlabel("Space  →  X", color=CYAN,  labelpad=8)
    ax.set_ylabel("Space  →  Y", color=CYAN,  labelpad=8)
    ax.set_zlabel(zlabel,        color=GOLD,  labelpad=8)
    ax.tick_params(colors=TEXT, labelsize=7)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor(GRID_C)
    ax.yaxis.pane.set_edgecolor(GRID_C)
    ax.zaxis.pane.set_edgecolor(GRID_C)


def draw_stars(ax, t):
    """Draw twinkling star dots on a 2-D axes (uses axes-coordinates)."""
    alphas = 0.55 * (0.3 + 0.7 * np.abs(np.sin(STAR_PHASE + t * 3.0)))
    ax.scatter(STAR_X, STAR_Y, s=0.5, c=WHITE,
               alpha=np.clip(alphas, 0, 1),
               transform=ax.transAxes, zorder=0)


# ══════════════════════════════════════════════════════════
#  FIGURE
# ══════════════════════════════════════════════════════════
fig = plt.figure(figsize=(14, 8), facecolor=BG)


# ══════════════════════════════════════════════════════════
#  MAIN ANIMATION CALLBACK  — called once per frame
# ══════════════════════════════════════════════════════════

def update(frame):
    # Wipe the figure clean so we can draw the current scene from scratch
    fig.clf()
    fig.set_facecolor(BG)

    scene, local, t = get_scene(frame)

    # ──────────────────────────────────────────────────────
    # SCENE 0 ── Title / Introduction
    # ──────────────────────────────────────────────────────
    if scene == 0:
        ax = fig.add_subplot(111, facecolor=BG)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        draw_stars(ax, t)

        ax.text(0.5, 0.80,
                "General Relativity",
                ha="center", va="center", fontsize=36, fontweight="bold",
                color=CYAN, alpha=fade_in(t, delay=0.0, speed=6),
                transform=ax.transAxes)

        ax.text(0.5, 0.69,
                "Spacetime Curvature",
                ha="center", va="center", fontsize=24,
                color=GOLD, alpha=fade_in(t, delay=0.20, speed=5),
                transform=ax.transAxes)

        ax.text(0.5, 0.55,
                "Einstein's core idea  (1915):",
                ha="center", va="center", fontsize=15,
                color=TEXT, alpha=fade_in(t, delay=0.35, speed=5),
                transform=ax.transAxes)

        ax.text(0.5, 0.44,
                '"Mass tells spacetime how to curve;\n'
                ' spacetime tells mass how to move."',
                ha="center", va="center", fontsize=13, style="italic",
                color=GREEN, alpha=fade_in(t, delay=0.45, speed=5),
                transform=ax.transAxes)

        ax.text(0.5, 0.27,
                "Think of spacetime like a stretched rubber sheet.\n"
                "Place a heavy bowling ball on it — the sheet bends downward.\n"
                "A marble placed nearby will roll toward the bowling ball.\n"
                "That rolling is what we call  GRAVITY.",
                ha="center", va="center", fontsize=11,
                color=TEXT, alpha=fade_in(t, delay=0.55, speed=5),
                transform=ax.transAxes)

        ax.text(0.5, 0.06,
                "▶  Watch the next scenes to see this in 3-D!",
                ha="center", va="center", fontsize=11,
                color=PINK, alpha=fade_in(t, delay=0.75, speed=5),
                transform=ax.transAxes)

    # ──────────────────────────────────────────────────────
    # SCENE 1 ── Flat Spacetime  (no mass → no curvature)
    # ──────────────────────────────────────────────────────
    elif scene == 1:
        ax = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        # Draw the FLAT rubber sheet  (Z = 0 everywhere)
        Z_flat = np.zeros_like(X_grid)
        ax.plot_wireframe(X_grid, Y_grid, Z_flat,
                          color=CYAN, linewidth=0.55,
                          alpha=0.75 * fade_in(t, speed=3))

        style_3d_axes(ax,
                      "Scene 1 — Flat Spacetime  (no mass, no gravity)",
                      zlabel="Height")

        # Slowly rotate the view so the student can see it is really flat
        ax.view_init(elev=28, azim=20 + t * 35)

        ax.text2D(0.02, 0.95,
                  "With NO massive objects anywhere,\n"
                  "spacetime is perfectly FLAT.\n\n"
                  "Light and objects travel in perfectly\n"
                  "straight lines — like soldiers\n"
                  "marching across a flat field.",
                  transform=ax.transAxes,
                  color=GREEN, fontsize=10, va="top",
                  alpha=fade_in(t, delay=0.25))

    # ──────────────────────────────────────────────────────
    # SCENE 2 ── Massive Star Warps Spacetime
    # ──────────────────────────────────────────────────────
    elif scene == 2:
        ax = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        # t goes 0 → 1 over the scene, so the dip deepens gradually
        strength = t
        Z_curved = spacetime_dip(strength)

        ax.plot_wireframe(X_grid, Y_grid, Z_curved,
                          color=CYAN, linewidth=0.4, alpha=0.65)

        # ── Draw the star at the bottom of the well ──
        # The star sits at the deepest point (centre, r ≈ 0.35)
        star_z = np.clip(-strength * MASS / 0.35, -MASS * 2.2, 0.1)
        ax.scatter([0], [0], [star_z],
                   color=ORANGE, s=280 * fade_in(t, speed=3),
                   zorder=10, edgecolors=GOLD, linewidths=1.5,
                   label="Massive Star  ☀")

        # Glow rings around the star (decorative)
        for ring_r, ring_alpha in [(0.18, 0.40), (0.32, 0.22)]:
            ang = np.linspace(0, 2 * np.pi, 80)
            ax.plot(ring_r * np.cos(ang),
                    ring_r * np.sin(ang),
                    np.full(80, star_z),
                    color=GOLD, alpha=ring_alpha * fade_in(t, speed=3), lw=1)

        style_3d_axes(ax, "Scene 2 — A Massive Star Bends Spacetime  ☀")
        ax.view_init(elev=30, azim=50 + t * 45)

        ax.text2D(0.02, 0.95,
                  "The orange dot is a massive star (like our Sun).\n\n"
                  "Its enormous mass presses down on spacetime,\n"
                  "creating a deep  'gravitational well'.\n\n"
                  "The deeper the well, the stronger the gravity.\n"
                  "A black hole would make an infinitely deep well!",
                  transform=ax.transAxes,
                  color=GREEN, fontsize=10, va="top",
                  alpha=fade_in(t, delay=0.10))

    # ──────────────────────────────────────────────────────
    # SCENE 3 ── Planet Orbits the Curved Sheet  (geodesic)
    # ──────────────────────────────────────────────────────
    elif scene == 3:
        ax = fig.add_subplot(111, projection="3d")
        ax.set_facecolor(BG)
        fig.patch.set_facecolor(BG)

        strength  = 1.0                # fully curved sheet
        Z_curved  = spacetime_dip(strength)

        # Spacetime grid
        ax.plot_wireframe(X_grid, Y_grid, Z_curved,
                          color=CYAN, linewidth=0.35, alpha=0.45)

        # Star (fixed at centre)
        star_z = np.clip(-strength * MASS / 0.35, -MASS * 2.2, 0.1)
        ax.scatter([0], [0], [star_z],
                   color=ORANGE, s=280, zorder=10,
                   edgecolors=GOLD, linewidths=1.5)

        # ── Full orbit ring (faint dashed guide) ──
        ox_full = ORBIT_R * np.cos(theta_all)
        oy_full = ORBIT_R * np.sin(theta_all)
        oz_full = np.array([planet_position(strength, th)[2]
                             for th in theta_all])
        ax.plot(ox_full, oy_full, oz_full,
                color=PINK, lw=0.9, alpha=0.35, linestyle="--")

        # ── Moving planet  (completes one orbit per scene) ──
        theta_now  = t * 2 * np.pi
        px, py, pz = planet_position(strength, theta_now)

        # Glowing trail (last 60° behind the planet)
        trail_start  = theta_now - np.pi / 3
        trail_angles = np.linspace(trail_start, theta_now, 50)
        t_trail = np.linspace(0.1, 1.0, 50)        # alpha gradient along trail
        trail_x = ORBIT_R * np.cos(trail_angles)
        trail_y = ORBIT_R * np.sin(trail_angles)
        trail_z = np.array([planet_position(strength, th)[2]
                             for th in trail_angles])
        ax.plot(trail_x, trail_y, trail_z,
                color=GOLD, lw=2.5, alpha=0.80)

        # Planet dot
        ax.scatter([px], [py], [pz],
                   color=GOLD, s=130, zorder=11,
                   edgecolors=WHITE, linewidths=1.2)

        # Label the planet
        ax.text(px + 0.1, py + 0.1, pz + 0.08, "🌍 Planet",
                color=GOLD, fontsize=8, zorder=12)

        style_3d_axes(ax, "Scene 3 — Planet Follows a Geodesic Through Curved Spacetime")
        ax.view_init(elev=32, azim=90 + t * 70)

        ax.text2D(0.02, 0.95,
                  "The gold dot is a planet  (like Earth).\n\n"
                  "It is NOT being 'pulled' by the star.\n"
                  "Instead, it follows the straightest possible\n"
                  "path (called a  GEODESIC) on the curved sheet.\n\n"
                  "The curve of the sheet makes the path circular —\n"
                  "THAT is what an orbit really is!",
                  transform=ax.transAxes,
                  color=GREEN, fontsize=10, va="top")

    # ──────────────────────────────────────────────────────
    # SCENE 4 ── Summary  (key takeaways)
    # ──────────────────────────────────────────────────────
    elif scene == 4:
        ax = fig.add_subplot(111, facecolor=BG)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        draw_stars(ax, t)

        ax.text(0.5, 0.93,
                "✅  Key Takeaways",
                ha="center", va="top", fontsize=22, fontweight="bold",
                color=CYAN, alpha=fade_in(t, speed=6),
                transform=ax.transAxes)

        # Each bullet: (emoji + title, explanation)
        bullets = [
            ("🌌  Spacetime",
             "A 4-D fabric — 3 dimensions of space + 1 of time — that everything exists inside."),
            ("⚖️   Mass = Curvature",
             "More mass  →  deeper curve.  Sun curves more than Earth, black hole most of all."),
            ("🌍  Gravity is NOT a Force",
             "It is the shape of curved spacetime.  Objects simply follow that shape."),
            ("🛸  Geodesics",
             "The 'straightest' possible path through curved spacetime.  Orbits are geodesics!"),
            ("📡  Real-world Proof",
             "GPS satellites must correct for curved spacetime every day or navigation fails by kilometres."),
        ]

        for i, (title, desc) in enumerate(bullets):
            y_title = 0.76 - i * 0.14
            y_desc  = y_title - 0.055
            a = fade_in(t, delay=0.08 + i * 0.09, speed=7)
            ax.text(0.06, y_title, title,
                    ha="left", va="center", fontsize=13, fontweight="bold",
                    color=GOLD, alpha=a, transform=ax.transAxes)
            ax.text(0.06, y_desc, desc,
                    ha="left", va="center", fontsize=10.5,
                    color=TEXT, alpha=a, transform=ax.transAxes)

        ax.text(0.5, 0.03,
                "E = mc²   —   A tiny bit of mass holds an enormous amount of energy!",
                ha="center", va="bottom", fontsize=12,
                color=PINK, alpha=fade_in(t, delay=0.75, speed=5),
                transform=ax.transAxes)

    return []


# ══════════════════════════════════════════════════════════
#  BUILD & SAVE THE ANIMATION
# ══════════════════════════════════════════════════════════
print("Building animation …")
print(f"  Total frames : {TOTAL_FRAMES}")
print(f"  Duration     : {TOTAL_FRAMES / FPS:.1f} seconds  @ {FPS} fps")

ani = FuncAnimation(
    fig,
    update,
    frames=TOTAL_FRAMES,
    interval=int(1000 / FPS),   # milliseconds between frames
    blit=False,
    repeat=True,
)

print("\n▶  Opening interactive window — close it to exit.")
plt.tight_layout()
plt.show()

