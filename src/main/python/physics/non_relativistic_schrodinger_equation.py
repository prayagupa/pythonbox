#!/usr/bin/env python3
"""
Non-Relativistic Schrödinger Equation — Educational Animation
══════════════════════════════════════════════════════════════
Numerically solves the Time-Dependent Schrödinger Equation (TDSE)
using the Split-Step Fourier (Suzuki–Trotter) method.

    iℏ ∂Ψ/∂t = [ -ℏ²/2m ∇² + V(x,t) ] Ψ

Scene 0 — Title & Equation Overview
Scene 1 — Free Gaussian Wave Packet  (dispersion in vacuum)
Scene 2 — Quantum Tunnelling through a rectangular barrier
Scene 3 — Harmonic Oscillator  (coherent state, classical oscillation)
Scene 4 — Infinite Square Well  (n=1 + n=2 superposition / quantum beating)

Natural units:  ℏ = m = 1
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import warnings
import os

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
PURPLE = "#aa55ff"
WHITE  = "#ffffff"

# ──────────────────────────────────────────────────────────────
# TIMING
# ──────────────────────────────────────────────────────────────
FPS          = 20
SCENE_FRAMES = [55, 95, 120, 110, 110]
CUMULATIVE   = np.cumsum([0] + SCENE_FRAMES)
TOTAL_FRAMES = sum(SCENE_FRAMES)

np.random.seed(42)


# ══════════════════════════════════════════════════════════════
#  QUANTUM SOLVER  —  Split-Step Fourier Method
# ══════════════════════════════════════════════════════════════

def gaussian_wave_packet(x, x0, sigma, k0):
    """Normalised Gaussian wave packet centred at x0 with momentum ℏk0."""
    norm = (2 * np.pi * sigma ** 2) ** (-0.25)
    return norm * np.exp(-((x - x0) ** 2) / (4 * sigma ** 2)) * np.exp(1j * k0 * x)


def split_step_evolve(psi, V, dx, dt, n_steps=1):
    """
    Advance ψ by n_steps × dt using the Suzuki–Trotter split-step method
    (second-order accurate):

        ψ(t+dt) ≈ exp(-iV dt/2) · IFFT[ exp(-iK dt) · FFT[ exp(-iV dt/2) ψ(t) ] ]

    In natural units (ℏ = m = 1): K = k²/2.
    """
    N   = len(psi)
    k   = np.fft.fftfreq(N, d=dx) * 2 * np.pi      # wave-number grid
    K   = 0.5 * k ** 2                               # kinetic energies (ℏ=m=1)
    eV  = np.exp(-0.5j * V * dt)                     # half-step potential phase
    eK  = np.exp(-1j * K * dt)                       # full-step kinetic phase
    for _ in range(n_steps):
        psi = eV * psi
        psi = np.fft.ifft(eK * np.fft.fft(psi))
        psi = eV * psi
    return psi


def precompute(x, psi0, V, dx, dt, n_frames, spf=4):
    """Pre-compute wave-function snapshots for every animation frame."""
    print(f"  computing {n_frames} frames …", end=" ", flush=True)
    states = [psi0.copy()]
    psi = psi0.copy()
    for _ in range(n_frames - 1):
        psi = split_step_evolve(psi, V, dx, dt, n_steps=spf)
        states.append(psi.copy())
    print("done.")
    return states


# ══════════════════════════════════════════════════════════════
#  SPATIAL GRID
# ══════════════════════════════════════════════════════════════

N  = 1024
L  = 80.0
dx = L / N
x  = np.linspace(-L / 2, L / 2, N, endpoint=False)

# ──────────────────────────────────────────────────────────────
# Scene 1 — Free Gaussian wave packet
# ──────────────────────────────────────────────────────────────
print("Scene 1 — free particle")
psi1 = gaussian_wave_packet(x, x0=-12.0, sigma=2.5, k0=3.0)
V1   = np.zeros(N)
s1   = precompute(x, psi1, V1, dx, dt=0.04, n_frames=SCENE_FRAMES[1])

# ──────────────────────────────────────────────────────────────
# Scene 2 — Quantum tunnelling
# ──────────────────────────────────────────────────────────────
print("Scene 2 — quantum tunnelling")
V0, bw, bc = 4.0, 1.5, 6.0
V2 = np.where((x >= bc - bw / 2) & (x <= bc + bw / 2), V0, 0.0)
psi2 = gaussian_wave_packet(x, x0=-14.0, sigma=2.5, k0=2.5)
s2   = precompute(x, psi2, V2, dx, dt=0.04, n_frames=SCENE_FRAMES[2])

# ──────────────────────────────────────────────────────────────
# Scene 3 — Harmonic oscillator (coherent state)
# ──────────────────────────────────────────────────────────────
print("Scene 3 — harmonic oscillator")
omega = 1.0
V3    = 0.5 * omega ** 2 * x ** 2
psi3  = gaussian_wave_packet(x, x0=5.0, sigma=1.0, k0=0.0)
s3    = precompute(x, psi3, V3, dx, dt=0.04, n_frames=SCENE_FRAMES[3], spf=3)

# ──────────────────────────────────────────────────────────────
# Scene 4 — Infinite square well (superposition n=1 and n=2)
# ──────────────────────────────────────────────────────────────
print("Scene 4 — infinite square well")
well_L = 20.0
V4     = np.where(np.abs(x) <= well_L / 2, 0.0, 1e6)

def box_state(n):
    psi = np.sqrt(2 / well_L) * np.sin(n * np.pi * (x + well_L / 2) / well_L)
    return np.where(np.abs(x) <= well_L / 2, psi, 0.0)

psi4 = (box_state(1) + box_state(2)).astype(complex) / np.sqrt(2)
s4   = precompute(x, psi4, V4, dx, dt=0.02, n_frames=SCENE_FRAMES[4], spf=3)

print(f"\nAll states ready. Rendering {TOTAL_FRAMES} frames at {FPS} fps …\n")


# ══════════════════════════════════════════════════════════════
#  FIGURE
# ══════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(16, 9), facecolor=BG)


def get_scene(frame):
    for i, (a, b) in enumerate(zip(CUMULATIVE[:-1], CUMULATIVE[1:])):
        if frame < b:
            loc = frame - a
            t   = loc / max(b - a - 1, 1)
            return i, loc, t
    return len(SCENE_FRAMES) - 1, frame - CUMULATIVE[-2], 1.0


def clear_fig():
    fig.clf()
    fig.patch.set_facecolor(BG)


# ══════════════════════════════════════════════════════════════
#  SCENE 0 — TITLE
# ══════════════════════════════════════════════════════════════

def render_scene0(local, t):
    clear_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")

    fade = min(1.0, t * 2.5)

    # ── title ──
    ax.text(8, 7.6, "Non-Relativistic Schrödinger Equation",
            ha="center", va="center", fontsize=22, color=CYAN,
            fontweight="bold", alpha=fade)

    # ── main equation ──
    eq_a = min(1.0, max(0.0, t * 4 - 0.5))
    ax.text(8, 6.1,
            r"$i\hbar\,\dfrac{\partial\Psi}{\partial t} ="
            r"\!\left[-\dfrac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r},t)\right]\!\Psi$",
            ha="center", va="center", fontsize=30, color=GOLD, alpha=eq_a)

    # ── term annotations ──
    ann_a = min(1.0, max(0.0, t * 5 - 1.8))
    for lx, formula, desc, col in [
        (2.8,  r"$\Psi$",                   "wave function",     CYAN),
        (7.0,  r"$-\frac{\hbar^2}{2m}∇^2$", "kinetic energy",    GREEN),
        (12.5, r"$V(\mathbf{r},t)$",         "potential energy",  ORANGE),
    ]:
        ax.text(lx, 4.5, formula, ha="center", fontsize=15, color=col, alpha=ann_a)
        ax.text(lx, 3.9, desc,   ha="center", fontsize=10, color=TEXT, alpha=ann_a * 0.8)

    # ── scene list ──
    lst_a = min(1.0, max(0.0, t * 6 - 2.5))
    scenes_txt = [
        "① Free Gaussian Wave Packet  —  dispersion in vacuum",
        "② Quantum Tunnelling  —  through a rectangular barrier",
        "③ Harmonic Oscillator  —  coherent-state oscillation",
        "④ Infinite Square Well  —  superposition & quantum beating",
    ]
    for i, s in enumerate(scenes_txt):
        ax.text(8, 3.05 - i * 0.58, s,
                ha="center", fontsize=11, color=PINK, alpha=lst_a)

    ax.text(8, 0.40,
            "Numerical method:  Split-Step Fourier (Suzuki–Trotter, 2nd order)   |   ℏ = m = 1",
            ha="center", fontsize=9, color=TEXT, alpha=ann_a * 0.65)


# ══════════════════════════════════════════════════════════════
#  GENERIC WAVE-FUNCTION RENDERER  (scenes 1–4)
# ══════════════════════════════════════════════════════════════

def render_wave(states, V_display, local, title,
                xlim, ylim_prob, ylim_wave,
                footer="", V_scale=1.0, V_color=ORANGE):
    """Two-panel layout: |ψ|² + potential  /  Re(ψ) & Im(ψ)."""
    clear_fig()
    fig.subplots_adjust(left=0.09, right=0.97, top=0.90,
                        bottom=0.09, hspace=0.52)
    ax_p = fig.add_subplot(2, 1, 1)   # probability density
    ax_w = fig.add_subplot(2, 1, 2)   # real & imaginary parts

    for ax in (ax_p, ax_w):
        ax.set_facecolor("#07071a")
        ax.tick_params(colors=TEXT, labelsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor("#22224a")

    psi  = states[local]
    prob = np.abs(psi) ** 2

    # ── |ψ|² ──
    ax_p.fill_between(x, 0, prob, color=CYAN, alpha=0.45)
    ax_p.plot(x, prob, color=CYAN, lw=1.4, label=r"$|\Psi|^2$")

    if V_display is not None:
        V_plot = V_display / V_scale * ylim_prob[1] * 0.80
        ax_p.fill_between(x, 0, V_plot, color=V_color, alpha=0.20)
        ax_p.plot(x, V_plot, color=V_color, lw=1.3, ls="--",
                  alpha=0.85, label="V(x)  [scaled]")

    ax_p.set_xlim(*xlim)
    ax_p.set_ylim(*ylim_prob)
    ax_p.set_xlabel("Position  x", color=TEXT, fontsize=10)
    ax_p.set_ylabel(r"$|\Psi(x,t)|^2$", color=TEXT, fontsize=10)
    ax_p.set_title(title, color=TEXT, fontsize=11, pad=4)
    ax_p.legend(loc="upper right", fontsize=8,
                facecolor="#07071a", edgecolor="#22224a", labelcolor=TEXT)

    norm = np.trapezoid(prob, x)
    ax_p.text(0.02, 0.91, f"∫|ψ|²dx = {norm:.4f}",
              transform=ax_p.transAxes, fontsize=8, color=GREEN)

    # expectation value <x>
    xbar = np.trapezoid(x * prob, x)
    ax_p.axvline(xbar, color=GOLD, lw=0.9, ls=":", alpha=0.8)
    ax_p.text(xbar, ylim_prob[1] * 0.92, f"⟨x⟩={xbar:.1f}",
              color=GOLD, fontsize=7, ha="center")

    # ── Re(ψ) and Im(ψ) ──
    ax_w.plot(x, psi.real, color=CYAN, lw=1.1,
              label=r"Re($\Psi$)", alpha=0.90)
    ax_w.plot(x, psi.imag, color=PINK, lw=1.1,
              label=r"Im($\Psi$)", alpha=0.90)
    ax_w.fill_between(x, 0, psi.real, color=CYAN, alpha=0.14)
    ax_w.fill_between(x, 0, psi.imag, color=PINK, alpha=0.12)
    ax_w.axhline(0, color=TEXT, lw=0.4, alpha=0.45)

    ax_w.set_xlim(*xlim)
    ax_w.set_ylim(*ylim_wave)
    ax_w.set_xlabel("Position  x", color=TEXT, fontsize=10)
    ax_w.set_ylabel(r"$\Psi(x,t)$", color=TEXT, fontsize=10)
    ax_w.set_title("Real  &  Imaginary Components", color=TEXT, fontsize=11, pad=4)
    ax_w.legend(loc="upper right", fontsize=8,
                facecolor="#07071a", edgecolor="#22224a", labelcolor=TEXT)

    # shared header + footer
    fig.text(0.50, 0.955,
             "Non-Relativistic Schrödinger Equation — iℏ ∂Ψ/∂t = [−ℏ²∇²/2m + V] Ψ",
             ha="center", fontsize=12, color=CYAN, fontweight="bold")
    if footer:
        fig.text(0.50, 0.010, footer,
                 ha="center", fontsize=8.5, color=GOLD, alpha=0.80)


# ══════════════════════════════════════════════════════════════
#  INDIVIDUAL SCENE CALLS
# ══════════════════════════════════════════════════════════════

def render_scene1(local, t):
    render_wave(
        states=s1, V_display=None, local=local,
        title="Scene 1 — Free Gaussian Wave Packet  (no potential)",
        xlim=(-30, 30), ylim_prob=(0, 0.30), ylim_wave=(-0.50, 0.50),
        footer="V(x) = 0   |   k₀ = 3.0,  σ₀ = 2.5   |   "
               "packet disperses as group velocity ≠ phase velocity",
    )


def render_scene2(local, t):
    render_wave(
        states=s2, V_display=V2, local=local,
        title="Scene 2 — Quantum Tunnelling through a Rectangular Barrier",
        xlim=(-28, 28), ylim_prob=(0, 0.26), ylim_wave=(-0.48, 0.48),
        V_scale=V0, V_color=ORANGE,
        footer=f"Barrier:  V₀ = {V0},  width = {bw},  centre = {bc}   |   "
               f"E_k ≈ k₀²/2 = 3.1 < V₀ = {V0}   →   classically forbidden, yet tunnelling occurs",
    )


def render_scene3(local, t):
    render_wave(
        states=s3, V_display=V3, local=local,
        title="Scene 3 — Harmonic Oscillator  (Coherent State)",
        xlim=(-16, 16), ylim_prob=(0, 0.50), ylim_wave=(-0.65, 0.65),
        V_scale=20.0, V_color=GREEN,
        footer="V(x) = ½ω²x²  (ω = 1)   |   "
               "coherent state preserves its shape while oscillating — mimics a classical particle",
    )


def render_scene4(local, t):
    V4_vis = np.where(np.abs(x) <= well_L / 2, 0.0, 6.0)
    render_wave(
        states=s4, V_display=V4_vis, local=local,
        title="Scene 4 — Infinite Square Well  (n=1 + n=2 superposition)",
        xlim=(-16, 16), ylim_prob=(0, 0.22), ylim_wave=(-0.38, 0.38),
        V_scale=6.0, V_color=PURPLE,
        footer=f"Ψ = (φ₁ + φ₂)/√2,  well width = {well_L}   |   "
               "probability density oscillates — quantum beating at Δω = E₂ − E₁",
    )


# ══════════════════════════════════════════════════════════════
#  MASTER ANIMATION UPDATE
# ══════════════════════════════════════════════════════════════

RENDERERS = [
    lambda loc, t: render_scene0(loc, t),
    lambda loc, t: render_scene1(loc, t),
    lambda loc, t: render_scene2(loc, t),
    lambda loc, t: render_scene3(loc, t),
    lambda loc, t: render_scene4(loc, t),
]


def update(frame):
    scene, local, t = get_scene(frame)
    RENDERERS[scene](local, t)
    if frame % 20 == 0:
        print(f"  frame {frame:>3}/{TOTAL_FRAMES}  scene {scene}  t={t:.2f}")
    return []


# ══════════════════════════════════════════════════════════════
#  RENDER & SAVE
# ══════════════════════════════════════════════════════════════

ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES,
                    interval=1000 / FPS, blit=False)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "schrodinger_equation.gif")

ani.save(out, writer=PillowWriter(fps=FPS),
         savefig_kwargs={"facecolor": BG})

print(f"\n✓  Saved  →  {out}")
plt.show()

