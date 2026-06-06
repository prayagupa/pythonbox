#!/usr/bin/env python3
"""
Schwarzschild Spacetime — Cinematic Educational Animation
═══════════════════════════════════════════════════════════
A high-school friendly visual tour of the spacetime around a
non-rotating black hole.

What this animation shows:
  1. A Flamm-style embedding diagram of curved space outside the horizon
  2. Gravitational time dilation for a probe moving through the field
  3. A stylised star field distorted by gravitational lensing
  4. A precessing orbit in the strong-field region

Physics note:
  This is a qualitative visualisation inspired by Schwarzschild geometry.
  The embedding surface and lensing panel are designed to be beautiful and
  intuitive rather than a full general-relativistic ray tracer.

Output:  schwarzschild_spacetime.gif  (same directory as this script)
"""

import os
import warnings

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
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — required for 3-D axes

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
#  RUNTIME TUNING
# ──────────────────────────────────────────────────────────────────────────────
PREVIEW = os.environ.get("PYTHONBOX_PREVIEW") == "1"
SHOW_WINDOW = os.environ.get("PYTHONBOX_NO_SHOW") != "1"

NFR = 84 if PREVIEW else 168
FPS = 18 if PREVIEW else 24
DT = 0.085
SAVE_DPI = 85 if PREVIEW else 110

# ──────────────────────────────────────────────────────────────────────────────
#  COLOUR PALETTE
# ──────────────────────────────────────────────────────────────────────────────
BG = "#02030a"
PANEL = "#060914"
TEXT = "#dce8ff"
MUTED = "#8ea3c7"
CYAN = "#50e3ff"
DEEP_CYAN = "#118ab2"
GOLD = "#ffd166"
ORANGE = "#ff8c42"
PINK = "#ff4d9d"
PURPLE = "#9d4edd"
WHITE = "#ffffff"
HORIZON = "#090909"

# ──────────────────────────────────────────────────────────────────────────────
#  SCHWARZSCHILD PARAMETERS  (geometric units: G = c = 1)
# ──────────────────────────────────────────────────────────────────────────────
MASS = 1.0
RS = 2.0 * MASS                     # Schwarzschild radius = 2M
PHOTON_SPHERE = 1.5 * RS            # r = 3M
ISCO = 3.0 * RS                     # innermost stable circular orbit = 6M
R_MAX = 9.0 * RS

# ──────────────────────────────────────────────────────────────────────────────
#  PRECOMPUTED GRIDS FOR THE EMBEDDING DIAGRAM
# ──────────────────────────────────────────────────────────────────────────────
R_STEPS = 40 if PREVIEW else 58
TH_STEPS = 96 if PREVIEW else 144
r = np.linspace(RS * 1.01, R_MAX, R_STEPS)
th = np.linspace(0, 2 * np.pi, TH_STEPS)
R, TH = np.meshgrid(r, th)
X = R * np.cos(TH)
Y = R * np.sin(TH)


def embedding_height(radius):
    """Flamm paraboloid height, inverted to look like a gravitational well."""
    safe_r = np.maximum(radius, RS * 1.0001)
    return -2.0 * np.sqrt(RS * (safe_r - RS))


Z = embedding_height(R)

# ──────────────────────────────────────────────────────────────────────────────
#  ORBIT / PROBE TRAJECTORY  (qualitative precessing strong-field orbit)
# ──────────────────────────────────────────────────────────────────────────────
phase = np.linspace(0.0, 1.0, NFR)
orbit_theta = np.linspace(0.0, 4.8 * np.pi, NFR)
ecc = 0.34
precession = 0.18
semi_latus = 4.55 * RS
orbit_r = semi_latus / (1.0 + ecc * np.cos((1.0 - precession) * orbit_theta))
orbit_x = orbit_r * np.cos(orbit_theta)
orbit_y = orbit_r * np.sin(orbit_theta)
orbit_z = embedding_height(orbit_r)


def time_rate(radius):
    """Proper-time rate dτ/dt for a stationary observer at radius r."""
    safe_r = np.maximum(radius, RS * 1.0001)
    return np.sqrt(np.clip(1.0 - RS / safe_r, 0.0, None))


rate_curve_r = np.linspace(RS * 1.03, R_MAX, 500)
rate_curve = time_rate(rate_curve_r)
probe_rate = time_rate(orbit_r)
coord_time = np.arange(NFR) * DT
probe_time = np.concatenate(([0.0], np.cumsum(probe_rate[:-1] * DT)))
clock_gap = coord_time - probe_time

# ──────────────────────────────────────────────────────────────────────────────
#  STARS FOR THE LENSING PANEL
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(7)
N_STARS = 900
star_r = np.sqrt(np.random.uniform(0.08, 1.0, N_STARS))
star_theta = np.random.uniform(0.0, 2 * np.pi, N_STARS)
star_x = 1.12 * star_r * np.cos(star_theta)
star_y = 1.12 * star_r * np.sin(star_theta)
star_size = np.random.uniform(3.0, 17.0, N_STARS)
star_tone = np.random.uniform(0.65, 1.0, N_STARS)
star_colors = np.column_stack([
    0.72 * star_tone + 0.28,
    0.80 * star_tone + 0.20,
    1.00 * np.ones_like(star_tone),
    np.random.uniform(0.35, 0.95, N_STARS),
])


def lens_stars(warp_phase):
    """Stylised lensing map: magnification + azimuthal swirl near the hole."""
    rr = np.sqrt(star_x**2 + star_y**2)
    ang = np.arctan2(star_y, star_x)

    pulse = 0.5 + 0.5 * np.sin(2 * np.pi * warp_phase)
    magnification = 1.0 + (0.18 + 0.05 * pulse) / (rr**2 + 0.08)
    swirl = (0.14 + 0.05 * np.cos(2 * np.pi * warp_phase)) / (rr + 0.12)
    swirl += 0.05 * np.sin(6 * ang + 2 * np.pi * warp_phase)

    new_r = np.clip(rr * magnification, 0.0, 1.6)
    new_ang = ang + swirl
    lx = new_r * np.cos(new_ang)
    ly = new_r * np.sin(new_ang)

    keep = new_r <= 1.35
    return lx[keep], ly[keep], star_size[keep], star_colors[keep]


# ──────────────────────────────────────────────────────────────────────────────
#  PANEL HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def style_panel(ax, title, xlabel="", ylabel=""):
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=TEXT, fontsize=11.5, pad=8)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#172338")
        spine.set_linewidth(0.9)
    if xlabel:
        ax.set_xlabel(xlabel, color=TEXT, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, color=TEXT, fontsize=9)
    ax.grid(color="#122033", alpha=0.45, linewidth=0.6)


# ──────────────────────────────────────────────────────────────────────────────
#  FIGURE
# ──────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 9), facecolor=BG)


# ──────────────────────────────────────────────────────────────────────────────
#  ANIMATION CALLBACK
# ──────────────────────────────────────────────────────────────────────────────
def update(frame):
    fig.clf()
    fig.set_facecolor(BG)

    gs = gridspec.GridSpec(
        2, 2, figure=fig,
        left=0.045, right=0.975, top=0.90, bottom=0.075,
        hspace=0.24, wspace=0.12,
    )

    ax_embed = fig.add_subplot(gs[0, 0], projection="3d")
    ax_clock = fig.add_subplot(gs[0, 1])
    ax_lens = fig.add_subplot(gs[1, 0])
    ax_orbit = fig.add_subplot(gs[1, 1])

    t = phase[frame]
    x_now = orbit_x[frame]
    y_now = orbit_y[frame]
    z_now = orbit_z[frame]
    r_now = orbit_r[frame]
    rate_now = probe_rate[frame]

    fig.suptitle(
        "Schwarzschild Spacetime  —  Curvature, Clocks, Lensing, and Orbits",
        fontsize=20, color=WHITE, fontweight="bold", y=0.965,
    )
    fig.text(
        0.5, 0.928,
        "A qualitative visualisation of spacetime outside a non-rotating black hole",
        ha="center", color=MUTED, fontsize=10,
    )

    # ── Panel 1: embedding diagram ───────────────────────────────────────────
    ax_embed.set_facecolor(PANEL)
    ax_embed.plot_surface(
        X, Y, Z,
        cmap="magma",
        linewidth=0,
        antialiased=True,
        alpha=0.94,
    )
    ax_embed.plot_wireframe(
        X, Y, Z,
        rstride=5, cstride=9,
        color=CYAN,
        linewidth=0.35,
        alpha=0.18,
    )

    ring_theta = np.linspace(0, 2 * np.pi, 300)
    for radius, color, alpha, label in [
        (RS, PINK, 0.85, "event horizon"),
        (PHOTON_SPHERE, ORANGE, 0.42, "photon sphere"),
        (ISCO, CYAN, 0.32, "ISCO"),
    ]:
        ring_x = radius * np.cos(ring_theta)
        ring_y = radius * np.sin(ring_theta)
        ring_z = embedding_height(np.full_like(ring_theta, radius))
        ax_embed.plot(ring_x, ring_y, ring_z, color=color, alpha=alpha, lw=1.5)

    trail_start = max(0, frame - 28)
    ax_embed.plot(
        orbit_x[trail_start:frame + 1],
        orbit_y[trail_start:frame + 1],
        orbit_z[trail_start:frame + 1],
        color=GOLD, lw=2.4, alpha=0.95,
    )
    ax_embed.scatter([0], [0], [embedding_height(RS * 1.01)], s=260, color=HORIZON,
                     edgecolors=PINK, linewidths=1.5, zorder=10)
    ax_embed.scatter([x_now], [y_now], [z_now], s=78, color=WHITE,
                     edgecolors=GOLD, linewidths=1.6, zorder=11)

    ax_embed.set_title("Curved Space Outside the Horizon", color=TEXT, pad=10, fontsize=11.5)
    ax_embed.set_xlim(-R_MAX, R_MAX)
    ax_embed.set_ylim(-R_MAX, R_MAX)
    ax_embed.set_zlim(Z.min() * 1.03, 0.6)
    ax_embed.set_xlabel("x", color=MUTED, labelpad=6)
    ax_embed.set_ylabel("y", color=MUTED, labelpad=6)
    ax_embed.set_zlabel("embedded depth", color=MUTED, labelpad=6)
    ax_embed.tick_params(colors=MUTED, labelsize=7)
    ax_embed.xaxis.pane.fill = False
    ax_embed.yaxis.pane.fill = False
    ax_embed.zaxis.pane.fill = False
    ax_embed.xaxis.pane.set_edgecolor("#162334")
    ax_embed.yaxis.pane.set_edgecolor("#162334")
    ax_embed.zaxis.pane.set_edgecolor("#162334")
    ax_embed.view_init(elev=28 + 4 * np.sin(2 * np.pi * t), azim=38 + 150 * t)
    ax_embed.text2D(
        0.03, 0.97,
        "Flamm-style embedding diagram\nfor the Schwarzschild exterior",
        transform=ax_embed.transAxes, va="top", color=TEXT, fontsize=9.5,
    )

    # ── Panel 2: gravitational time dilation ────────────────────────────────
    style_panel(ax_clock, "Gravitational Time Dilation", xlabel="radius  r / rₛ", ylabel="dτ / dt")
    rr_scaled = rate_curve_r / RS
    ax_clock.fill_between(rr_scaled, 0, rate_curve, color=DEEP_CYAN, alpha=0.22)
    ax_clock.plot(rr_scaled, rate_curve, color=CYAN, lw=2.5)
    ax_clock.axvline(1.0, color=PINK, lw=1.2, ls="--", alpha=0.75)
    ax_clock.axvline(PHOTON_SPHERE / RS, color=ORANGE, lw=1.0, ls=":", alpha=0.75)
    ax_clock.axvline(ISCO / RS, color=GOLD, lw=1.0, ls=":", alpha=0.75)
    ax_clock.scatter([r_now / RS], [rate_now], s=110, color=WHITE, edgecolors=GOLD, linewidths=1.7, zorder=5)
    ax_clock.set_xlim(1.0, R_MAX / RS)
    ax_clock.set_ylim(0.0, 1.04)

    ax_clock.text(1.02, 0.06, "horizon", color=PINK, fontsize=8.5)
    ax_clock.text(PHOTON_SPHERE / RS + 0.04, 0.13, "photon sphere", color=ORANGE, fontsize=8.5)
    ax_clock.text(ISCO / RS + 0.04, 0.20, "ISCO", color=GOLD, fontsize=8.5)

    ax_clock.text(
        0.05, 0.93,
        f"Probe radius      : {r_now / RS:4.2f} rₛ\n"
        f"Proper-time rate  : {rate_now:4.3f} × distant clock\n"
        f"Distant observer  : {coord_time[frame]:4.2f}\n"
        f"Probe proper time : {probe_time[frame]:4.2f}\n"
        f"Clock gap         : {clock_gap[frame]:4.2f}",
        transform=ax_clock.transAxes,
        va="top",
        color=TEXT,
        fontsize=9.5,
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#08111d", edgecolor="#18304d", alpha=0.96),
    )
    ax_clock.text(
        0.05, 0.17,
        "Closer to the horizon, the probe's clock\nruns more slowly relative to a far-away observer.",
        transform=ax_clock.transAxes,
        color=MUTED,
        fontsize=8.8,
    )

    # ── Panel 3: gravitational lensing ──────────────────────────────────────
    ax_lens.set_facecolor("#000000")
    ax_lens.set_title("Stylised Gravitational Lensing", color=TEXT, fontsize=11.5, pad=8)
    lx, ly, ls, lc = lens_stars(t)
    ax_lens.scatter(lx, ly, s=ls, c=lc, linewidths=0)

    ring_strength = 0.5 + 0.5 * np.sin(2 * np.pi * t)
    for radius, color, width, alpha in [
        (0.18, PINK, 0.030 + 0.010 * ring_strength, 0.26),
        (0.26, ORANGE, 0.026 + 0.008 * ring_strength, 0.18),
        (0.34, GOLD, 0.022 + 0.006 * ring_strength, 0.10),
    ]:
        circle = Circle((0, 0), radius=radius, facecolor="none", edgecolor=color,
                        linewidth=18 * width / 0.03, alpha=alpha)
        ax_lens.add_patch(circle)

    ax_lens.add_patch(Circle((0, 0), radius=0.115, facecolor=HORIZON, edgecolor=PINK, linewidth=1.3, alpha=1.0))
    ax_lens.add_patch(Circle((0, 0), radius=0.162, facecolor="none", edgecolor=WHITE, linewidth=0.9, alpha=0.17))

    for angle in np.linspace(0, 2 * np.pi, 6, endpoint=False):
        rr_arc = np.linspace(0.18, 0.95, 120)
        bend = 0.18 / (rr_arc + 0.04)
        ax_lens.plot(
            rr_arc * np.cos(angle + bend),
            rr_arc * np.sin(angle + bend),
            color="#33506e", lw=0.5, alpha=0.24,
        )

    ax_lens.text(
        0.03, 0.96,
        "Background starlight is magnified and bent\ninto arcs and near-rings around the hole.",
        transform=ax_lens.transAxes, va="top", color=TEXT, fontsize=9.3,
    )
    ax_lens.set_aspect("equal")
    ax_lens.set_xlim(-1.05, 1.05)
    ax_lens.set_ylim(-1.05, 1.05)
    ax_lens.set_xticks([])
    ax_lens.set_yticks([])
    for spine in ax_lens.spines.values():
        spine.set_color("#172338")
        spine.set_linewidth(0.9)

    # ── Panel 4: orbital motion and precession ───────────────────────────────
    style_panel(ax_orbit, "Strong-Field Orbit", xlabel="x / rₛ", ylabel="y / rₛ")
    ax_orbit.set_aspect("equal")

    ax_orbit.add_patch(Circle((0, 0), radius=RS / RS, facecolor=HORIZON, edgecolor=PINK, linewidth=1.4, alpha=1.0))
    ax_orbit.add_patch(Circle((0, 0), radius=PHOTON_SPHERE / RS, facecolor="none", edgecolor=ORANGE, linewidth=1.0, ls="--", alpha=0.50))
    ax_orbit.add_patch(Circle((0, 0), radius=ISCO / RS, facecolor="none", edgecolor=CYAN, linewidth=1.0, ls=":", alpha=0.42))

    ax_orbit.plot(orbit_x / RS, orbit_y / RS, color="#20354d", lw=1.2, alpha=0.65)
    trail_start = max(0, frame - 45)
    ax_orbit.plot(orbit_x[trail_start:frame + 1] / RS, orbit_y[trail_start:frame + 1] / RS,
                  color=GOLD, lw=2.5, alpha=0.95)
    ax_orbit.scatter([x_now / RS], [y_now / RS], s=100, color=WHITE,
                     edgecolors=GOLD, linewidths=1.7, zorder=5)
    ax_orbit.scatter([0], [0], s=220, color=HORIZON, edgecolors=PINK, linewidths=1.2, zorder=4)

    ax_orbit.text(PHOTON_SPHERE / RS + 0.08, 0.08, "photon sphere", color=ORANGE, fontsize=8.3)
    ax_orbit.text(ISCO / RS + 0.08, -0.20, "ISCO", color=CYAN, fontsize=8.3)
    ax_orbit.text(
        0.03, 0.96,
        f"The orbit does not close neatly.\nStrong curvature causes apsidal precession.\nCurrent radius: {r_now / RS:4.2f} rₛ",
        transform=ax_orbit.transAxes, va="top", color=TEXT, fontsize=9.3,
    )
    ax_orbit.set_xlim(-4.9, 4.9)
    ax_orbit.set_ylim(-4.9, 4.9)

    fig.text(
        0.5, 0.025,
        "Event horizon at r = rₛ   •   Photon sphere at 1.5 rₛ   •   ISCO at 3 rₛ",
        ha="center", color=MUTED, fontsize=9.2,
    )

    return []


out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schwarzschild_spacetime.gif")

if __name__ == "__main__":
    print("Preparing Schwarzschild spacetime animation …")
    print(f"  frames   : {NFR}")
    print(f"  fps      : {FPS}")
    print(f"  preview  : {PREVIEW}")

    ani = FuncAnimation(fig, update, frames=NFR, interval=1000 / FPS, blit=False)

    print("\n▶  Opening interactive window — close it to save GIF.")
    plt.show()

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schwarzschild_spacetime.gif")
    print(f"Rendering → {out}")
    ani.save(
        out,
        writer=PillowWriter(fps=FPS),
        dpi=SAVE_DPI,
        savefig_kwargs={"facecolor": BG},
    )
    print(f"✓ Saved → {out}")
