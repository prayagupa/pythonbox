"""
rotating_tesseract.py — Visually Appealing Rotating Tesseract (4D Hypercube)
=============================================================================
A tesseract (4D hypercube) is simultaneously rotated in two orthogonal
4D planes (XW and YZ), then perspective-projected to 3D for display.

Features:
  • Simultaneous rotation in XW, YZ and ZW planes at different speeds
  • Perspective projection: 4D → 3D  (w-depth gives size variation)
  • Semi-transparent face panels on all 24 square faces
  • Three-tier neon colouring:
        cyan   – inner cube  (w = −1 face)
        coral  – outer cube  (w = +1 face)
        purple – bridging edges (connect the two cubes through 4D)
  • Glowing vertex dots
  • Dark space background

Run:  python rotating_tesseract.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d import Axes3D          # noqa: F401  (registers projection)
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from itertools import product, combinations

# ══════════════════════════════════════════════════════════════════════════════
# Tesseract geometry
# ══════════════════════════════════════════════════════════════════════════════

# 16 vertices: every combination of (±1, ±1, ±1, ±1)
VERTS_4D = np.array(list(product([-1.0, 1.0], repeat=4)))   # (16, 4)

# Edges: two vertices share an edge ↔ they differ in exactly one coordinate
EDGES = [
    (i, j)
    for i in range(16)
    for j in range(i + 1, 16)
    if int(np.sum(np.abs(VERTS_4D[i] - VERTS_4D[j]))) == 2       # 32 edges
]

def _edge_type(i: int, j: int) -> str:
    wi, wj = VERTS_4D[i, 3], VERTS_4D[j, 3]
    if wi < 0 and wj < 0:  return "inner"
    if wi > 0 and wj > 0:  return "outer"
    return "bridge"

EDGE_TYPES = [_edge_type(i, j) for i, j in EDGES]

EDGE_STYLE = {
    "inner":  dict(color="#4D9FFF", lw=2.0, alpha=0.95),   # blue (same as outer)
    "outer":  dict(color="#4D9FFF", lw=2.0, alpha=0.95),   # blue
    "bridge": dict(color="#2DDF6A", lw=1.4, alpha=0.85),   # green
}

# ── 24 square faces of the tesseract ─────────────────────────────────────────
# A face is defined by fixing 2 of the 4 axes and letting the other 2 vary.
# Vertices are ordered as a proper quad (CCW).
FACES_4D: list[list[int]] = []
FACE_TYPES: list[str]     = []

for _fixed_axes in combinations(range(4), 2):
    _free_axes = [ax for ax in range(4) if ax not in _fixed_axes]
    for _fixed_vals in product([-1.0, 1.0], repeat=2):
        _quad_offsets = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
        _face_idx: list[int] = []
        for _fv in _quad_offsets:
            _v = np.zeros(4)
            for _ii, _ax in enumerate(_fixed_axes):
                _v[_ax] = _fixed_vals[_ii]
            for _ii, _ax in enumerate(_free_axes):
                _v[_ax] = _fv[_ii]
            _face_idx.append(int(np.where(np.all(VERTS_4D == _v, axis=1))[0][0]))
        FACES_4D.append(_face_idx)
        _fa_list = list(_fixed_axes)
        if 3 in _fa_list:                                   # w is fixed → xyz face
            _w_idx = _fa_list.index(3)
            FACE_TYPES.append("inner" if _fixed_vals[_w_idx] < 0 else "outer")
        else:                                               # w is free → bridge face
            FACE_TYPES.append("bridge")

def _rgba(hex_c: str, a: float) -> tuple:
    r, g, b = mcolors.to_rgb(hex_c)
    return (r, g, b, a)

FACE_RGBA = {
    "inner":  _rgba("#4D9FFF", 0.35),   # blue (same as outer)
    "outer":  _rgba("#4D9FFF", 0.35),   # blue
    "bridge": _rgba("#2DDF6A", 0.20),   # green
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
    scale = 1.0 / (W_DIST - w)
    return verts4[:, :3] * scale[:, np.newaxis]

# ══════════════════════════════════════════════════════════════════════════════
# Figure / axes
# ══════════════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(8, 8), facecolor="#0d1117")
ax  = fig.add_subplot(111, projection="3d")
ax.set_facecolor("#0d1117")

for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    pane.fill = False
    pane.set_edgecolor("none")

ax.set_axis_off()
ax.grid(False)

PAD = 1.1
ax.set_xlim(-PAD, PAD)
ax.set_ylim(-PAD, PAD)
ax.set_zlim(-PAD, PAD)

ax.set_title(
    "Maya",
    color="#FF9500", fontsize=13, fontweight="bold", pad=14,
)


# ══════════════════════════════════════════════════════════════════════════════
# Face helper
# ══════════════════════════════════════════════════════════════════════════════

def make_face_poly(v3: np.ndarray) -> Poly3DCollection:
    """Build a Poly3DCollection for all 24 projected tesseract faces."""
    verts      = [[v3[i] for i in face] for face in FACES_4D]
    facecolors = [FACE_RGBA[ft] for ft in FACE_TYPES]
    poly = Poly3DCollection(verts, facecolors=facecolors,
                            edgecolors="none", linewidths=0)
    return poly

# ══════════════════════════════════════════════════════════════════════════════
# Pre-build artist objects (mutate each frame — much faster than re-adding)
# ══════════════════════════════════════════════════════════════════════════════

# Initial face panels
_v3_init = project(VERTS_4D)
poly_ref  = [make_face_poly(_v3_init)]
ax.add_collection3d(poly_ref[0])

# Edge lines
line_objs = []
for etype in EDGE_TYPES:
    st = EDGE_STYLE[etype]
    ln, = ax.plot([], [], [],
                  color=st["color"], lw=st["lw"], alpha=st["alpha"],
                  solid_capstyle="round")
    line_objs.append(ln)

# Vertex dots — coloured to match their cube (inner=red, outer=blue)
_VERT_COLORS = [EDGE_STYLE["inner"]["color"] if VERTS_4D[k, 3] < 0
                else EDGE_STYLE["outer"]["color"]
                for k in range(len(VERTS_4D))]

dot_objs = [
    ax.plot([], [], [], "o",
            color=_VERT_COLORS[k], markersize=5, alpha=0.95, zorder=6)[0]
    for k in range(len(VERTS_4D))
]

# ══════════════════════════════════════════════════════════════════════════════
# Animation
# ══════════════════════════════════════════════════════════════════════════════

FRAMES = 480
SPEED  = 0.60   # fraction of 2π completed per loop  → very slow

def update(frame: int):
    t  = frame / FRAMES * 2 * np.pi * SPEED

    # Compound 4D rotation across three planes at different rates
    R  = rot4d("xw", t) @ rot4d("yz", t * 0.6) @ rot4d("zw", t * 0.3)
    v3 = project(VERTS_4D @ R.T)       # (16, 3)

    # Rebuild face panels (remove old, add new)
    poly_ref[0].remove()
    new_poly = make_face_poly(v3)
    ax.add_collection3d(new_poly)
    poly_ref[0] = new_poly

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

# ── Save as GIF ───────────────────────────────────────────────────────────────
GIF_PATH = "rotating_tesseract_maya.gif"
print(f"Saving animation to {GIF_PATH} …")
writer = animation.PillowWriter(fps=30)
ani.save(GIF_PATH, writer=writer, dpi=100)
print(f"Saved → {GIF_PATH}")

plt.show()
