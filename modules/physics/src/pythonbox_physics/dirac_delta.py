#!/usr/bin/env python3
"""
Dirac Delta Function  —  Four-Panel Animated Visualisation
══════════════════════════════════════════════════════════════
An educational animation that shows four complementary views of δ(x):

  Panel 1 — Gaussian Squeeze
      δ_σ(x) = (1/σ√2π) exp(−x²/2σ²)  as σ → 0
      The bell curve narrows and grows infinitely tall while its
      area remains exactly 1.

  Panel 2 — Four Representations Converging
      Gaussian · Lorentzian · Rectangular (top-hat) · Sinc²
      All share the same scale parameter σ and all converge to δ(x).

  Panel 3 — Fourier / Dirichlet Kernel
      δ_K(x) = sin(Kx) / (πx)  as K → ∞
      The partial Fourier integral becomes a sharper and sharper spike
      surrounded by the famous Gibbs oscillations.

  Panel 4 — Sifting Property
      ∫ f(x) δ(x − a) dx = f(a)
      A glowing cursor sweeps across a test function, picking out
      the exact value at each location.

Run from the repo root:
    python modules/physics/src/pythonbox_physics/dirac_delta.py

Output: dirac_delta.gif  (saved next to this script)

Dependencies: numpy, matplotlib, pillow  (all in requirements.txt)
"""

import numpy as np
import matplotlib

# ── macOS / headless backend fallback (mirrors spacetime_curvature.py) ────────
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _probe  # noqa: F401
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ── Output path ───────────────────────────────────────────────────────────────
OUT_PATH = Path(__file__).parent / "dirac_delta.gif"

# ── Colour palette  (deep-space aesthetic) ────────────────────────────────────
BG     = "#04040f"   # near-black background
PANEL  = "#07071c"   # axis face
TEXT   = "#dde8ff"   # soft white labels
CYAN   = "#00e5ff"   # Gaussian  /  sifting cursor
GOLD   = "#ffd166"   # Lorentzian
GREEN  = "#06d6a0"   # Rectangular
PINK   = "#ef476f"   # Sinc² / negative fill
PURPLE = "#c084fc"   # Fourier kernel
ORANGE = "#ff9a3c"   # test function f(x)
WHITE  = "#ffffff"
DIM    = "#2e3a60"   # grid / spine
HLGREEN = "#39ff14"  # highlight green for sifting dot

# ── Spatial grid ──────────────────────────────────────────────────────────────
N_X   = 4000                          # grid points  (fine enough for narrow σ)
X_MAX = 7.0
x     = np.linspace(-X_MAX, X_MAX, N_X)

XLIM  = (-5.5, 5.5)                   # display window for all panels

# ── Animation timeline ────────────────────────────────────────────────────────
N_FRAMES = 220
FPS      = 22

t          = np.linspace(0.0, 1.0, N_FRAMES)

# σ: exponential squeeze from 1.8 down to 0.035
SIGMA_I    = 1.8
SIGMA_F    = 0.035
sigma_vals = SIGMA_I * np.exp(np.log(SIGMA_F / SIGMA_I) * t)

# Fourier cutoff K: linear ramp from 0.6 to 34
K_vals = 0.6 + 33.4 * t

# Sifting: cursor 'a' sweeps sinusoidally twice across [−4, 4]
a_vals = 4.0 * np.sin(2.3 * np.pi * t)

# ── Delta-function approximations ─────────────────────────────────────────────


def gauss(xv: np.ndarray, sig: float) -> np.ndarray:
    """Gaussian approximation: δ_σ(x) = (1/σ√2π) exp(−x²/2σ²)."""
    return np.exp(-xv ** 2 / (2.0 * sig ** 2)) / (sig * np.sqrt(2.0 * np.pi))


def lorentz(xv: np.ndarray, sig: float) -> np.ndarray:
    """Lorentzian (Cauchy): δ_σ(x) = (σ/π) / (x² + σ²).
    Peak = 1/(πσ),  integral = 1."""
    return (sig / np.pi) / (xv ** 2 + sig ** 2)


def rect(xv: np.ndarray, sig: float) -> np.ndarray:
    """Rectangular (top-hat): 1/(2σ) for |x| ≤ σ, else 0.
    Peak = 1/(2σ),  integral = 1."""
    return np.where(np.abs(xv) <= sig, 0.5 / sig, 0.0)


def sinc2(xv: np.ndarray, sig: float) -> np.ndarray:
    """Fejér / sinc² kernel: σ·sin²(x/σ) / (πx²).
    Peak = 1/(πσ),  integral = 1."""
    with np.errstate(divide="ignore", invalid="ignore"):
        v = sig * np.sin(xv / sig) ** 2 / (np.pi * xv ** 2)
    return np.where(np.abs(xv) < 1e-9, 1.0 / (np.pi * sig), v)


def dirichlet(xv: np.ndarray, K: float) -> np.ndarray:
    """Dirichlet kernel: sin(Kx)/(πx)  →  δ(x) as K → ∞."""
    with np.errstate(divide="ignore", invalid="ignore"):
        v = np.sin(K * xv) / (np.pi * xv)
    return np.where(np.abs(xv) < 1e-9, K / np.pi, v)


def f_test(xv: np.ndarray) -> np.ndarray:
    """Smooth test function for the sifting property panel."""
    return (
        1.3 * np.sin(1.8 * xv)
        + 0.55 * np.cos(3.5 * xv)
        + 0.25 * np.sin(6.5 * xv)
    )


f_vals = f_test(x)

# ── Fixed y-axis limits (computed from extreme frame σ = SIGMA_F) ─────────────
_gauss_peak_max  = 1.0 / (SIGMA_F * np.sqrt(2.0 * np.pi))   # ~11.4
_rect_peak_max   = 0.5 / SIGMA_F                              # ~14.3
_kmax            = K_vals[-1]                                 # 34

Y_P1_MAX   = _gauss_peak_max * 1.14          # ~13   (Gaussian only)
Y_P2_MAX   = _rect_peak_max  * 1.12          # ~16   (all four)
Y_P3_MAX   = (_kmax / np.pi) * 1.14          # ~12.3
Y_P3_MIN   = -(_kmax / np.pi) * 0.38         # ~-4.1
Y_P4       = (-2.4, 2.4)                     # f(x) range

# ── Pre-compute all frame data ────────────────────────────────────────────────
print("Pre-computing frame data …")
frames: list[dict] = []
for i in range(N_FRAMES):
    sig = float(sigma_vals[i])
    K   = float(K_vals[i])
    a   = float(a_vals[i])
    frames.append(
        {
            "sigma": sig,
            "K":     K,
            "a":     a,
            "g":     gauss(x, sig),
            "l":     lorentz(x, sig),
            "r":     rect(x, sig),
            "s":     sinc2(x, sig),
            "fd":    dirichlet(x, K),
        }
    )
print(f"Done — {N_FRAMES} frames ready.")

# ── Figure & axes ─────────────────────────────────────────────────────────────
print("Setting up figure …")
fig = plt.figure(figsize=(14, 9.5), facecolor=BG)

gs = GridSpec(
    3, 2,
    figure=fig,
    height_ratios=[0.055, 1, 1],
    hspace=0.52,
    wspace=0.30,
    top=0.93, bottom=0.07,
    left=0.07, right=0.97,
)

ax_title = fig.add_subplot(gs[0, :])
ax1      = fig.add_subplot(gs[1, 0])   # Gaussian squeeze
ax2      = fig.add_subplot(gs[1, 1])   # Four representations
ax3      = fig.add_subplot(gs[2, 0])   # Fourier / Dirichlet
ax4      = fig.add_subplot(gs[2, 1])   # Sifting property

# Title strip
ax_title.set_axis_off()
ax_title.text(
    0.5, 0.55,
    "Dirac  Delta  Function  —  δ(x)",
    transform=ax_title.transAxes,
    color=WHITE, fontsize=17.5, fontweight="bold",
    ha="center", va="center", fontfamily="monospace",
)
ax_title.text(
    0.5, -0.3,
    r"$\int_{-\infty}^{\,\infty}\delta(x)\,dx = 1$"
    r"     $\delta(x) = 0\ \ (x \neq 0)$"
    r"     $\int f(x)\,\delta(x-a)\,dx = f(a)$",
    transform=ax_title.transAxes,
    color=GOLD, fontsize=9, ha="center", va="center",
    alpha=0.85,
)


# ── Axis decorator ────────────────────────────────────────────────────────────
def _decorate(ax, title: str) -> None:
    """Apply shared dark-space styling after ax.cla()."""
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=TEXT, fontsize=8.8, pad=5)
    ax.set_xlabel("x", color=TEXT, fontsize=8.5, labelpad=2)
    ax.tick_params(colors=TEXT, labelsize=7.2)
    ax.axhline(0, color=DIM, lw=0.9, ls="--", zorder=0)
    ax.axvline(0, color=DIM, lw=0.7, ls=":",  zorder=0)
    for sp in ax.spines.values():
        sp.set_color(DIM)


# ── Panel badge (small info box) ──────────────────────────────────────────────
def _badge(ax, text: str, color: str = TEXT) -> None:
    ax.text(
        0.975, 0.965, text,
        transform=ax.transAxes,
        ha="right", va="top",
        color=color, fontsize=9.0, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.25", fc="#0a0a2a", ec=color,
                  lw=0.8, alpha=0.85),
    )


# ── Animation function ────────────────────────────────────────────────────────
def animate(fi: int) -> None:
    d   = frames[fi]
    sig = d["sigma"]
    K   = d["K"]
    a   = d["a"]

    # ── Panel 1 — Gaussian Squeeze ────────────────────────────────────────────
    ax1.cla()
    _decorate(
        ax1,
        r"Gaussian Squeeze:  "
        r"$\delta_\sigma(x)=\dfrac{1}{\sigma\sqrt{2\pi}}\,e^{-x^2/2\sigma^2}$",
    )
    g = d["g"]
    ax1.fill_between(x, g, color=CYAN, alpha=0.20, zorder=2)
    ax1.plot(x, g, color=CYAN, lw=2.2, zorder=3)
    ax1.set_xlim(XLIM)
    ax1.set_ylim(0, Y_P1_MAX)
    _badge(ax1, f"σ = {sig:.3f}", CYAN)
    ax1.text(
        0.03, 0.96,
        r"$\int\!\delta_\sigma\,dx = 1$",
        transform=ax1.transAxes, ha="left", va="top",
        color=GREEN, fontsize=8.5, alpha=0.9,
    )
    # Peak marker
    peak_h = 1.0 / (sig * np.sqrt(2.0 * np.pi))
    ax1.plot([0.0], [peak_h], "o", color=WHITE, ms=4.5, zorder=5)
    ax1.text(
        0.975, 0.79,
        f"peak = {peak_h:.1f}",
        transform=ax1.transAxes, ha="right", va="top",
        color=TEXT, fontsize=7.8,
    )

    # ── Panel 2 — Four Representations ───────────────────────────────────────
    ax2.cla()
    _decorate(ax2, "Four Representations  (same σ parameter)")
    ax2.fill_between(x, d["g"], color=CYAN,   alpha=0.10, zorder=1)
    ax2.fill_between(x, d["s"], color=PINK,   alpha=0.10, zorder=1)
    ax2.plot(x, d["g"], color=CYAN,   lw=1.9, label="Gaussian",    zorder=3)
    ax2.plot(x, d["l"], color=GOLD,   lw=1.9, label="Lorentzian",  zorder=3)
    ax2.plot(x, d["r"], color=GREEN,  lw=2.0, label="Rectangular", zorder=3)
    ax2.plot(x, d["s"], color=PINK,   lw=1.9, label="Sinc²",       zorder=3)
    ax2.set_xlim(XLIM)
    ax2.set_ylim(-0.4, Y_P2_MAX)
    ax2.legend(
        loc="upper left", fontsize=7.2,
        facecolor="#0d0d2e", edgecolor=DIM,
        labelcolor=TEXT, framealpha=0.88,
    )
    _badge(ax2, f"σ = {sig:.3f}", TEXT)

    # ── Panel 3 — Fourier / Dirichlet Kernel ──────────────────────────────────
    ax3.cla()
    _decorate(
        ax3,
        r"Fourier Kernel:  "
        r"$\delta_K(x)=\dfrac{\sin(Kx)}{\pi x}\;\xrightarrow{K\to\infty}\;\delta(x)$",
    )
    fd = d["fd"]
    ax3.fill_between(x, fd, 0,
                     where=(fd >= 0), color=PURPLE, alpha=0.22, zorder=2)
    ax3.fill_between(x, fd, 0,
                     where=(fd <  0), color=PINK,   alpha=0.14, zorder=2)
    ax3.plot(x, fd, color=PURPLE, lw=1.9, zorder=3)
    # Central peak dot
    ax3.plot([0.0], [K / np.pi], "o", color=WHITE, ms=4.5, zorder=5)
    ax3.set_xlim(XLIM)
    ax3.set_ylim(Y_P3_MIN, Y_P3_MAX)
    _badge(ax3, f"K = {K:.1f}", PURPLE)
    ax3.text(
        0.03, 0.96,
        r"Gibbs oscillations $\to 0$ as $K \to \infty$",
        transform=ax3.transAxes, ha="left", va="top",
        color=PINK, fontsize=7.2, alpha=0.85,
    )

    # ── Panel 4 — Sifting Property ────────────────────────────────────────────
    ax4.cla()
    _decorate(
        ax4,
        r"Sifting Property:  "
        r"$\int f(x)\,\delta(x-a)\,dx = f(a)$",
    )
    # Test function
    ax4.plot(x, f_vals, color=ORANGE, lw=2.2, alpha=0.90,
             zorder=2, label="f(x)")
    # δ-cursor: vertical line + shaded strip
    ax4.axvline(a, color=CYAN, lw=2.2, alpha=0.90, zorder=4)
    strip_w = max(0.06, sig * 0.5)          # strip narrows with σ
    ax4.axvspan(a - strip_w, a + strip_w,
                color=CYAN, alpha=0.18, zorder=3)
    # f(a) value
    fa = float(f_test(np.array([a])))
    # Horizontal dashed line at f(a)
    ax4.axhline(fa, color=CYAN, lw=0.9, ls=":",
                alpha=0.55, zorder=1)
    # Glowing dot at (a, f(a))
    ax4.scatter([a], [fa], color=PANEL,    s=110, zorder=6)
    ax4.scatter([a], [fa], color=HLGREEN,  s=70,  zorder=7)
    ax4.scatter([a], [fa], color=WHITE,    s=22,  zorder=8)
    ax4.set_xlim(XLIM)
    ax4.set_ylim(*Y_P4)
    ax4.legend(
        loc="upper left", fontsize=7.2,
        facecolor="#0d0d2e", edgecolor=DIM,
        labelcolor=TEXT, framealpha=0.88,
    )
    _badge(ax4, f"a={a:+.2f}   f(a)={fa:+.2f}", HLGREEN)

    if fi % 44 == 0:
        print(f"  [{fi * 100 // N_FRAMES:3d}%] frame {fi}/{N_FRAMES}"
              f"  σ={sig:.4f}  K={K:.1f}  a={a:.2f}")


# ── Build & save ───────────────────────────────────────────────────────────────
print(f"Rendering {N_FRAMES} frames to GIF …")
anim = animation.FuncAnimation(
    fig, animate,
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
