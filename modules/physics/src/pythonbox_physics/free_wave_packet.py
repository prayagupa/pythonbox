#!/usr/bin/env python3
"""
Free Gaussian Wave Packet  —  Animated Quantum Visualisation
═══════════════════════════════════════════════════════════════
Simulation 1 from the Schrödinger Equation educational series.

   iℏ ∂Ψ/∂t = −(ℏ²/2m) ∂²Ψ/∂x²     (V = 0,  free particle)

Physics shown:
  • Quantum dispersion — packet width spreads as σ(t) = σ₀√(1 + (t/2σ₀²)²)
  • Phase-rainbow coloring — oscillating quantum phase e^{ik₀x} made visible
  • Group velocity  v_g = k₀  vs  phase velocity  v_φ = k₀/2
  • Momentum distribution — constant in time for a free particle
  • Heisenberg uncertainty — Δx · Δk ≥ ½

Numerical method:  Split-Step Fourier (Suzuki–Trotter, 2nd order)
Natural units:     ℏ = m = 1

Output:  free_wave_packet.gif  (same directory as this script)
"""

import os
import warnings

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
#  COLOUR PALETTE  (deep-space aesthetic)
# ──────────────────────────────────────────────────────────────────────────────
BG     = "#03030e"   # near-black background
PANEL  = "#05051a"   # axis face
TEXT   = "#ccd8f0"   # soft white labels
CYAN   = "#00e5ff"   # probability density / Re(ψ)
GOLD   = "#ffd166"   # ⟨x⟩ marker / time counter
GREEN  = "#06d6a0"   # σ_x / norm readout
ORANGE = "#ff9a3c"   # theoretical envelope
PINK   = "#ef476f"   # Im(ψ)
PURPLE = "#9b5de5"   # momentum space
WHITE  = "#ffffff"

# ──────────────────────────────────────────────────────────────────────────────
#  GRID & PHYSICS PARAMETERS
# ──────────────────────────────────────────────────────────────────────────────
N    = 1024          # spatial grid points
L    = 80.0          # domain length  [−L/2, +L/2]
dx   = L / N
x    = np.linspace(-L / 2, L / 2, N, endpoint=False)

X0   = -15.0         # initial packet centre
SIG0 = 2.0           # initial width σ₀
K0   = 3.0           # initial wave-number → group velocity v_g = k₀

DT   = 0.04          # time step
SPF  = 3             # solver steps per animation frame
NFR  = 130           # total animation frames
FPS  = 22            # output GIF frame rate

# ──────────────────────────────────────────────────────────────────────────────
#  SPLIT-STEP FOURIER SOLVER  (V = 0 → no potential phase)
# ──────────────────────────────────────────────────────────────────────────────
k_grid = np.fft.fftfreq(N, d=dx) * 2 * np.pi
eK     = np.exp(-1j * 0.5 * k_grid**2 * DT)   # kinetic phase per step


def evolve(psi: np.ndarray, steps: int = 1) -> np.ndarray:
    """Advance ψ by `steps` × DT using the split-step method (V=0)."""
    for _ in range(steps):
        psi = np.fft.ifft(eK * np.fft.fft(psi))
    return psi


# ──────────────────────────────────────────────────────────────────────────────
#  INITIAL STATE
# ──────────────────────────────────────────────────────────────────────────────
norm0 = (2 * np.pi * SIG0**2) ** (-0.25)
psi0  = norm0 * np.exp(-(x - X0)**2 / (4 * SIG0**2)) * np.exp(1j * K0 * x)

# ──────────────────────────────────────────────────────────────────────────────
#  PRECOMPUTE ALL STATES
# ──────────────────────────────────────────────────────────────────────────────
print(f"Pre-computing {NFR} frames … ", end="", flush=True)
states: list[np.ndarray] = [psi0.copy()]
psi = psi0.copy()
for _ in range(NFR - 1):
    psi = evolve(psi, SPF)
    states.append(psi.copy())
print("done.\n")

# ──────────────────────────────────────────────────────────────────────────────
#  PRECOMPUTE OBSERVABLES
# ──────────────────────────────────────────────────────────────────────────────
dt_frame = SPF * DT
times    = np.arange(NFR) * dt_frame
prob_all = [np.abs(s)**2 for s in states]

x_mean  = np.array([np.trapezoid(x     * p, x) for p in prob_all])
x2_mean = np.array([np.trapezoid(x**2  * p, x) for p in prob_all])
sigma_x = np.sqrt(np.maximum(x2_mean - x_mean**2, 0))

# Analytical: σ(t) = σ₀ √(1 + (t / 2σ₀²)²)
sigma_th = SIG0 * np.sqrt(1 + (times / (2 * SIG0**2))**2)

# Momentum space (constant for free particle — computed once from ψ₀)
k_shift  = np.fft.fftshift(k_grid)
phi0     = np.fft.fftshift(np.fft.fft(psi0)) * dx / np.sqrt(2 * np.pi)
mom_dist = np.abs(phi0)**2

# ──────────────────────────────────────────────────────────────────────────────
#  DISPLAY LIMITS
# ──────────────────────────────────────────────────────────────────────────────
XLIM = (-30, 32)
KLIM = (-8, 8)

xmask   = (x       >= XLIM[0]) & (x       <= XLIM[1])
kmask   = (k_shift >= KLIM[0]) & (k_shift <= KLIM[1])

max_prob = max(np.max(p[xmask]) for p in prob_all) * 1.14
max_wave = max(
    max(np.max(np.abs(s[xmask].real)), np.max(np.abs(s[xmask].imag)))
    for s in states
) * 1.2
max_mom  = np.max(mom_dist[kmask]) * 1.15

# ──────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def style_ax(ax, title="", xlabel="", ylabel="", tc=TEXT):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=TEXT, labelsize=8)
    for sp in ax.spines.values():
        sp.set_edgecolor("#181838")
        sp.set_linewidth(0.7)
    if xlabel: ax.set_xlabel(xlabel, color=TEXT, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, color=TEXT, fontsize=9)
    if title:  ax.set_title(title, color=tc, fontsize=9.5, pad=5)


def phase_line(ax, xv, yv, phase, prob=None, lw=1.7, base_alpha=0.93):
    """Rainbow-colored line; color encodes the quantum phase angle φ ∈ (−π, π]."""
    rgba = plt.cm.hsv((phase + np.pi) / (2 * np.pi)).copy()   # (N, 4) RGBA
    if prob is not None:
        # Fade the color to transparent where the amplitude is negligible
        fade = np.sqrt(np.clip(prob / (max_prob * 0.04), 0.0, 1.0))
        rgba[:, 3] = base_alpha * fade
    else:
        rgba[:, 3] = base_alpha
    pts  = np.array([xv, yv]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc   = LineCollection(segs, colors=rgba[:-1], linewidths=lw)
    ax.add_collection(lc)


def glow_fill(ax, xv, yv, color=CYAN):
    """Layered glow fill: wide+faint → narrow+bright."""
    for alpha, scale in [(0.04, 1.08), (0.09, 1.04), (0.18, 1.01), (0.33, 1.00)]:
        ax.fill_between(xv, 0, yv * scale, color=color, alpha=alpha, linewidth=0)


# ──────────────────────────────────────────────────────────────────────────────
#  FIGURE LAYOUT
# ──────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 9), facecolor=BG)
gs  = gridspec.GridSpec(
    3, 3, figure=fig,
    left=0.07, right=0.97, top=0.87, bottom=0.07,
    hspace=0.72, wspace=0.40,
)
ax_main = fig.add_subplot(gs[0:2, :])   # top (large): |ψ|² probability density
ax_re   = fig.add_subplot(gs[2, 0])     # bottom-left : Re(ψ)
ax_im   = fig.add_subplot(gs[2, 1])     # bottom-centre: Im(ψ)
ax_mom  = fig.add_subplot(gs[2, 2])     # bottom-right : momentum space

# ──────────────────────────────────────────────────────────────────────────────
#  ANIMATION UPDATE
# ──────────────────────────────────────────────────────────────────────────────

def update(frame: int):
    # ── clear & style each axis ─────────────────────────────────
    for ax in (ax_main, ax_re, ax_im, ax_mom):
        ax.cla()

    psi   = states[frame]
    prob  = prob_all[frame]
    phase = np.angle(psi)
    t     = times[frame]
    xb    = x_mean[frame]
    sx    = sigma_x[frame]
    st    = sigma_th[frame]

    # Slice to display region
    xv  = x[xmask]
    pv  = prob[xmask]
    phv = phase[xmask]
    rv  = psi[xmask].real
    iv  = psi[xmask].imag
    # Amplitude envelope (for wave panels)
    env = np.sqrt(pv)

    # ════════════════════════════════════════════════════════
    #  TOP PANEL — |ψ(x,t)|²  with phase-rainbow glow
    # ════════════════════════════════════════════════════════
    ax = ax_main
    style_ax(
        ax,
        title=(r"$|\Psi(x,t)|^2$  —  Probability Density"
               r"    (line color encodes quantum phase  $\varphi \in (-\pi,\,\pi]$)"),
        xlabel="Position  x",
        ylabel=r"$|\Psi(x,t)|^2$",
        tc=CYAN,
    )

    # Layered glow fills
    glow_fill(ax, xv, pv, CYAN)

    # Phase-rainbow outline of |ψ|²
    phase_line(ax, xv, pv, phv, prob=pv, lw=2.2)

    # Faint white highlight on top of rainbow
    ax.plot(xv, pv, color=WHITE, lw=0.5, alpha=0.40, zorder=5)

    # Theoretical Gaussian envelope
    gauss_env = (
        (1.0 / (st * np.sqrt(2 * np.pi)))
        * np.exp(-0.5 * ((xv - xb) / st)**2)
    )
    ax.plot(xv, gauss_env, color=ORANGE, lw=1.3, ls="--", alpha=0.82,
            label=f"theory  σ(t) = {st:.2f}", zorder=4)

    # ⟨x⟩ — centre of mass marker
    ax.axvline(xb, color=GOLD, lw=1.4, ls="--", alpha=0.88, zorder=6)
    arrow_y = max_prob * 0.55
    ax.annotate(
        f"⟨x⟩ = {xb:.1f}",
        xy=(xb, arrow_y),
        xytext=(xb + 2.8, arrow_y + max_prob * 0.16),
        color=GOLD, fontsize=9.5, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.1),
        zorder=10,
    )

    # σ_x width — double-headed arrow
    ax.axvline(xb - sx, color=GREEN, lw=0.9, ls=":", alpha=0.65)
    ax.axvline(xb + sx, color=GREEN, lw=0.9, ls=":", alpha=0.65)
    arrow_h = max_prob * 0.14
    ax.annotate(
        "", xy=(xb + sx, arrow_h), xytext=(xb - sx, arrow_h),
        arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.0),
    )
    ax.text(xb, arrow_h + max_prob * 0.04,
            f"2σ_x = {2*sx:.2f}",
            ha="center", color=GREEN, fontsize=8, alpha=0.90)

    ax.axhline(0, color=TEXT, lw=0.4, alpha=0.30)
    ax.set_xlim(*XLIM)
    ax.set_ylim(-0.008 * max_prob, max_prob)

    ax.legend(loc="upper right", fontsize=8.5,
              facecolor=PANEL, edgecolor="#222244", labelcolor=TEXT, framealpha=0.88)

    # Readout overlays
    norm_val = float(np.trapezoid(prob, x))
    ax.text(0.012, 0.955, f"∫|ψ|²dx = {norm_val:.5f}",
            transform=ax.transAxes, color=GREEN, fontsize=8.5)
    ax.text(0.012, 0.870, f"t = {t:.2f}",
            transform=ax.transAxes, color=GOLD, fontsize=11, fontweight="bold")

    # Phase legend (text badges, top-right corner)
    for dy, label, col in [
        (0.955, "φ = −π  →  red",  "#ff3300"),
        (0.895, "φ =  0  →  cyan", "#00ffcc"),
        (0.835, "φ = +π  →  red",  "#ff3300"),
    ]:
        ax.text(0.988, dy, label,
                transform=ax.transAxes, ha="right", fontsize=7,
                color=col, alpha=0.72)

    # ════════════════════════════════════════════════════════
    #  BOTTOM LEFT — Re(ψ)
    # ════════════════════════════════════════════════════════
    ax = ax_re
    style_ax(ax, title=r"Real part   Re($\Psi$)",
             xlabel="x", ylabel=r"Re($\Psi$)", tc=CYAN)

    ax.fill_between(xv, 0, rv, where=(rv >= 0), color=CYAN, alpha=0.20, lw=0)
    ax.fill_between(xv, 0, rv, where=(rv <  0), color=PINK, alpha=0.20, lw=0)
    phase_line(ax, xv, rv, phv, prob=pv, lw=1.6)

    # Amplitude envelope guides
    ax.plot(xv,  env, color=WHITE, lw=0.7, ls="--", alpha=0.30)
    ax.plot(xv, -env, color=WHITE, lw=0.7, ls="--", alpha=0.30)

    ax.axhline(0, color=TEXT, lw=0.4, alpha=0.30)
    ax.axvline(xb, color=GOLD, lw=0.7, ls="--", alpha=0.45)
    ax.set_xlim(*XLIM)
    ax.set_ylim(-max_wave, max_wave)

    # ════════════════════════════════════════════════════════
    #  BOTTOM CENTRE — Im(ψ)
    # ════════════════════════════════════════════════════════
    ax = ax_im
    style_ax(ax, title=r"Imaginary part   Im($\Psi$)",
             xlabel="x", ylabel=r"Im($\Psi$)", tc=PINK)

    ax.fill_between(xv, 0, iv, where=(iv >= 0), color=PINK, alpha=0.20, lw=0)
    ax.fill_between(xv, 0, iv, where=(iv <  0), color=CYAN, alpha=0.20, lw=0)
    phase_line(ax, xv, iv, phv, prob=pv, lw=1.6)

    ax.plot(xv,  env, color=WHITE, lw=0.7, ls="--", alpha=0.30)
    ax.plot(xv, -env, color=WHITE, lw=0.7, ls="--", alpha=0.30)

    ax.axhline(0, color=TEXT, lw=0.4, alpha=0.30)
    ax.axvline(xb, color=GOLD, lw=0.7, ls="--", alpha=0.45)
    ax.set_xlim(*XLIM)
    ax.set_ylim(-max_wave, max_wave)

    # ════════════════════════════════════════════════════════
    #  BOTTOM RIGHT — |φ̃(k)|²  Momentum Space
    # ════════════════════════════════════════════════════════
    ax = ax_mom
    style_ax(ax,
             title=r"Momentum Space   $|\tilde{\Psi}(k,t)|^2$",
             xlabel="Momentum  k",
             ylabel=r"$|\tilde{\Psi}(k)|^2$",
             tc=PURPLE)

    kv = k_shift[kmask]
    mv = mom_dist[kmask]

    # Glow fill
    for alpha, scale in [(0.06, 1.06), (0.14, 1.02), (0.30, 1.00)]:
        ax.fill_between(kv, 0, mv * scale, color=PURPLE, alpha=alpha, lw=0)
    ax.plot(kv, mv, color="#c084fc", lw=1.9, alpha=0.92)

    # k₀ marker
    ax.axvline(K0, color=GOLD, lw=1.1, ls="--", alpha=0.80)
    ax.text(K0 + 0.3, max_mom * 0.80, f"k₀ = {K0}", color=GOLD, fontsize=8)

    # Δk ≈ 1/(2σ₀) — momentum uncertainty
    dk = 1.0 / (2 * SIG0)
    ax.annotate(
        "", xy=(K0 + dk, max_mom * 0.35), xytext=(K0 - dk, max_mom * 0.35),
        arrowprops=dict(arrowstyle="<->", color=GREEN, lw=0.9),
    )
    ax.text(K0, max_mom * 0.43, f"Δk ≈ {dk:.2f}",
            ha="center", color=GREEN, fontsize=7.5, alpha=0.90)

    ax.text(0.05, 0.89, "constant in time\n(free evolution)",
            transform=ax.transAxes, color=TEXT, fontsize=7.5,
            style="italic", alpha=0.62)

    ax.set_xlim(*KLIM)
    ax.set_ylim(0, max_mom)

    # ════════════════════════════════════════════════════════
    #  FIGURE-LEVEL HEADER  (cleared & redrawn each frame)
    # ════════════════════════════════════════════════════════
    for txt in list(fig.texts):
        txt.remove()

    fig.text(
        0.50, 0.960,
        "Simulation 1 — Free Gaussian Wave Packet",
        ha="center", fontsize=17, color=CYAN, fontweight="bold",
    )
    fig.text(
        0.50, 0.922,
        (r"$i\hbar\,\partial_t\Psi = -\dfrac{\hbar^2}{2m}\,\partial_{xx}^2\Psi$"
         r"     V(x) = 0     ℏ = m = 1"
         f"     k₀ = {K0}  (v_g = {K0:.0f},  v_φ = {K0/2:.1f})"
         f"     σ₀ = {SIG0}"
         r"     Δx · Δk ≥ ½"),
        ha="center", fontsize=10, color=GOLD, alpha=0.90,
    )

    if frame % 20 == 0 or frame == NFR - 1:
        print(f"  frame {frame:3d}/{NFR}   t = {t:.2f}   "
              f"⟨x⟩ = {xb:.2f}   σ_x = {sx:.3f}   σ_theory = {st:.3f}")

    return []


# ──────────────────────────────────────────────────────────────────────────────
#  RENDER & SAVE
# ──────────────────────────────────────────────────────────────────────────────
ani = FuncAnimation(fig, update, frames=NFR, interval=1000 / FPS, blit=False)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "free_wave_packet.gif")
print(f"Rendering {NFR} frames → {out}\n")

ani.save(
    out,
    writer=PillowWriter(fps=FPS),
    dpi=110,
    savefig_kwargs={"facecolor": BG},
)
print(f"\n✓  Saved  →  {out}")
plt.show()

