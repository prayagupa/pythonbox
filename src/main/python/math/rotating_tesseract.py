"""
rotating_tesseract.py — Visually Appealing Rotating Tesseract (4D Hypercube)
=============================================================================
A tesseract (4D hypercube) is simultaneously rotated in two orthogonal
4D planes (XW and YZ), then perspective-projected to 3D for display.

Features:
  • Simultaneous rotation in XW and YZ planes at different speeds
  • Perspective projection: 4D → 3D  (w-depth gives size variation)
  • Three-tier neon colouring:
        cyan   – inner cube  (w = −1 face)
        coral  – outer cube  (w = +1 face)
        purple – bridging edges (connect the two cubes through 4D)
  • Glowing vertex dots whose size tracks w-depth
  • Dark space background

Run:  python rotating_tesseract.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401  (registers projection)
from itertools import product

# ══════════════════════════════════════════════════════════════════════════════
# Tesseract geometry
# ══════════════════════════════════════════════════════════════════════════════

# 16 vertices: every combination of (±1, ±1, ±1, ±1)
VERTS_4D = np.array(list(product([-1.0, 1.0], repeat=4)))   # (16, 4)

# Two vertices share an edge ↔ they differ in exactly one coordinate
# (their L1 distance == 2 because each coordinate is ±1)
EDGES = [
    (i, j)
    for i in range(16)
    for j in range(i + 1, 16)
    if int(np.sum(np.abs(VERTS_4D[i] - VERTS_4D[j]))) == 2       # 32 edges
]

# Colour by the w-coordinates of each edge's endpoints
def _edge_type(i: int, j: int) -> str:
    wi, wj = VERTS_4D[i, 3], VERTS_4D[j, 3]
    if wi < 0 and wj < 0:  return "inner"
    if wi > 0 and wj > 0:  return "outer"
    return "bridge"

EDGE_TYPES = [_edge_type(i, j) for i, j in EDGES]

EDGE_STYLE = {
    "inner":  dict(color="#00D4FF", lw=2.0, alpha=0.90),   # cyan
    "outer":  dict(color="#FF6B6B", lw=2.0, alpha=0.90),   # coral
    "bridge": dict(color="#C147E9", lw=1.2, alpha=0.55),   # purple
}

# ══════════════════════════════════════════════════════════════════════════════
# 4-D rotation helpers
# ══════════════════════════════════════════════════════════════════════════════

_PLANE_AXES = {"xw": (0, 3), "yz": (1, 2), "xy": (0, 1),
               "xz": (0, 2), "yw": (1, 3), "zw": (2, 3)}

def rot4d(plane: str, theta: float) -> np.ndarray:
    """Return a 4×4 rotation matrix for the given named coordinate plane."""
    R = np.eye(4)
    a, b = _PLANE_AXES[plane]
    c, s = np.cos(theta), np.sin(theta)
    R[a, a] =  c;  R[a, b] = -s
    R[b, a] =  s;  R[b, b] =  c
    return R

# ══════════════════════════════════════════════════════════════════════════════
# Perspective projection: 4D → 3D
# ══════════════════════════════════════════════════════════════════════════════

W_DIST = 3.0   # "camera" distance along the w-axis

def project(verts4: np.ndarray) -> np.ndarray:
    """Perspective-project (N,4) array to (N,3)."""
    w     = verts4[:, 3]
    scale = 1.0 / (W_DIST - w)                       # closer w → bigger
    return verts4[:, :3] * scale[:, np.newaxis]

# ══════════════════════════════════════════════════════════════════════════════
# Figure / axes
# ══════════════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(8, 8), facecolor="#0d1117")
ax  = fig.add_subplot(111, projection="3d")
ax.set_facecolor("#0d1117")

for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    pane.fill = False
    pane.set_edgecolor("#1e2230")

ax.tick_params(labelsize=0, length=0)
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])
ax.grid(True, color="#1a1f2e", linewidth=0.4)

PAD = 1.1
ax.set_xlim(-PAD, PAD)
ax.set_ylim(-PAD, PAD)
ax.set_zlim(-PAD, PAD)

ax.set_title(
    "Rotating Tesseract  ·  4D → 3D Perspective Projection",
    color="#c9d1d9", fontsize=13, fontweight="bold", pad=14,
)

# Legend (text labels in the corner)
legend_items = [
    ("#00D4FF", "inner cube  (w = −1)"),
    ("#FF6B6B", "outer cube  (w = +1)"),
    ("#C147E9", "bridging edges"),
]
for idx, (col, label) in enumerate(legend_items):
    ax.text2D(0.02, 0.12 - idx * 0.055, f"━  {label}",
              transform=ax.transAxes, color=col, fontsize=9, alpha=0.85)

# ══════════════════════════════════════════════════════════════════════════════
# Pre-build artist objects (mutate each frame — much faster than re-adding)
# ══════════════════════════════════════════════════════════════════════════════

line_objs = []
for etype in EDGE_TYPES:
    st = EDGE_STYLE[etype]
    ln, = ax.plot([], [], [],
                  color=st["color"], lw=st["lw"], alpha=st["alpha"],
                  solid_capstyle="round")
    line_objs.append(ln)

# Vertex dots — size will be updated to reflect w-depth each frame
dot_objs = [
    ax.plot([], [], [], "o",
            color="#ffffff", markersize=4, alpha=0.75, zorder=6)[0]
    for _ in range(len(VERTS_4D))
]

# ══════════════════════════════════════════════════════════════════════════════
# Animation
# ══════════════════════════════════════════════════════════════════════════════

FRAMES = 480   # one full loop

def update(frame: int):
    t = frame / FRAMES * 2 * np.pi

    # Compound 4D rotation: XW plane (main spin) + YZ plane (slower tumble)
    R = rot4d("xw", t) @ rot4d("yz", t * 0.6) @ rot4d("zw", t * 0.3)
    v3 = project(VERTS_4D @ R.T)       # (16, 3)

    # Update edge lines
    for idx, (a, b) in enumerate(EDGES):
        line_objs[idx].set_data([v3[a, 0], v3[b, 0]],
                                [v3[a, 1], v3[b, 1]])
        line_objs[idx].set_3d_properties([v3[a, 2], v3[b, 2]])

    # Update vertex dots
    for k, dot in enumerate(dot_objs):
        dot.set_data([v3[k, 0]], [v3[k, 1]])
        dot.set_3d_properties([v3[k, 2]])

    return line_objs + dot_objs

ani = animation.FuncAnimation(
    fig, update,
    frames=FRAMES,
    interval=16,      # ~60 fps
    blit=False,
)

plt.tight_layout()
plt.show()

