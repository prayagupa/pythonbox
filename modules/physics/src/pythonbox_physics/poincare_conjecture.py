#!/usr/bin/env python3
"""
Generalized Poincaré Conjecture — Topology Meets Ricci Flow
============================================================

Five-act animation illustrating the core ideas behind one of the most
celebrated theorems in modern mathematics:

  Act I   — A simply-connected closed 3-manifold (bumpy deformed sphere)
  Act II  — Hamilton's Ricci flow evolves the metric toward constant curvature
  Act III — The limiting shape: the round sphere S³
  Act IV  — Loop contraction: π₁(Sⁿ) = 0 — every loop contracts to a point
  Act V   — The generalised statement holds for all n ≥ 1

Mathematical background
-----------------------
The Poincaré Conjecture (now Theorem) states:
    Every compact, simply-connected, closed 3-manifold is homeomorphic
    to the 3-sphere S³.

Key proofs by dimension:
    n ≥ 5 : Smale   (1961)  — via h-cobordism theorem
    n = 4 : Freedman (1982) — via surgery on smooth 4-manifolds
    n = 3 : Perelman (2003) — via Ricci flow with surgery

Ricci flow (Hamilton 1982):
    ∂g/∂t = −2 Ric(g)

    The metric g evolves so that regions of high curvature shrink
    faster, smoothing the manifold.  Perelman showed that singularities
    can be resolved by surgery, and the flow ultimately reaches
    a sphere of constant positive curvature.

Simple connectivity:
    A space is simply connected if every closed loop can be
    continuously contracted to a point — π₁(X) = 0.
    The sphere Sⁿ (n ≥ 2) is the canonical simply-connected manifold.

Run:
    python modules/physics/src/pythonbox_physics/poincare_conjecture.py

Output: poincare_conjecture.gif  (same directory as this script)

Dependencies: numpy, matplotlib, pillow  (all in requirements.txt)
"""

import numpy as np
import matplotlib

# ── macOS / headless backend fallback ────────────────────────────────────────
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _probe  # noqa: F401
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap, Normalize
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3-D projection
from pathlib import Path

# ── Output path ───────────────────────────────────────────────────────────────
OUT_PATH: Path = Path(__file__).parent / "poincare_conjecture.gif"

# ── Grid parameters ───────────────────────────────────────────────────────────
NU: int = 42          # colatitude (θ) resolution
NV: int = 42          # longitude  (φ) resolution
N_LOOP: int = 160     # points on the contracting loop
N_KF: int = 64        # Ricci-flow keyframes to precompute

# ── Animation parameters ──────────────────────────────────────────────────────
N_FRAMES: int = 300
FPS: int = 20

# Phase boundaries as fraction of N_FRAMES (0 → 1)
PH_MANIFOLD: float = 0.18   # 0.00 – 0.18 : deformed manifold
PH_FLOW:     float = 0.55   # 0.18 – 0.55 : Ricci flow
PH_SPHERE:   float = 0.64   # 0.55 – 0.64 : round sphere reveal
PH_LOOP:     float = 0.84   # 0.64 – 0.84 : loop contraction
PH_OUTRO:    float = 1.00   # 0.84 – 1.00 : generalised statement

# Camera
AZ_START: float = 25.0
AZ_DRIFT: float = 0.18      # degrees per frame
ELEV: float = 22.0

# Background colour
BG: str = "#020212"

# ── Colormaps ─────────────────────────────────────────────────────────────────
CMAP_COLD: LinearSegmentedColormap = LinearSegmentedColormap.from_list(
    "pc_cold",
    [
        "#060620",   # very dark navy
        "#0d1a66",
        "#1a33bb",
        "#2255ee",
        "#4488ff",
        "#88bbff",
    ],
)

CMAP_FLOW: LinearSegmentedColormap = LinearSegmentedColormap.from_list(
    "pc_flow",
    [
        "#0a0855",   # deep indigo   (negative curvature)
        "#1155cc",   # blue
        "#00aaee",   # cyan
        "#00cc88",   # sea-green
        "#aadd00",   # lime
        "#ffcc00",   # gold
        "#ff7700",   # orange
        "#ee1100",   # red           (high positive curvature)
    ],
)

CMAP_WARM: LinearSegmentedColormap = LinearSegmentedColormap.from_list(
    "pc_warm",
    [
        "#100018",   # very dark purple
        "#3a0066",
        "#7711bb",
        "#cc44ff",   # vivid violet
        "#ffaaff",   # pink-lavender
        "#ffffff",   # white (peak curvature)
    ],
)

LOOP_COL: str = "#00ffcc"    # neon teal for the contracting loop

# ── Angular grid ──────────────────────────────────────────────────────────────
_u = np.linspace(3e-3, np.pi - 3e-3, NU)   # colatitude (avoids poles)
_v = np.linspace(0.0, 2.0 * np.pi, NV)     # longitude
U, V = np.meshgrid(_u, _v, indexing="ij")

# ── Radial perturbation (simply-connected bumpy sphere) ───────────────────────

def _make_perturbation(
    U: np.ndarray, V: np.ndarray
) -> np.ndarray:
    """
    Superposition of low-degree spherical-harmonic-like modes.
    The resulting surface is topologically a sphere (genus 0, simply
    connected) — it can be continuously deformed to a round sphere
    without tearing or gluing.
    """
    return (
          0.30 * np.sin(2.0 * U) * np.cos(V)
        + 0.20 * np.cos(3.0 * U)
        + 0.14 * np.sin(U) * np.sin(2.0 * V)
        + 0.09 * np.sin(4.0 * U) * np.cos(3.0 * V)
        + 0.07 * np.cos(2.0 * U) * np.sin(3.0 * V)
        + 0.05 * np.sin(5.0 * U) * np.cos(V)
    )


DELTA: np.ndarray = _make_perturbation(U, V)


def _surface_xyz(t: float) -> tuple:
    """
    Parametric surface at Ricci-flow time t ∈ [0, 1].
    t = 0 → maximally deformed manifold.
    t = 1 → unit sphere.
    A smoothstep envelope gives physically natural deceleration.
    """
    s = t * t * (3.0 - 2.0 * t)            # smoothstep S-curve
    r = 1.0 + (1.0 - s) ** 2 * DELTA
    return (
        r * np.sin(U) * np.cos(V),
        r * np.sin(U) * np.sin(V),
        r * np.cos(U),
    )


# ── Gaussian curvature (numerical) ───────────────────────────────────────────

def _gaussian_curvature(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
) -> np.ndarray:
    """
    Numerically estimated Gaussian curvature K via the first and second
    fundamental forms, using finite-difference partial derivatives.

    K = (L·N - M²) / (E·G - F²)

    where E, F, G are first-fundamental-form coefficients and L, M, N
    are second-fundamental-form coefficients.
    """
    Xu = np.gradient(X, axis=0)
    Yu = np.gradient(Y, axis=0)
    Zu = np.gradient(Z, axis=0)
    Xv = np.gradient(X, axis=1)
    Yv = np.gradient(Y, axis=1)
    Zv = np.gradient(Z, axis=1)

    # Unit surface normal  N̂ = (rᵤ × rᵥ) / |rᵤ × rᵥ|
    Nx = Yu * Zv - Zu * Yv
    Ny = Zu * Xv - Xu * Zv
    Nz = Xu * Yv - Yu * Xv
    mag = np.sqrt(Nx**2 + Ny**2 + Nz**2) + 1e-12
    Nx /= mag
    Ny /= mag
    Nz /= mag

    Xuu = np.gradient(Xu, axis=0)
    Yuu = np.gradient(Yu, axis=0)
    Zuu = np.gradient(Zu, axis=0)
    Xuv = np.gradient(Xu, axis=1)
    Yuv = np.gradient(Yu, axis=1)
    Zuv = np.gradient(Zu, axis=1)  # noqa: F841
    Xvv = np.gradient(Xv, axis=1)
    Yvv = np.gradient(Yv, axis=1)
    Zvv = np.gradient(Zv, axis=1)

    # First fundamental form
    E_ = Xu * Xu + Yu * Yu + Zu * Zu
    F_ = Xu * Xv + Yu * Yv + Zu * Zv
    G_ = Xv * Xv + Yv * Yv + Zv * Zv

    # Second fundamental form
    L_ = Xuu * Nx + Yuu * Ny + Zuu * Nz
    M_ = Xuv * Nx + Yuv * Ny + Zuv * Nz
    N_ff = Xvv * Nx + Yvv * Ny + Zvv * Nz

    K = (L_ * N_ff - M_**2) / (E_ * G_ - F_**2 + 1e-12)
    return K


def _face_colors(K: np.ndarray, cmap: LinearSegmentedColormap,
                 norm: Normalize) -> np.ndarray:
    """
    Average vertex curvatures to quad-face centres, then map through cmap.
    Returns RGBA array of shape (NU-1, NV-1, 4) matching plot_surface faces.
    """
    K_face = 0.25 * (
        K[:-1, :-1] + K[1:, :-1] + K[:-1, 1:] + K[1:, 1:]
    )
    return cmap(norm(K_face))


# ── Pre-computation ───────────────────────────────────────────────────────────
print("Pre-computing Ricci-flow keyframes …")

_surfaces: list = []
_curvatures: list = []
_T_VALS: np.ndarray = np.linspace(0.0, 1.0, N_KF)

for _i, _t in enumerate(_T_VALS):
    _X, _Y, _Z = _surface_xyz(_t)
    _K = _gaussian_curvature(_X, _Y, _Z)
    _surfaces.append((_X, _Y, _Z))
    _curvatures.append(_K)
    if _i % 16 == 0:
        print(f"  keyframe {_i:3d}/{N_KF}  t_flow = {_t:.3f}")

print(f"All {N_KF} keyframes ready.")

# Clipped global curvature range for consistent colormap normalisation
_K_flat = np.concatenate([k.ravel() for k in _curvatures])
_K_LO, _K_HI = np.percentile(_K_flat, 2), np.percentile(_K_flat, 98)
_NORM = Normalize(vmin=_K_LO, vmax=_K_HI)

print("Pre-computing face colours for all colormaps …")
_fc_cold: list = [
    _face_colors(_curvatures[i], CMAP_COLD, _NORM) for i in range(N_KF)
]
_fc_flow: list = [
    _face_colors(_curvatures[i], CMAP_FLOW, _NORM) for i in range(N_KF)
]
_fc_warm: list = [
    _face_colors(_curvatures[i], CMAP_WARM, _NORM) for i in range(N_KF)
]
print("Face colour cache ready.")

# ── Loop geometry ─────────────────────────────────────────────────────────────

def _loop_xyz(lat_frac: float, r: float = 1.04) -> tuple:
    """
    Latitude circle at colatitude θ = (π/2) × lat_frac, floating
    just above the sphere surface (r slightly > 1).
    lat_frac = 1.0 → equator;  lat_frac = 0.0 → north pole.
    """
    theta_c = 0.5 * np.pi * lat_frac
    phi_c = np.linspace(0.0, 2.0 * np.pi, N_LOOP)
    sin_t = np.sin(theta_c)
    cos_t = np.cos(theta_c)
    return (
        r * sin_t * np.cos(phi_c),
        r * sin_t * np.sin(phi_c),
        r * cos_t * np.ones_like(phi_c),
    )


# ── Figure & axes ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 8.5), facecolor=BG)
ax = fig.add_axes([0.0, 0.06, 1.0, 0.88], projection="3d")
ax.set_facecolor(BG)
ax.set_axis_off()

for _pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    _pane.fill = False
    _pane.set_edgecolor("none")
ax.grid(False)

_lim = 1.75
ax.set_xlim(-_lim, _lim)
ax.set_ylim(-_lim, _lim)
ax.set_zlim(-_lim, _lim)

# ── Text elements ─────────────────────────────────────────────────────────────
_txt_title = fig.text(
    0.5, 0.968,
    "Generalized Poincaré Conjecture",
    ha="center", va="top",
    fontsize=22, color="#dde0ff",
    fontfamily="serif", style="italic", fontweight="bold",
)
_txt_sub = fig.text(
    0.5, 0.924,
    "Every simply-connected closed n-manifold is homeomorphic to Sⁿ",
    ha="center", va="top",
    fontsize=12, color="#7788aa",
    fontfamily="serif",
)
_txt_phase = fig.text(
    0.5, 0.042,
    "",
    ha="center", va="bottom",
    fontsize=12, color="#44ccff",
    fontfamily="monospace",
)
_txt_attr = fig.text(
    0.5, 0.008,
    "Smale 1961  (n ≥ 5)   ·   Freedman 1982  (n = 4)   ·   "
    "Perelman 2003  (n = 3)",
    ha="center", va="bottom",
    fontsize=8.5, color="#334455",
    fontfamily="serif",
)

# ── Surface holder ────────────────────────────────────────────────────────────
_surf = [None]

# ── Loop glow artists (three overlaid layers + head dot) ──────────────────────
_l_glow, = ax.plot(
    [], [], [], "-", color=LOOP_COL, lw=10.0,
    alpha=0.0, solid_capstyle="round", zorder=3,
)
_l_mid, = ax.plot(
    [], [], [], "-", color=LOOP_COL, lw=3.8,
    alpha=0.0, solid_capstyle="round", zorder=4,
)
_l_core, = ax.plot(
    [], [], [], "-", color="#ffffff", lw=1.1,
    alpha=0.0, solid_capstyle="round", zorder=5,
)
_l_dot, = ax.plot(
    [], [], [], "o", color="#ffffff", ms=9,
    markeredgecolor=LOOP_COL, markeredgewidth=2.2,
    alpha=0.0, zorder=6,
)

# ── Surface drawing helper ────────────────────────────────────────────────────

def _redraw_surface(t_flow: float, cmap_key: str) -> None:
    """
    Remove the previous surface artist and draw a new one at the given
    Ricci-flow time, coloured by Gaussian curvature via *cmap_key*.
    """
    idx = int(np.clip(t_flow, 0.0, 1.0) * (N_KF - 1))
    X, Y, Z = _surfaces[idx]
    fc_map = {"cold": _fc_cold, "flow": _fc_flow, "warm": _fc_warm}
    fc = fc_map[cmap_key][idx]

    if _surf[0] is not None:
        try:
            _surf[0].remove()
        except Exception:
            pass

    _surf[0] = ax.plot_surface(
        X, Y, Z,
        facecolors=fc,
        rstride=1, cstride=1,
        linewidth=0, antialiased=True,
        alpha=0.90,
    )


# ── Animation update ──────────────────────────────────────────────────────────

def _update(frame: int) -> list:
    frac = frame / N_FRAMES

    # ── Phase dispatch ────────────────────────────────────────────────────────
    if frac < PH_MANIFOLD:
        t_flow = 0.0
        cmap_key = "cold"
        label = "Act I — Simply-connected closed 3-manifold  (deformed S³)"
        show_loop = False
        loop_p = 0.0

    elif frac < PH_FLOW:
        p = (frac - PH_MANIFOLD) / (PH_FLOW - PH_MANIFOLD)
        t_flow = p
        cmap_key = "flow" if p >= 0.12 else "cold"
        label = f"Act II — Ricci Flow  ▸  t = {p:.2f}  (curvature equalising …)"
        show_loop = False
        loop_p = 0.0

    elif frac < PH_SPHERE:
        t_flow = 1.0
        cmap_key = "warm"
        label = "Act III — S³ : round sphere of constant positive curvature"
        show_loop = False
        loop_p = 0.0

    elif frac < PH_LOOP:
        p = (frac - PH_SPHERE) / (PH_LOOP - PH_SPHERE)
        t_flow = 1.0
        cmap_key = "warm"
        label = "Act IV — π₁(Sⁿ) = 0 : every loop is contractible"
        show_loop = True
        loop_p = p

    else:
        t_flow = 1.0
        cmap_key = "warm"
        label = (
            "Act V — ∀ n ≥ 1 :  "
            "simply-connected closed n-manifold  ≅  Sⁿ"
        )
        show_loop = False
        loop_p = 0.0

    # ── Surface ───────────────────────────────────────────────────────────────
    _redraw_surface(t_flow, cmap_key)

    # ── Contracting loop ──────────────────────────────────────────────────────
    if show_loop:
        # First 28 % of loop phase: loop rests at equator (fade-in)
        # Remaining 72 %: loop contracts smoothly to north pole
        if loop_p < 0.28:
            lat_frac = 1.0
            af = min(1.0, loop_p / 0.09)
        else:
            q = (loop_p - 0.28) / 0.72
            ease = q * q * (3.0 - 2.0 * q)   # smoothstep contraction
            lat_frac = 1.0 - ease
            # fade out in the final 10 %
            af = 1.0 if q < 0.90 else max(0.0, (1.0 - q) / 0.10)

        lx, ly, lz = _loop_xyz(lat_frac)

        for artist, xy, xyz_prop in [
            (_l_glow, (lx, ly), lz),
            (_l_mid,  (lx, ly), lz),
            (_l_core, (lx, ly), lz),
        ]:
            artist.set_data(*xy)
            artist.set_3d_properties(xyz_prop)

        _l_dot.set_data([lx[0]], [ly[0]])
        _l_dot.set_3d_properties([lz[0]])

        _l_glow.set_alpha(0.13 * af)
        _l_mid.set_alpha(0.56 * af)
        _l_core.set_alpha(0.93 * af)
        _l_dot.set_alpha(0.90 * af)
    else:
        for _a in (_l_glow, _l_mid, _l_core, _l_dot):
            _a.set_alpha(0.0)

    # ── Camera rotation ───────────────────────────────────────────────────────
    ax.view_init(elev=ELEV, azim=AZ_START + frame * AZ_DRIFT)

    # ── Phase label ───────────────────────────────────────────────────────────
    _txt_phase.set_text(label)

    return [_l_glow, _l_mid, _l_core, _l_dot, _txt_phase]


# ── Render ────────────────────────────────────────────────────────────────────
print(f"Rendering {N_FRAMES} frames to GIF …")

anim = animation.FuncAnimation(
    fig, _update,
    frames=N_FRAMES,
    interval=1000 // FPS,
    blit=False,
)

anim.save(str(OUT_PATH), writer=animation.PillowWriter(fps=FPS))
print(f"Saved → {OUT_PATH}")
print("Displaying animation in UI window …")
plt.show()
plt.close(fig)

if __name__ == "__main__":
    pass

