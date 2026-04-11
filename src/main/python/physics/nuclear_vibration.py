#!/usr/bin/env python3
"""
Nuclear Vibration Animation  (interactive + GIF)
════════════════════════════════════════════════════════════════════════════════
Collective quadrupole oscillations of an atomic nucleus (¹⁶O, Oxygen-16).

Physics:
  Nuclear surface described by spherical harmonics:
      R(θ,t) = R₀ · [1 + β(t) · Y₂⁰(θ)]
      Y₂⁰(θ) = (3cos²θ − 1) / 2        (ℓ=2, m=0 quadrupole mode)
      β(t)    = β₀ · cos(ω t)           (harmonic oscillation)

  The nucleus alternates between:
      β > 0  →  Prolate (elongated, like a rugby ball)
      β < 0  →  Oblate  (flattened, like a discus)
      β = 0  →  Spherical

Nucleons (protons in red, neutrons in blue) undergo:
  • Collective motion: co-deform with the nuclear surface
  • Thermal vibrations: small random oscillations superimposed

Gamma (γ) rays flash when β is near its extremes (classical turning points).

Output: nuclear_vibration.gif
"""

import numpy as np
import matplotlib
# Switch to an interactive backend before pyplot is imported
try:
    matplotlib.use("MacOSX")      # native macOS window
except Exception:
    try:
        matplotlib.use("TkAgg")   # fallback: needs tkinter
    except Exception:
        pass                      # keep whatever default was set
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import FancyArrowPatch
import warnings

warnings.filterwarnings("ignore")

# ─── Nucleus parameters ────────────────────────────────────────────────────────
A   = 16           # Mass number  (Oxygen-16)
Z   = 8            # Proton number
N_n = A - Z        # Neutron number  = 8
R0  = 1.2 * A**(1/3)          # Nuclear radius ≈ 3.02 fm
BETA0 = 0.42       # Quadrupole deformation amplitude
OMEGA = 2 * np.pi  # Vibration angular frequency [rad / time-unit]

# ─── Animation settings ────────────────────────────────────────────────────────
NFR   = 120        # Total frames (≈ 2 full oscillations)
FPS   = 24
DT    = 2.0 / NFR  # 2 full oscillation cycles per animation

# ─── Colour palette ────────────────────────────────────────────────────────────
BG     = "#04040f"
PROT_C = "#ff3b3b"
NEUT_C = "#3a9dff"
SURF_C = "#33ccff"
GLOW_C = "#0044ff"
GOLD_C = "#ffd700"
TEXT_C = "#ccdcff"
GRID_C = "#1a1a3a"

# ─── Figure layout ────────��────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 7), facecolor=BG)
fig.patch.set_facecolor(BG)

# Main nucleus panel (left)
ax = fig.add_axes([0.03, 0.09, 0.60, 0.84], facecolor=BG)
ax.set_xlim(-6.8, 6.8)
ax.set_ylim(-6.8, 6.8)
ax.set_aspect("equal")
ax.axis("off")

# β(t) time-series panel (top-right)
ax2 = fig.add_axes([0.68, 0.55, 0.29, 0.38], facecolor="#08081a")
ax2.set_facecolor("#08081a")
ax2.tick_params(colors="gray", labelsize=7)
for sp in ax2.spines.values():
    sp.set_color(GRID_C)
ax2.axhline(0,     color=GRID_C, lw=0.8)
ax2.axhline( BETA0, color="#ff333344", lw=0.8, ls="--")
ax2.axhline(-BETA0, color="#3333ff44", lw=0.8, ls="--")
ax2.set_xlim(0, NFR * DT)
ax2.set_ylim(-BETA0 * 1.4, BETA0 * 1.4)
ax2.set_xlabel("time (arb. units)", color="gray", fontsize=7)
ax2.set_ylabel("β(t)", color="gray", fontsize=7)
ax2.set_title("Deformation  β(t) = β₀ cos(ωt)", color=TEXT_C, fontsize=8, pad=4)

# Energy bar panel (bottom-right)
ax3 = fig.add_axes([0.68, 0.09, 0.29, 0.36], facecolor="#08081a")
ax3.set_facecolor("#08081a")
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)
for sp in ax3.spines.values():
    sp.set_color(GRID_C)
ax3.tick_params(colors="gray", labelsize=7)
ax3.axis("off")

# ─── Title & labels ────────────────────────────────────────────────────────────
fig.text(0.03, 0.975, "Nuclear Quadrupole Vibration  ·  ¹⁶O nucleus",
         color="white", fontsize=13, fontweight="bold", va="top")
fig.text(0.03, 0.945, "Collective shape oscillation: Prolate ↕  ↔  Oblate ↔",
         color="#7799cc", fontsize=9, va="top")

# ─── Nucleon initial positions ─────────────────────────────────────────────────
np.random.seed(42)

def _random_in_disk(n, r):
    """Uniform random positions inside a disk of radius r."""
    pts = []
    while len(pts) < n:
        p = np.random.uniform(-r, r, 2)
        if np.linalg.norm(p) < r * 0.88:
            pts.append(p)
    return np.array(pts)

p_pos0  = _random_in_disk(Z,   R0)     # proton  base positions
n_pos0  = _random_in_disk(N_n, R0)     # neutron base positions
p_phase = np.random.uniform(0, 2 * np.pi, Z)
n_phase = np.random.uniform(0, 2 * np.pi, N_n)

# ─── Surface & nucleon kinematics ──────────────────────────────────────────────
THETA = np.linspace(0, 2 * np.pi, 400)

def surface_xy(t):
    """Nuclear surface (quadrupole deformation)."""
    beta_t = BETA0 * np.cos(OMEGA * t)
    Y20    = (3 * np.cos(THETA) ** 2 - 1) / 2.0
    R      = R0 * (1.0 + beta_t * Y20)
    return R * np.cos(THETA), R * np.sin(THETA)

def nucleon_xy(pos0, phases, t):
    """Nucleon positions: collective deformation + thermal vibration."""
    beta_t = BETA0 * np.cos(OMEGA * t)
    amp    = 0.14
    x = pos0[:, 0] * (1.0 + 0.55 * beta_t) + amp * np.cos(phases + 4.7 * t)
    y = pos0[:, 1] * (1.0 - 0.55 * beta_t) + amp * np.sin(phases + 4.7 * t)
    return x, y

# ─── Glow effect (concentric scaled copies of the surface) ─────────────────────
N_GLOW   = 12
GLOW_MAX = 0.07   # peak alpha per layer
glow_arts = []
for i in range(N_GLOW, 0, -1):
    alpha = GLOW_MAX * (i / N_GLOW) ** 1.5
    scale = 1.0 + 0.055 * i
    patch = plt.Polygon([[0, 0]], closed=True,
                         color=GLOW_C, alpha=alpha, zorder=1)
    ax.add_patch(patch)
    patch.set_animated(True)
    glow_arts.append((patch, scale))

# ─── Core fill & outline ───────────────────────────────────────────────────────
core_fill = plt.Polygon([[0, 0]], closed=True,
                          facecolor="#00082a", edgecolor="none",
                          alpha=0.80, zorder=2)
ax.add_patch(core_fill)
core_fill.set_animated(True)

inner_fill = plt.Polygon([[0, 0]], closed=True,
                           facecolor="#001a55", edgecolor="none",
                           alpha=0.45, zorder=3)
ax.add_patch(inner_fill)
inner_fill.set_animated(True)

surf_line, = ax.plot([], [], color=SURF_C, lw=2.0, alpha=0.95, zorder=4, animated=True)
inner_line, = ax.plot([], [], color="#66aaff", lw=0.7, alpha=0.45,
                       ls="--", zorder=4, animated=True)

# ─── Nucleon scatters ──────────────────────────────────────────────────────────
p_scat = ax.scatter([], [], s=115, c=PROT_C, zorder=7,
                     edgecolors="#ffaaaa", linewidths=0.7)
p_scat.set_animated(True)
n_scat = ax.scatter([], [], s=115, c=NEUT_C, zorder=7,
                     edgecolors="#aaccff", linewidths=0.7)
n_scat.set_animated(True)

# ─── Axis indicators (semi-axis markers) ──────────────────────────────────────
arrow_kw = dict(arrowstyle="<->", color="#ffffff44", lw=0.8)
a_arrow = FancyArrowPatch((0, 0), (1, 0), **arrow_kw, zorder=8)
b_arrow = FancyArrowPatch((0, 0), (0, 1), **arrow_kw, zorder=8)
ax.add_patch(a_arrow)
ax.add_patch(b_arrow)
a_arrow.set_animated(True)
b_arrow.set_animated(True)
a_label = ax.text(0, 0, "", color="#ffffff88", fontsize=8,
                  ha="center", va="top", zorder=9, animated=True)
b_label = ax.text(0, 0, "", color="#ffffff88", fontsize=8,
                  ha="left", va="center", zorder=9, animated=True)

# ─── Gamma-ray lines (flash when near extremes) ────────────────────────────────
N_GAMMA = 6
gamma_angles = np.linspace(0, 2 * np.pi, N_GAMMA, endpoint=False) + np.pi / N_GAMMA
gamma_lines  = []
for ang in gamma_angles:
    ln, = ax.plot([], [], color=GOLD_C, lw=1.5, alpha=0.0, zorder=10, animated=True)
    gamma_lines.append((ln, ang))

# ─── Status text ──────────────────────────────────────────────────────────────
status_text = ax.text(0.50, 0.025, "", transform=ax.transAxes,
                      ha="center", va="bottom", color=SURF_C,
                      fontsize=10, fontfamily="monospace", zorder=11, animated=True)

# ─── β(t) history line ────────────────────────────────────────────────────────
bline,     = ax2.plot([], [], color=SURF_C,  lw=1.6, zorder=3, animated=True)
bline_dot, = ax2.plot([], [], "o", color="white", ms=5, zorder=4, animated=True)

# ─── Energy panel content ─────────────────────────────────────────────────────
ax3.set_title("Energy partitioning", color=TEXT_C, fontsize=8, pad=4)
kin_bar  = ax3.barh(0.65, 0, height=0.18, left=0.02,
                     color=PROT_C, alpha=0.85)[0]
kin_bar.set_animated(True)
pot_bar  = ax3.barh(0.35, 0, height=0.18, left=0.02,
                     color=NEUT_C, alpha=0.85)[0]
pot_bar.set_animated(True)
ax3.text(0.02, 0.88, "Kinetic (∝ β̇²)", color="#ffaaaa", fontsize=7, va="center")
ax3.text(0.02, 0.15, "Potential (∝ β²)",  color="#aaccff", fontsize=7, va="center")
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)

# ─── Legend ───────────────────────────────────────────────────────────────────
p_patch = mpatches.Patch(color=PROT_C, label=f"Proton  (Z = {Z})")
n_patch = mpatches.Patch(color=NEUT_C, label=f"Neutron (N = {N_n})")
g_patch = mpatches.Patch(color=GOLD_C, label="γ-ray emission")
ax.legend(handles=[p_patch, n_patch, g_patch],
          loc="lower left", facecolor="#0a0a22",
          edgecolor="#334466", labelcolor="white",
          fontsize=9, framealpha=0.85)

# ─── Annotation box (physics labels) ──────────────────────────────────────────
info_lines = [
    f"  A = {A},  Z = {Z},  N = {N_n}",
    f"  R₀ ≈ {R0:.2f} fm",
    f"  β₀ = {BETA0:.2f}",
    "  Mode: ℓ=2, m=0  (E2)",
]
for i, line in enumerate(info_lines):
    fig.text(0.68, 0.07 - i * 0.018, line,
             color="#8899bb", fontsize=7.5, va="top",
             fontfamily="monospace")

# ─── State variables ──────────────────────────────────────────────────────────
beta_hist = []
time_hist = []

# ─── Update function ──────────────────────────────────────────────────────────
def update(frame):
    t      = frame * DT
    beta_t = BETA0 * np.cos(OMEGA * t)
    dbeta  = -BETA0 * OMEGA * np.sin(OMEGA * t)   # β̇

    # ── Nuclear surface
    xs, ys = surface_xy(t)
    verts  = np.column_stack([xs, ys])

    for patch, scale in glow_arts:
        patch.set_xy(np.column_stack([xs * scale, ys * scale]))

    core_fill.set_xy(verts)
    inner_fill.set_xy(np.column_stack([xs * 0.55, ys * 0.55]))
    surf_line.set_data(xs, ys)
    inner_line.set_data(xs * 0.72, ys * 0.72)

    # ── Semi-axis indicators
    #   equatorial radius a (θ=π/2) and polar radius b (θ=0)
    a_rad = R0 * (1.0 + beta_t * ((3 * 0 - 1) / 2.0))   # θ=π/2 → Y20=(0-1)/2
    b_rad = R0 * (1.0 + beta_t * ((3 * 1 - 1) / 2.0))   # θ=0   → Y20=(3-1)/2=1
    a_rad = float(np.abs(a_rad))
    b_rad = float(np.abs(b_rad))
    a_arrow.set_positions((0, -0.25), (a_rad, -0.25))
    b_arrow.set_positions((-0.25, 0), (-0.25, b_rad))
    a_label.set_position((a_rad / 2, -0.9))
    a_label.set_text(f"a={a_rad:.2f}")
    b_label.set_position((-1.1, b_rad / 2))
    b_label.set_text(f"b={b_rad:.2f}")

    # ── Nucleons
    px, py = nucleon_xy(p_pos0, p_phase, t)
    nx, ny = nucleon_xy(n_pos0, n_phase, t)
    p_scat.set_offsets(np.column_stack([px, py]))
    n_scat.set_offsets(np.column_stack([nx, ny]))

    # ── Gamma-ray flashes near extremes (|β| > 0.9 β₀)
    gamma_alpha = max(0.0, (np.abs(beta_t) / BETA0 - 0.88) / 0.12)
    gamma_alpha = float(np.clip(gamma_alpha, 0, 1))
    for ln, ang in gamma_lines:
        r_inner = R0 * 1.05
        r_outer = R0 * (1.9 + 0.6 * gamma_alpha)
        lx = [r_inner * np.cos(ang), r_outer * np.cos(ang)]
        ly = [r_inner * np.sin(ang), r_outer * np.sin(ang)]
        ln.set_data(lx, ly)
        ln.set_alpha(gamma_alpha * 0.9)

    # ── Status text
    if beta_t > 0.015:
        shape = "Prolate  ↕"
    elif beta_t < -0.015:
        shape = "Oblate   ↔"
    else:
        shape = "Spherical ●"
    status_text.set_text(f"β(t) = {beta_t:+.3f}   |   {shape}")

    # ── β(t) history
    time_hist.append(t)
    beta_hist.append(beta_t)
    bline.set_data(time_hist, beta_hist)
    bline_dot.set_data([t], [beta_t])

    # ── Energy bars  (kinetic ∝ β̇², potential ∝ β²)
    E_tot = (BETA0 * OMEGA) ** 2          # constant total energy (proportional)
    E_kin = dbeta ** 2 / E_tot            # normalised [0,1]
    E_pot = (OMEGA * beta_t) ** 2 / E_tot
    kin_bar.set_width(float(np.clip(E_kin * 0.96, 0, 0.96)))
    pot_bar.set_width(float(np.clip(E_pot * 0.96, 0, 0.96)))

    artists = ([core_fill, inner_fill, surf_line, inner_line,
                p_scat, n_scat, status_text,
                bline, bline_dot, kin_bar, pot_bar,
                a_arrow, b_arrow, a_label, b_label]
               + [gp for gp, _ in glow_arts]
               + [ln for ln, _ in gamma_lines])
    return artists


# ─── Animate & save ────────────────────────────────────────────────────────────
print(f"Rendering {NFR} frames  ({NFR / FPS:.1f} s at {FPS} fps) …")
anim = FuncAnimation(fig, update, frames=NFR,
                     interval=1000 // FPS, blit=True)

OUT = "/Users/A1353612/prayag/pythonbox/src/main/python/physics/nuclear_vibration.gif"
print(f"Saving → {OUT}")
anim.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
print("Done ✓")

# ─── Interactive live display ──────────────────────────────────────────────────
# Reset accumulated history so the β(t) plot replays cleanly
beta_hist.clear()
time_hist.clear()

print("Opening interactive window – close it to exit.")
anim_live = FuncAnimation(fig, update, frames=NFR,
                          interval=1000 // FPS, blit=True, repeat=True)
plt.show()
plt.close(fig)

