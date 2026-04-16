#!/usr/bin/env python3
"""
Schwarzschild Gravitational Lensing — Visual Animation
═══════════════════════════════════════════════════════
A visually appealing, educational animation of gravitational lensing
by a Schwarzschild (non-rotating) black hole.

- Shows how background starlight is bent into arcs and rings
- Demonstrates Einstein rings, multiple images, and photon sphere
- Designed for clarity and beauty, not full ray-tracing accuracy

Output: schwarzschild_lensing.gif (same directory as this script)
"""

import os
import numpy as np
import matplotlib

# macOS-friendly backend fallback
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _test_plt
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle

# ─────────────────────────────────────────────────────────────
#  PARAMETERS
# ─────────────────────────────────────────────────────────────

BG = "#070a13"
BLACK = "#111"
RED = "#e63946"      # Event horizon
ORANGE = "#ff8c42"   # Photon sphere
GREEN = "#43ff64"    # Einstein ring
WHITE = "#fff"

RS = 1.0  # Schwarzschild radius (arbitrary units)
PHOTON_SPHERE = 1.5 * RS

NFR = 96
FPS = 24
SAVE_DPI = 110

# ─────────────────────────────────────────────────────────────
#  STAR FIELD
# ─────────────────────────────────────────────────────────────
np.random.seed(42)
N_STARS = 700
star_r = np.sqrt(np.random.uniform(0.12, 1.0, N_STARS))
star_theta = np.random.uniform(0, 2 * np.pi, N_STARS)
star_x = star_r * np.cos(star_theta)
star_y = star_r * np.sin(star_theta)
star_size = np.random.uniform(4, 16, N_STARS)
star_colors = np.column_stack([
    0.7 + 0.3 * np.random.rand(N_STARS),
    0.8 + 0.2 * np.random.rand(N_STARS),
    np.ones(N_STARS),
    0.45 + 0.5 * np.random.rand(N_STARS)
])

# ─────────────────────────────────────────────────────────────
#  LENSING FUNCTION (stylized, not full GR)
# ─────────────────────────────────────────────────────────────
def lens_map(x, y, strength=1.0):
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    # Deflection angle: alpha ~ 4GM/(c^2 b) = 2RS/r
    alpha = strength * RS / np.clip(r, RS * 0.18, None)
    # Swirl for visual effect near photon sphere
    swirl = 0.18 * np.exp(-((r - PHOTON_SPHERE) / 0.22)**2)
    theta_lensed = theta + alpha + swirl * np.sin(4 * theta)
    r_lensed = r + 0.13 * alpha
    return r_lensed * np.cos(theta_lensed), r_lensed * np.sin(theta_lensed)

# ─────────────────────────────────────────────────────────────
#  ANIMATION SETUP
# ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)

ax.set_aspect('equal')
ax.set_xlim(-1.25, 1.25)
ax.set_ylim(-1.25, 1.25)
ax.set_facecolor(BG)
ax.axis('off')

# ─────────────────────────────────────────────────────────────
#  ANIMATION CALLBACK
# ─────────────────────────────────────────────────────────────
def update(frame):
    ax.cla()
    ax.set_aspect('equal')
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_facecolor(BG)
    ax.axis('off')

    # Animate lensing strength and source alignment
    t = frame / NFR
    align = 0.5 + 0.5 * np.sin(2 * np.pi * t)
    strength = 0.7 + 0.5 * np.sin(2 * np.pi * t)

    # Lensed star field
    lx, ly = lens_map(star_x, star_y + 0.25 * align, strength=strength)
    ax.scatter(lx, ly, s=star_size, c=star_colors, linewidths=0)

    # Draw black hole (event horizon) - RED
    ax.add_patch(Circle((0, 0), radius=RS, facecolor=BLACK, edgecolor=RED, linewidth=2.2, alpha=1.0, zorder=10))
    # Photon sphere - ORANGE
    ax.add_patch(Circle((0, 0), radius=PHOTON_SPHERE, facecolor='none', edgecolor=ORANGE, linewidth=1.2, alpha=0.7, zorder=9, ls='--'))

    # Einstein ring (when source aligns) - GREEN
    if abs(align - 1.0) < 0.13:
        ax.add_patch(Circle((0, 0), radius=0.98, facecolor='none', edgecolor=GREEN, linewidth=3.5, alpha=0.7, zorder=11))

    # Title and annotation
    ttl1 = "Schwarzschild Gravitational Lensing"
    desc1 = "Starlight bends into arcs and rings\nnear a black hole"
    legend1 = "Event horizon (red)   •   Photon sphere (orange)   •   Einstein ring (green)"

    ttl = ""
    desc = ""
    legend = ""

    ax.text(0, 1.18, ttl, ha='center', color=WHITE, fontsize=18, fontweight='bold')
    ax.text(0, 1.08, desc, ha='center', color=ORANGE, fontsize=11)
    ax.text(0, -1.18, legend,
            ha='center', color=GREEN, fontsize=9)

    return []

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Preparing Schwarzschild lensing animation …")
    ani = FuncAnimation(fig, update, frames=NFR, interval=1000 / FPS, blit=False)
    print("\n▶  Opening interactive window — close it to save GIF.")
    plt.show()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avidhya_schwarzschild_lensing.gif")
    print(f"Rendering → {out}")
    ani.save(
        out,
        writer=PillowWriter(fps=FPS),
        dpi=SAVE_DPI,
        savefig_kwargs={"facecolor": BG},
    )
    print(f"✓ Saved → {out}")
