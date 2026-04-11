#!/usr/bin/env python3
"""
Free Gaussian Wave Packet — Pure Visual GIF
Two panels stacked vertically, no text, no axes, no labels.
Top:    |ψ(x,t)|²  probability density with phase-rainbow glow
Bottom: Re(ψ) and Im(ψ) overlaid with phase coloring
"""

import os
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection

warnings.filterwarnings("ignore")

# ── Colour palette ────────────────────────────────────────────────────────────
BG     = "#0e0300"
PANEL  = "#1a0500"
ORANGE = "#ff6d00"
RED    = "#ff1744"
YELLOW = "#ffd600"
WHITE  = "#ffffff"

# ── Grid & physics ────────────────────────────────────────────────────────────
N    = 1024
L    = 80.0
dx   = L / N
x    = np.linspace(-L / 2, L / 2, N, endpoint=False)

X0   = -15.0
SIG0 = 2.0
K0   = 3.0

DT   = 0.04
SPF  = 3
NFR  = 130
FPS  = 22

# ── Split-step solver ─────────────────────────────────────────────────────────
k_grid = np.fft.fftfreq(N, d=dx) * 2 * np.pi
eK     = np.exp(-1j * 0.5 * k_grid**2 * DT)


def evolve(psi, steps=1):
    for _ in range(steps):
        psi = np.fft.ifft(eK * np.fft.fft(psi))
    return psi


# ── Initial state ─────────────────────────────────────────────────────────────
norm0 = (2 * np.pi * SIG0**2) ** (-0.25)
psi0  = norm0 * np.exp(-(x - X0)**2 / (4 * SIG0**2)) * np.exp(1j * K0 * x)

# ── Pre-compute all states ────────────────────────────────────────────────────
print(f"Pre-computing {NFR} frames … ", end="", flush=True)
states = [psi0.copy()]
psi = psi0.copy()
for _ in range(NFR - 1):
    psi = evolve(psi, SPF)
    states.append(psi.copy())
print("done.")

prob_all = [np.abs(s)**2 for s in states]

# ── Display region ────────────────────────────────────────────────────────────
XLIM  = (-30, 32)
xmask = (x >= XLIM[0]) & (x <= XLIM[1])

max_prob = max(np.max(p[xmask]) for p in prob_all) * 1.12
max_wave = max(
    max(np.max(np.abs(s[xmask].real)), np.max(np.abs(s[xmask].imag)))
    for s in states
) * 1.15


# ── Phase-rainbow line helper ─────────────────────────────────────────────────
def phase_line(ax, xv, yv, phase, prob=None, lw=1.9, base_alpha=0.95):
    rgba = plt.cm.hsv((phase + np.pi) / (2 * np.pi)).copy()
    if prob is not None:
        fade = np.sqrt(np.clip(prob / (max_prob * 0.04), 0.0, 1.0))
        rgba[:, 3] = base_alpha * fade
    else:
        rgba[:, 3] = base_alpha
    pts  = np.array([xv, yv]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc   = LineCollection(segs, colors=rgba[:-1], linewidths=lw)
    ax.add_collection(lc)


def glow_fill(ax, xv, yv, color=ORANGE):
    for alpha, scale in [(0.04, 1.08), (0.09, 1.04), (0.18, 1.01), (0.35, 1.00)]:
        ax.fill_between(xv, 0, yv * scale, color=color, alpha=alpha, linewidth=0)


def strip_ax(ax, xlim, ylim):
    """Remove all text, ticks, borders — pure visual."""
    ax.set_facecolor(PANEL)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


# ── Figure layout ─────────────────────────────────────────────────────────────
fig, (ax_top, ax_bottom) = plt.subplots(
    2, 1,
    figsize=(14, 8),
    facecolor=BG,
    gridspec_kw={"hspace": 0.015},
)


# ── Animation update ──────────────────────────────────────────────────────────
def update(frame):
    ax_top.cla()
    ax_bottom.cla()

    psi   = states[frame]
    prob  = prob_all[frame]
    phase = np.angle(psi)

    xv  = x[xmask]
    pv  = prob[xmask]
    phv = phase[xmask]
    rv  = psi[xmask].real
    iv  = psi[xmask].imag
    env = np.sqrt(pv)

    # ── Top panel: |ψ|² ──────────────────────────────────────────────────────
    strip_ax(ax_top, XLIM, (-0.006 * max_prob, max_prob))

    glow_fill(ax_top, xv, pv, ORANGE)
    phase_line(ax_top, xv, pv, phv, prob=pv, lw=2.4)
    ax_top.plot(xv, pv, color=YELLOW, lw=0.55, alpha=0.35, zorder=5)
    ax_top.axhline(0, color=WHITE, lw=0.3, alpha=0.15)

    # ── Bottom panel: Re(ψ) + Im(ψ) ──────────────────────────────────────────
    strip_ax(ax_bottom, XLIM, (-max_wave, max_wave))

    # Im fill
    ax_bottom.fill_between(xv, 0, iv, where=(iv >= 0), color=RED,    alpha=0.18, lw=0)
    ax_bottom.fill_between(xv, 0, iv, where=(iv <  0), color=ORANGE, alpha=0.18, lw=0)
    # Re fill
    ax_bottom.fill_between(xv, 0, rv, where=(rv >= 0), color=ORANGE, alpha=0.18, lw=0)
    ax_bottom.fill_between(xv, 0, rv, where=(rv <  0), color=RED,    alpha=0.18, lw=0)

    # Amplitude envelope guides
    ax_bottom.plot(xv,  env, color=YELLOW, lw=0.7, ls="--", alpha=0.25)
    ax_bottom.plot(xv, -env, color=YELLOW, lw=0.7, ls="--", alpha=0.25)

    # Phase-coloured waveform lines
    phase_line(ax_bottom, xv, rv, phv, prob=pv, lw=1.7)
    phase_line(ax_bottom, xv, iv, phv, prob=pv, lw=1.7, base_alpha=0.65)

    ax_bottom.axhline(0, color=WHITE, lw=0.3, alpha=0.15)

    return []


# ── Render & save ─────────────────────────────────────────────────────────────
ani = FuncAnimation(fig, update, frames=NFR, interval=1000 / FPS, blit=False)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "free_wave_packet_visual.gif")
print(f"\nRendering {NFR} frames → {out}\n")

ani.save(
    out,
    writer=PillowWriter(fps=FPS),
    dpi=120,
    savefig_kwargs={"facecolor": BG},
)
print(f"\n✓  Saved → {out}")

# Re-create the animation for the live interactive window
ani_live = FuncAnimation(fig, update, frames=NFR, interval=1000 / FPS, blit=False)
print("\nOpening interactive window … (close the window to exit)")
plt.show()
plt.close(fig)

