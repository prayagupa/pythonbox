#!/usr/bin/env python3
"""
Einstein's Theory of Relativity — Educational Animation
═══════════════════════════════════════════════════════
Scene 0 — Introduction & The Two Postulates of Special Relativity
Scene 1 — Time Dilation: The Light Clock Thought Experiment
Scene 2 — Length Contraction: Lorentz Contraction
Scene 3 — General Relativity: Spacetime Curvature (3D)
Scene 4 — E = mc²: Mass-Energy Equivalence & Summary
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Rectangle, FancyBboxPatch, Ellipse, Circle
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D   # noqa: F401  (registers 3d projection)
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
# COLOUR PALETTE  (deep-space aesthetic)
# ──────────────────────────────────────────────────────────────
BG     = "#04040f"
TEXT   = "#dde8ff"
CYAN   = "#00d4ff"
ORANGE = "#ff7733"
GOLD   = "#ffd700"
GREEN  = "#44ff88"
PINK   = "#ff66cc"
WHITE  = "#ffffff"
GRID_C = "#0d0d2b"

# ──────────────────────────────────────────────────────────────
# TIMING
# ──────────────────────────────────────────────────────────────
FPS           = 20
SCENE_FRAMES  = [90, 110, 100, 120, 100]   # frames per scene
CUMULATIVE    = np.cumsum([0] + SCENE_FRAMES)
TOTAL_FRAMES  = sum(SCENE_FRAMES)

# ──────────────────────────────────────────────────────────────
# STATIC STAR FIELD  (consistent seed so stars don't jump)
# ──────────────────────────────────────────────────────────────
np.random.seed(42)
STAR_X     = np.random.uniform(0, 16, 260)
STAR_Y     = np.random.uniform(0, 9,  260)
STAR_PHASE = np.random.uniform(0, 2 * np.pi, 260)

fig = plt.figure(figsize=(16, 9), facecolor=BG)


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def get_scene(frame):
    """Return (scene_index, local_frame, t ∈ [0,1]) for a global frame."""
    for i, c in enumerate(CUMULATIVE[1:]):
        if frame < c:
            local = frame - CUMULATIVE[i]
            t = local / SCENE_FRAMES[i]
            return i, local, t
    last = len(SCENE_FRAMES) - 1
    return last, SCENE_FRAMES[last] - 1, 1.0


def draw_stars(ax, t, alpha_max=0.55):
    alphas = alpha_max * (0.3 + 0.7 * np.abs(np.sin(STAR_PHASE + t * 3)))
    ax.scatter(STAR_X, STAR_Y, s=0.4, c=WHITE, alpha=np.clip(alphas, 0, 1),
               zorder=0)


def fade(t, start=0.0, scale=4.0):
    """Smooth alpha ramp: 0 at t=start, 1 at t=start+1/scale."""
    return float(np.clip((t - start) * scale, 0.0, 1.0))


# ══════════════════════════════════════════════════════════════
#  SCENE 0 — TITLE & POSTULATES
# ══════════════════════════════════════════════════════════════

def scene_title(t, _local):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9)
    ax.axis("off"); ax.set_facecolor(BG)
    draw_stars(ax, t)

    # Animated light beam racing across the top
    bx = t * 19 - 1.5
    ax.plot([bx - 2.5, bx], [8.25, 8.25], color=CYAN, lw=2, alpha=0.7)
    ax.plot(bx, 8.25, "o", color=CYAN, ms=5)

    # Title card
    a1 = fade(t, 0.0, 5)
    ax.text(8, 6.9, "EINSTEIN'S THEORY OF RELATIVITY",
            fontsize=25, fontweight="bold", color=GOLD,
            ha="center", va="center", alpha=a1, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.55", facecolor="#080818",
                      edgecolor=GOLD, linewidth=1.5, alpha=a1 * 0.85))

    ax.text(8, 6.05, "A Visual Journey Through Space and Time",
            fontsize=14, color=CYAN, ha="center", va="center",
            alpha=fade(t, 0.12, 5), fontstyle="italic")

    # Postulate I
    a2 = fade(t, 0.30, 5)
    ax.add_patch(FancyBboxPatch((1.8, 4.1), 5.6, 1.45,
                 boxstyle="round,pad=0.12", facecolor="#090920",
                 edgecolor=ORANGE, lw=1.8, alpha=a2))
    ax.text(4.6, 5.25, "Postulate  I", fontsize=11,
            color=ORANGE, fontweight="bold", ha="center", alpha=a2)
    ax.text(4.6, 4.65, "Laws of physics are identical\nin all inertial reference frames",
            fontsize=9, color=TEXT, ha="center", alpha=a2)

    # Postulate II
    a3 = fade(t, 0.50, 5)
    ax.add_patch(FancyBboxPatch((8.6, 4.1), 5.6, 1.45,
                 boxstyle="round,pad=0.12", facecolor="#090920",
                 edgecolor=PINK, lw=1.8, alpha=a3))
    ax.text(11.4, 5.25, "Postulate  II", fontsize=11,
            color=PINK, fontweight="bold", ha="center", alpha=a3)
    ax.text(11.4, 4.65, "The speed of light c is constant\nfor ALL observers",
            fontsize=9, color=TEXT, ha="center", alpha=a3)

    a4 = fade(t, 0.68, 5)
    ax.text(8, 3.35, "c  =  299 792 458  m/s",
            fontsize=14, color=WHITE, ha="center",
            fontfamily="monospace", alpha=a4)
    ax.text(8, 2.75, "(≈ 186 282 miles per second — nothing travels faster)",
            fontsize=10, color=TEXT, ha="center", alpha=a4)

    a5 = fade(t, 0.80, 6)
    ax.text(8, 1.95, "These two simple postulates lead to the most",
            fontsize=10, color=TEXT, ha="center", alpha=a5)
    ax.text(8, 1.45, "revolutionary physics ever conceived…",
            fontsize=10, color=GOLD, ha="center", alpha=a5, fontstyle="italic")


# ══════════════════════════════════════════════════════════════
#  SCENE 1 — TIME DILATION  (Light Clock)
# ══════════════════════════════════════════════════════════════

def scene_time_dilation(t, _local):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9)
    ax.axis("off"); ax.set_facecolor(BG)
    draw_stars(ax, t, 0.28)

    ax.text(8, 8.62, "SPECIAL RELATIVITY: TIME DILATION",
            fontsize=15, color=GOLD, ha="center", fontweight="bold")
    ax.text(8, 8.18, "The Light Clock Thought Experiment",
            fontsize=10, color=CYAN, ha="center", fontstyle="italic")

    beta  = 0.866          # v/c
    gamma = 1 / np.sqrt(1 - beta ** 2)   # ≈ 2.0
    mw    = 1.8            # mirror width

    # ─── Stationary light clock (left) ───────────────────────
    cx_s  = 3.8
    bot_s, top_s = 2.0, 6.5
    h_s   = top_s - bot_s

    # dashed frame
    ax.add_patch(Rectangle((cx_s - mw / 2 - 0.1, bot_s - 0.25),
                            mw + 0.2, h_s + 0.5,
                            facecolor="none", edgecolor="#334466",
                            lw=1, linestyle="--", alpha=0.5))

    # mirrors
    ax.plot([cx_s - mw/2, cx_s + mw/2], [bot_s, bot_s],
            color=CYAN, lw=4, solid_capstyle="round")
    ax.plot([cx_s - mw/2, cx_s + mw/2], [top_s, top_s],
            color=CYAN, lw=4, solid_capstyle="round")
    ax.text(cx_s, bot_s - 0.38, "mirror", fontsize=7, color=CYAN, ha="center")
    ax.text(cx_s, top_s + 0.18, "mirror", fontsize=7, color=CYAN, ha="center")

    # photon bounce — 5 round trips per full t
    n_bounces = 5
    bf_s  = (t * n_bounces) % 1.0
    py_s  = bot_s + h_s * bf_s * 2 if bf_s < 0.5 else top_s - h_s * (bf_s - 0.5) * 2

    # fading photon trail
    TRAIL = 14
    for k in range(TRAIL):
        bf_tr = ((t * n_bounces) - k * 0.025) % 1.0
        py_tr = (bot_s + h_s * bf_tr * 2
                 if bf_tr < 0.5 else top_s - h_s * (bf_tr - 0.5) * 2)
        ax.plot(cx_s, py_tr, "o", color=GOLD,
                ms=max(1, 6 * (1 - k / TRAIL)),
                alpha=max(0, 1 - k / TRAIL))
    ax.plot(cx_s, py_s, "o", color=GOLD, ms=9, zorder=10)

    ticks_s = int(t * n_bounces * 2)
    ax.text(cx_s, 1.50, "Observer on Earth", fontsize=8, color=TEXT, ha="center")
    ax.text(cx_s, 1.00, f"Ticks: {ticks_s}", fontsize=14,
            color=GREEN, ha="center", fontweight="bold")
    ax.text(cx_s, 0.52, "(Stationary clock)", fontsize=8, color=GREEN, ha="center")

    # ─── Moving light clock (right) ──────────────────────────
    cx_m  = 9.5 + t * 2.8          # drifts right across screen
    bot_m, top_m = 2.0, 6.5
    h_m   = top_m - bot_m

    if cx_m - mw / 2 < 15.8:
        ax.add_patch(Rectangle((cx_m - mw / 2 - 0.1, bot_m - 0.25),
                                mw + 0.2, h_m + 0.5,
                                facecolor="none", edgecolor="#664433",
                                lw=1, linestyle="--", alpha=0.5))

        ax.plot([cx_m - mw/2, cx_m + mw/2], [bot_m, bot_m],
                color=ORANGE, lw=4, solid_capstyle="round")
        ax.plot([cx_m - mw/2, cx_m + mw/2], [top_m, top_m],
                color=ORANGE, lw=4, solid_capstyle="round")

        # photon is slower (time-dilated): fewer bounces by factor gamma
        n_bounces_m = n_bounces / gamma
        bf_m   = (t * n_bounces_m) % 1.0
        diag   = mw * 0.25    # small horizontal zig-zag to show diagonal path
        if bf_m < 0.5:
            py_m = bot_m + h_m * bf_m * 2
            px_m = cx_m + diag * (bf_m * 2 - 0.5)
        else:
            py_m = top_m - h_m * (bf_m - 0.5) * 2
            px_m = cx_m + diag * (0.5 - (bf_m - 0.5) * 2)

        # ghost diagonal path
        ax.plot([cx_m - diag, cx_m + diag, cx_m - diag],
                [bot_m, top_m, bot_m],
                color=ORANGE, lw=0.6, alpha=0.3, linestyle="--")

        ax.plot(px_m, py_m, "o", color=ORANGE, ms=9, zorder=10)

        # velocity arrow
        ax.annotate("", xy=(cx_m + 1.9, bot_m - 0.65),
                    xytext=(cx_m - 0.4, bot_m - 0.65),
                    arrowprops=dict(arrowstyle="->", color=PINK, lw=2.0))
        ax.text(cx_m + 0.75, bot_m - 0.95,
                f"v = {beta}c", fontsize=9, color=PINK, ha="center")

        ticks_m = int(t * n_bounces_m * 2)
        ax.text(cx_m, 1.50, f"Moving at {beta}c", fontsize=8, color=TEXT, ha="center")
        ax.text(cx_m, 1.00, f"Ticks: {ticks_m}", fontsize=14,
                color=ORANGE, ha="center", fontweight="bold")
        ax.text(cx_m, 0.52, f"(γ = {gamma:.1f}× slower!)",
                fontsize=8, color=ORANGE, ha="center")

    # divider
    ax.plot([7.5, 7.5], [0.3, 8.0], color="#334466", lw=1, linestyle=":")

    # formula box
    fa = fade(t, 0.0, 3)
    ax.add_patch(FancyBboxPatch((3.2, 7.1), 9.6, 0.78,
                 boxstyle="round,pad=0.1", facecolor="#050520",
                 edgecolor=CYAN, lw=1.5, alpha=fa * 0.85))
    ax.text(8, 7.49,
            r"$\Delta t' = \gamma \cdot \Delta t_0$   where   "
            r"$\gamma = 1/\sqrt{1-v^2/c^2}$   ⟹   $\gamma = 2.0$ at $v = 0.866c$",
            fontsize=10.5, color=CYAN, ha="center", va="center", alpha=fa)

    if t > 0.6:
        ax.text(8, 0.12,
                "The moving photon travels a LONGER diagonal path → "
                "more time needed per tick → MOVING CLOCKS RUN SLOW",
                fontsize=9, color=GOLD, ha="center",
                alpha=fade(t, 0.6, 5))


# ══════════════════════════════════════════════════════════════
#  SCENE 2 — LENGTH CONTRACTION
# ══════════════════════════════════════════════════════════════

def scene_length_contraction(t, _local):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9)
    ax.axis("off"); ax.set_facecolor(BG)
    draw_stars(ax, t, 0.28)

    ax.text(8, 8.62, "SPECIAL RELATIVITY: LENGTH CONTRACTION",
            fontsize=15, color=GOLD, ha="center", fontweight="bold")
    ax.text(8, 8.18,
            "Lorentz Contraction — Objects shrink along the direction of motion",
            fontsize=10, color=CYAN, ha="center", fontstyle="italic")

    rest_len = 5.5
    # beta ramps from 0 → 0.99 → 0 across the scene
    beta      = 0.98 * np.sin(t * np.pi) ** 2
    gamma     = 1 / np.sqrt(max(1e-9, 1 - beta ** 2))
    contracted = rest_len / gamma

    # ─── Fixed ruler ─────────────────────────────────────────
    def ruler(ax_, y_):
        ax_.plot([0.5, 15.5], [y_, y_], color="#334466", lw=1)
        for xi in np.arange(0.5, 16, 0.5):
            h = 0.25 if (xi % 2.0 < 0.01) else 0.14
            ax_.plot([xi, xi], [y_, y_ + h], color="#334466", lw=0.6)
        ax_.text(0.6, y_ + 0.35, "Fixed ruler", fontsize=7, color="#445577")

    ruler(ax, 7.2)
    ruler(ax, 4.0)

    # ─── Rest frame (top) ────────────────────────────────────
    y_rest = 6.5
    x0_r   = 8 - rest_len / 2
    ax.add_patch(FancyBboxPatch((x0_r, y_rest - 0.5), rest_len, 1.0,
                 boxstyle="round,pad=0.15",
                 facecolor="#0a1f3c", edgecolor=CYAN, lw=2.5))
    for wi in [0.7, 1.6, 2.5, 3.4, 4.3]:
        if wi < rest_len - 0.3:
            ax.add_patch(Ellipse((x0_r + wi, y_rest + 0.15),
                                 0.38, 0.28,
                                 facecolor="#00d4ff18", edgecolor=CYAN, lw=0.8))
    ax.text(8, y_rest, "AT  REST", fontsize=10, color=WHITE,
            ha="center", va="center", fontweight="bold")
    ax.annotate("", xy=(x0_r + rest_len + 0.2, y_rest + 0.7),
                xytext=(x0_r - 0.2, y_rest + 0.7),
                arrowprops=dict(arrowstyle="<->", color=CYAN, lw=1.5))
    ax.text(8, y_rest + 1.0, f"L₀ = {rest_len:.1f} units",
            fontsize=10, color=CYAN, ha="center")

    # ─── Moving frame (bottom) ───────────────────────────────
    y_move = 3.3
    x0_m   = 8 - contracted / 2
    ax.add_patch(FancyBboxPatch((x0_m, y_move - 0.5), contracted, 1.0,
                 boxstyle="round,pad=0.15",
                 facecolor="#3a0a0a", edgecolor=ORANGE, lw=2.5))
    n_win = max(1, round(4 * contracted / rest_len))
    for wi_idx in range(n_win):
        wx = x0_m + (wi_idx + 0.5) * contracted / (n_win + 0.5)
        w_size = max(0.10, 0.38 / gamma)
        ax.add_patch(Ellipse((wx, y_move + 0.15), w_size, 0.28,
                             facecolor="#ff773320", edgecolor=ORANGE, lw=0.8))
    ax.text(8, y_move, f"v = {beta:.3f}c",
            fontsize=9, color=WHITE, ha="center", va="center", fontweight="bold")

    # velocity arrows
    for ai in range(4):
        ax.annotate("", xy=(x0_m + contracted + 0.3 + 0.65 * (ai + 1), y_move),
                    xytext=(x0_m + contracted + 0.3 + 0.65 * ai, y_move),
                    arrowprops=dict(arrowstyle="->", color=PINK, lw=1.6))

    ax.annotate("", xy=(x0_m + contracted + 0.2, y_move + 0.7),
                xytext=(x0_m - 0.2, y_move + 0.7),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=1.5))
    ax.text(8, y_move + 1.0,
            f"L = L₀/γ = {contracted:.2f} units   (γ = {gamma:.2f})",
            fontsize=10, color=ORANGE, ha="center")

    pct = 100 * contracted / rest_len
    ax.text(8, y_move - 0.85,
            f"Compressed to  {pct:.1f}%  of rest length",
            fontsize=10, color=GOLD, ha="center", fontweight="bold")

    # velocity meter (left sidebar)
    ax.text(1.25, 5.45, "SPEED", fontsize=8, color=TEXT, ha="center")
    ax.text(1.25, 5.10, "METER", fontsize=8, color=TEXT, ha="center")
    for bar_i in range(10):
        frac    = (bar_i + 1) * 0.1
        c_bar   = ORANGE if frac <= beta else "#111133"
        ax.add_patch(Rectangle((0.5, 2.5 + bar_i * 0.21), 1.5, 0.18,
                                facecolor=c_bar, edgecolor="#334466", lw=0.5))
    ax.text(1.25, 4.70, f"{beta:.3f}c", fontsize=10,
            color=GOLD, ha="center", fontweight="bold")

    # formula
    ax.add_patch(FancyBboxPatch((4.0, 1.05), 8.0, 0.92,
                 boxstyle="round,pad=0.12", facecolor="#050520",
                 edgecolor=CYAN, lw=1.5))
    ax.text(8, 1.51,
            r"$L = L_0 \sqrt{1 - v^2/c^2} \;=\; L_0 / \gamma$",
            fontsize=13, color=CYAN, ha="center", va="center")

    if t > 0.45:
        ax.text(8, 0.45,
                "Only the dimension along the direction of motion contracts. "
                "Height and width are unchanged.",
                fontsize=9, color=TEXT, ha="center",
                alpha=fade(t, 0.45, 5))


# ══════════════════════════════════════════════════════════════
#  SCENE 3 — GENERAL RELATIVITY: SPACETIME CURVATURE  (3D)
# ══════════════════════════════════════════════════════════════

def scene_spacetime_curvature(t, _local):
    ax3 = fig.add_axes([0.02, 0.09, 0.55, 0.87], projection="3d")
    ax3.set_facecolor(BG)

    ax2 = fig.add_axes([0.60, 0.04, 0.39, 0.92])
    ax2.set_facecolor(BG); ax2.axis("off")
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 10)

    fig.text(0.5, 0.975,
             "GENERAL RELATIVITY: Spacetime Curvature",
             fontsize=14, color=GOLD, ha="center", fontweight="bold")

    # ─── 3D Spacetime grid ───────────────────────────────────
    N    = 36
    span = 4.5
    x_g  = np.linspace(-span, span, N)
    y_g  = np.linspace(-span, span, N)
    X, Y = np.meshgrid(x_g, y_g)

    mass = float(np.clip(t * 4.5, 0, 3.2))
    R    = np.sqrt(X ** 2 + Y ** 2)
    Z    = -mass / (R + 0.55)

    cmap_s = LinearSegmentedColormap.from_list(
        "spacetime",
        [(0.01, 0.01, 0.14), (0.0, 0.28, 0.72), (0.0, 0.82, 1.0)],
        N=256)
    ax3.plot_surface(X, Y, Z, cmap=cmap_s, alpha=0.72,
                     rstride=2, cstride=2, linewidth=0, antialiased=True)

    # fabric grid lines
    for xi in x_g[::4]:
        zl = -mass / (np.sqrt(xi ** 2 + y_g ** 2) + 0.55)
        ax3.plot([xi] * N, y_g, zl, color="#1a6aaa", lw=0.55, alpha=0.55)
    for yi in y_g[::4]:
        zl = -mass / (np.sqrt(x_g ** 2 + yi ** 2) + 0.55)
        ax3.plot(x_g, [yi] * N, zl, color="#1a6aaa", lw=0.55, alpha=0.55)

    # central mass (glowing sphere)
    u_s, v_s = np.mgrid[0:2*np.pi:20j, 0:np.pi:12j]
    r_s = 0.26 + mass * 0.055
    z_bot = float(-mass / 0.55)
    sx = r_s * np.cos(u_s) * np.sin(v_s)
    sy = r_s * np.sin(u_s) * np.sin(v_s)
    sz = r_s * np.cos(v_s) + z_bot + r_s
    ax3.plot_surface(sx, sy, sz, color=ORANGE, alpha=0.95)

    # glow halos
    for hr in [0.4, 0.75, 1.1]:
        th_h = np.linspace(0, 2 * np.pi, 60)
        ax3.plot(hr * np.cos(th_h), hr * np.sin(th_h),
                 np.full(60, z_bot + 0.04),
                 color=ORANGE, lw=0.7, alpha=0.25)

    # orbiting planet
    orb_r = 2.5
    ang   = t * 3.2 * np.pi
    ax3.scatter([orb_r * np.cos(ang)], [orb_r * np.sin(ang)],
                [float(-mass / (orb_r + 0.55))],
                color=GREEN, s=60, zorder=10)
    th_o  = np.linspace(0, 2 * np.pi, 100)
    ax3.plot(orb_r * np.cos(th_o), orb_r * np.sin(th_o),
             -mass / (orb_r + 0.55) * np.ones(100),
             color=GOLD, lw=1.2, alpha=0.55, linestyle="--")

    # bending light ray
    lx = np.linspace(-span, -0.5, 60)
    bend = mass * 0.32 / (np.abs(lx) + 0.8)
    lz_  = -mass / (np.sqrt(lx ** 2 + bend ** 2) + 0.55)
    ax3.plot(lx, bend, lz_, color=GOLD, lw=1.6, alpha=0.75)

    # axes cosmetics
    ax3.view_init(elev=27, azim=30 + t * 55)
    ax3.set_xlim(-span, span); ax3.set_ylim(-span, span)
    ax3.set_xlabel("X", color=TEXT, labelpad=-4, fontsize=8)
    ax3.set_ylabel("Y", color=TEXT, labelpad=-4, fontsize=8)
    ax3.set_zlabel("Curvature", color=TEXT, labelpad=-4, fontsize=8)
    ax3.tick_params(colors=TEXT, labelsize=6, pad=-2)
    for pane in (ax3.xaxis.pane, ax3.yaxis.pane, ax3.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor(GRID_C)
    ax3.grid(False)

    # ─── Right panel ─────────────────────────────────────────
    ax2.text(5, 9.5, "General Relativity", fontsize=14,
             color=GOLD, ha="center", fontweight="bold")
    ax2.text(5, 9.05, "\"Mass tells spacetime how to curve,",
             fontsize=9, color=TEXT, ha="center", fontstyle="italic")
    ax2.text(5, 8.68, " spacetime tells matter how to move.\"",
             fontsize=9, color=TEXT, ha="center", fontstyle="italic")
    ax2.text(5, 8.30, "— John Archibald Wheeler",
             fontsize=8, color=CYAN, ha="center")

    a_list = fade(t, 0.08, 3)
    items = [
        (7.55, "⬤  Massive object curves spacetime fabric",          ORANGE),
        (6.85, "⬤  Planets orbit curved geodesics (not 'pulled')",   GREEN),
        (6.15, "⬤  Light bends near massive objects",                GOLD),
        (5.45, "⬤  Clocks run slower in stronger gravity",           PINK),
        (4.75, "⬤  GPS satellites need GR corrections (+45 μs/day)", CYAN),
        (4.05, "⬤  Black holes: extreme curvature, escape vₑ = c",  WHITE),
        (3.35, "⬤  Gravitational waves: ripples in spacetime fabric","#aaffaa"),
    ]
    for cy_i, txt, col in items:
        ax2.text(0.2, cy_i, txt, fontsize=9, color=col, alpha=a_list)

    if t > 0.50:
        a_eq = fade(t, 0.50, 4)
        ax2.add_patch(FancyBboxPatch((0.2, 0.95), 9.6, 1.65,
                     boxstyle="round,pad=0.22", facecolor="#050520",
                     edgecolor=CYAN, lw=1.5, alpha=a_eq))
        ax2.text(5, 2.18,
                 r"$G_{\mu\nu} + \Lambda g_{\mu\nu} "
                 r"= \dfrac{8\pi G}{c^4}\, T_{\mu\nu}$",
                 fontsize=15, color=WHITE, ha="center", alpha=a_eq)
        ax2.text(5, 1.40, "Einstein's Field Equations",
                 fontsize=9, color=TEXT, ha="center", alpha=a_eq)
        ax2.text(5, 0.55, "Geometry (left) = Matter / Energy (right)",
                 fontsize=9, color=CYAN, ha="center",
                 alpha=a_eq, fontstyle="italic")


# ══════════════════════════════════════════════════════════════
#  SCENE 4 — E = mc²  &  SUMMARY
# ══════════════════════════════════════════════════════════════

def scene_emc2(t, _local):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9)
    ax.axis("off"); ax.set_facecolor(BG)
    draw_stars(ax, t, 0.38)

    ax.text(8, 8.62, "E = mc²  —  MASS-ENERGY EQUIVALENCE",
            fontsize=15, color=GOLD, ha="center", fontweight="bold")

    # Grand formula reveal with glow shadow
    af = fade(t, 0.0, 3.5)
    for off in [0.06, 0.04, 0.02]:
        ax.text(8 + off, 7.25 - off, r"$E = mc^2$",
                fontsize=54, color="#ff440018",
                ha="center", fontweight="bold", alpha=af * 0.6)
    ax.text(8, 7.25, r"$E = mc^2$",
            fontsize=54, color=CYAN, ha="center",
            fontweight="bold", alpha=af)

    # Term labels
    terms = [
        (3.5,  6.12, "E", "Energy  (Joules)",          ORANGE),
        (8.0,  6.12, "m", "Mass  (kg)",                GREEN),
        (12.5, 6.12, "c²", "Speed of Light² (m²/s²)", PINK),
    ]
    for tx, ty, sym, label, col in terms:
        a_t = fade(t, 0.08, 4)
        ax.text(tx, ty, sym, fontsize=22, color=col,
                ha="center", fontweight="bold", alpha=a_t)
        ax.text(tx, ty - 0.58, label, fontsize=9, color=col,
                ha="center", alpha=a_t, fontstyle="italic")

    # Expanding energy burst
    if t > 0.20:
        burst_r = min(1.6, (t - 0.20) * 4.5)
        a_burst = max(0.0, 1.0 - burst_r / 1.6)
        n_rays  = 32
        for ri in range(n_rays):
            ang = ri * 2 * np.pi / n_rays + t * 1.8
            dx  = np.cos(ang); dy = np.sin(ang)
            ax.plot([8 + dx * 0.25, 8 + dx * burst_r],
                    [7.25 + dy * 0.25, 7.25 + dy * burst_r],
                    color=GOLD, lw=1.4, alpha=a_burst * 0.85)

    # Calculation box
    if t > 0.35:
        a_calc = fade(t, 0.35, 4)
        ax.add_patch(FancyBboxPatch((1.5, 4.55), 13.0, 1.25,
                     boxstyle="round,pad=0.22", facecolor="#080820",
                     edgecolor=GOLD, lw=1.5, alpha=a_calc))
        ax.text(8, 5.47,
                "1 gram of matter  ⟹  E = 0.001 × (3×10⁸)²  =  9×10¹³ J",
                fontsize=11, color=WHITE, ha="center", alpha=a_calc)
        ax.text(8, 4.90,
                "= 21.5 kilotons of TNT   ≈   Hiroshima atomic bomb  × 1.4",
                fontsize=10, color=GOLD, ha="center", alpha=a_calc)

    # Applications
    if t > 0.55:
        a_app = fade(t, 0.55, 4)
        apps = [
            (3.95, "☀  Stars: hydrogen fusion converts mass → light and heat"),
            (3.35, "⚛  Nuclear reactors: tiny Δm → enormous energy output"),
            (2.75, "🔬  PET scanners: antimatter annihilation inside the human body"),
            (2.15, "🌌  Gamma-ray bursts: most energetic events in the universe"),
        ]
        for ay, atxt in apps:
            ax.text(8, ay, atxt, fontsize=10, color=TEXT,
                    ha="center", alpha=a_app)

    # Summary
    if t > 0.82:
        a_sum = fade(t, 0.82, 8)
        ax.add_patch(FancyBboxPatch((2.5, 0.55), 11.0, 0.8,
                     boxstyle="round,pad=0.18", facecolor="#050520",
                     edgecolor=CYAN, lw=1.5, alpha=a_sum))
        ax.text(8, 0.95,
                "Mass and energy are two faces of the same coin — interconvertible.",
                fontsize=11, color=CYAN, ha="center",
                alpha=a_sum, fontstyle="italic", fontweight="bold")


# ══════════════════════════════════════════════════════════════
#  MAIN  UPDATE  FUNCTION
# ══════════════════════════════════════════════════════════════

SCENE_FUNCS = [
    scene_title,
    scene_time_dilation,
    scene_length_contraction,
    scene_spacetime_curvature,
    scene_emc2,
]


def update(frame):
    fig.clear()
    fig.set_facecolor(BG)
    scene, local, t = get_scene(frame)
    try:
        SCENE_FUNCS[scene](t, local)
    except Exception as exc:
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(BG)
        ax.text(0.5, 0.5, f"[Scene {scene} — {exc}]",
                transform=ax.transAxes, color=TEXT,
                ha="center", fontsize=11)
    return []


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀  Rendering Einstein's Relativity Animation…")
    print(f"    Scenes  : {len(SCENE_FUNCS)}")
    print(f"    Frames  : {TOTAL_FRAMES}")
    print(f"    FPS     : {FPS}")
    print(f"    Duration: {TOTAL_FRAMES / FPS:.1f} s")

    ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES,
                        interval=1000 / FPS, blit=False)

    output = "einstein_relativity.gif"
    writer = PillowWriter(fps=FPS)
    print(f"    Saving  → {output}  (this may take ~1-2 minutes)…")
    ani.save(output, writer=writer, dpi=90)
    print(f"✓  Saved: {output}")

    plt.show()

