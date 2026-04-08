"""
rotating_cube.py — Visually Appealing Transparent Rotating Cube in 3D
=======================================================================
A glowing, transparent cube that rotates smoothly on a dark background.

Features:
  • Semi-transparent face panels with gradient-like face colouring
  • Bright neon edge highlights
  • Animated spin (azimuth + slow elevation drift)
  • Dark space-themed background

Run:  python rotating_cube.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ── Cube geometry ─────────────────────────────────────────────────────────────
# 8 vertices of a unit cube centred at the origin
VERTICES = np.array([
    [-1, -1, -1],
    [ 1, -1, -1],
    [ 1,  1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [ 1,  1,  1],
    [-1,  1,  1],
], dtype=float)

# 6 faces, each defined by 4 vertex indices
FACES = [
    [0, 1, 2, 3],   # bottom  (z = -1)
    [4, 5, 6, 7],   # top     (z = +1)
    [0, 1, 5, 4],   # front   (y = -1)
    [2, 3, 7, 6],   # back    (y = +1)
    [0, 3, 7, 4],   # left    (x = -1)
    [1, 2, 6, 5],   # right   (x = +1)
]

# Per-face accent colours (neon palette on dark bg)
FACE_COLORS = [
    "#7B2FBE",   # violet  – bottom
    "#C147E9",   # purple  – top
    "#00D4FF",   # cyan    – front
    "#0096FF",   # blue    – back
    "#FF6B6B",   # coral   – left
    "#FF9F45",   # amber   – right
]

EDGE_COLOR  = "#FFFFFF"   # bright white edges
FACE_ALPHA  = 0.25        # face transparency
EDGE_ALPHA  = 0.90        # edge brightness
EDGE_LW     = 1.6         # edge line width

# ── Figure / axes setup ───────────────────────────────────────────────────────
fig = plt.figure(figsize=(7, 7))
fig.patch.set_facecolor("#0d1117")

ax = fig.add_subplot(111, projection="3d")
ax.set_facecolor("#0d1117")

# Hide pane fills but keep subtle grid lines
for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    pane.fill = False
    pane.set_edgecolor("#1e2230")

ax.tick_params(colors="#3a3f55", labelsize=0, length=0)  # hide tick labels
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])
ax.grid(True, color="#1a1f2e", linewidth=0.4)

# Fix axis limits so the cube stays centred during rotation
PAD = 1.5
ax.set_xlim(-PAD, PAD)
ax.set_ylim(-PAD, PAD)
ax.set_zlim(-PAD, PAD)

# ── Title ─────────────────────────────────────────────────────────────────────
ax.set_title("Transparent Rotating Cube", color="#c9d1d9",
             fontsize=14, fontweight="bold", pad=12)

# ── Helper: build Poly3DCollection for current vertex positions ───────────────

def build_poly(verts: np.ndarray) -> Poly3DCollection:
    """Return a Poly3DCollection for the 6 cube faces."""
    face_verts = [[verts[i] for i in face] for face in FACES]
    poly = Poly3DCollection(
        face_verts,
        facecolors=FACE_COLORS,
        edgecolors=EDGE_COLOR,
        linewidths=EDGE_LW,
        alpha=FACE_ALPHA,
    )
    return poly

# ── Rotation matrices ─────────────────────────────────────────────────────────

def rot_x(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s,  c]])

def rot_y(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[ c, 0, s],
                     [ 0, 1, 0],
                     [-s, 0, c]])

def rot_z(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]])

# ── Initial poly placeholder ──────────────────────────────────────────────────
poly_ref = [build_poly(VERTICES)]
ax.add_collection3d(poly_ref[0])

# ── Animation update ──────────────────────────────────────────────────────────
FRAMES       = 360
AZ_SPEED     = 1.0          # degrees per frame (azimuth)
EL_AMPLITUDE = 20.0         # degrees (elevation oscillation)
EL_FREQ      = 0.5          # oscillation cycles per full rotation

def update(frame: int):
    az_rad = np.deg2rad(frame * AZ_SPEED)
    el_rad = np.deg2rad(EL_AMPLITUDE * np.sin(2 * np.pi * EL_FREQ * frame / FRAMES))

    R = rot_y(az_rad) @ rot_x(el_rad)
    rotated = VERTICES @ R.T

    # Remove old poly and add a fresh one
    poly_ref[0].remove()
    new_poly = build_poly(rotated)
    ax.add_collection3d(new_poly)
    poly_ref[0] = new_poly

    return (new_poly,)

# ── Run animation ─────────────────────────────────────────────────────────────
ani = animation.FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=16,      # ~60 fps
    blit=False,
)

plt.tight_layout()
plt.show()

