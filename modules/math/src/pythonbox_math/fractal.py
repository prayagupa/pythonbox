"""
fractal.py — Beautiful Fractals Animation
==========================================
Animates four fractals in a 2×2 panel:

  1. Mandelbrot Set     — colour wave rippling through the set (twilight cyclic map)
  2. Julia Set          — c parameter rotates on a circle → mesmerising morph
  3. Burning Ship       — colour wave cycling over the inferno (hsv cyclic map)
  4. Sierpiński Triangle— chaos-game progressive point reveal

Run:  python fractal.py
Output: fractals_animation.gif  (also opens an interactive window)

📖  Math & theory: docs/06_fractals_julia_set.md
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
from matplotlib.animation import FuncAnimation, PillowWriter


# ── settings ──────────────────────────────────────────────────────────────────

N_FRAMES = 72      # total animation frames
FPS      = 18      # playback speed
RES      = 500     # pixels per panel side  (lower → faster precompute)
MAX_ITER = 180     # escape-time depth


# ── helpers ───────────────────────────────────────────────────────────────────

def _grid(x0, x1, y0, y1, w=RES, h=RES):
    """Create a 2-D grid of complex numbers."""
    return (np.linspace(x0, x1, w)[np.newaxis, :]
            + 1j * np.linspace(y0, y1, h)[:, np.newaxis])


# ── fractal kernels ───────────────────────────────────────────────────────────

def _escape(grid, julia_c=None, max_iter=MAX_ITER):
    """
    Generic smooth escape-time algorithm.
    Pass julia_c to switch from Mandelbrot to Julia mode.
    """
    z = grid.copy() if julia_c is not None else np.zeros_like(grid)
    iteration = np.zeros(grid.shape, dtype=np.float32)
    mask = np.ones(grid.shape, dtype=bool)
    for i in range(1, max_iter + 1):
        z[mask] = z[mask] ** 2 + (julia_c if julia_c is not None else grid[mask])
        escaped = mask & (np.abs(z) > 2.0)
        safe = np.clip(np.abs(z[escaped]), 1.0001, None)
        iteration[escaped] = i - np.log2(np.log2(safe))
        mask[escaped] = False
    iteration[mask] = max_iter
    return iteration


def _mandelbrot():
    return _escape(_grid(-2.5, 1.0, -1.25, 1.25))


def _julia(c):
    return _escape(_grid(-1.8, 1.8, -1.8, 1.8), julia_c=c)


def _burning_ship():
    g = _grid(-2.5, 1.5, -2.0, 0.8)
    z = np.zeros_like(g)
    iteration = np.zeros(g.shape, dtype=np.float32)
    mask = np.ones(g.shape, dtype=bool)
    for i in range(1, MAX_ITER + 1):
        zr = np.abs(z[mask].real) + 1j * np.abs(z[mask].imag)
        z[mask] = zr ** 2 + g[mask]
        escaped = mask & (np.abs(z) > 2.0)
        iteration[escaped] = i
        mask[escaped] = False
    iteration[mask] = MAX_ITER
    return iteration


def _sierpinski(n=200_000):
    V = np.array([[0., 0.], [1., 0.], [.5, 3 ** .5 / 2]])
    pts = np.zeros((n, 2))
    p = np.array([.5, .3])
    for i in range(n):
        p = (p + V[np.random.randint(3)]) / 2
        pts[i] = p
    return pts[:, 0], pts[:, 1]


# ── precompute ────────────────────────────────────────────────────────────────

def _precompute():
    print("⏳  [1/4] Mandelbrot …")
    mb = _mandelbrot()

    print(f"⏳  [2/4] {N_FRAMES} Julia frames …")
    thetas = np.linspace(0, 2 * np.pi, N_FRAMES, endpoint=False)
    julia_frames = [_julia(0.7885 * np.exp(1j * t)) for t in thetas]

    print("⏳  [3/4] Burning Ship …")
    bs = _burning_ship()

    print("⏳  [4/4] Sierpiński points …")
    sx, sy = _sierpinski()

    print("✅  Precompute done.\n")
    return mb, julia_frames, bs, sx, sy


# ── animation ─────────────────────────────────────────────────────────────────

def animate():
    mb, julia_frames, bs, sx, sy = _precompute()

    DARK = "#0a0a0a"
    fig = plt.figure(figsize=(14, 14), facecolor=DARK)
    fig.suptitle("✦  Beautiful Fractals  ✦", fontsize=24, color="white",
                 fontweight="bold", y=0.975)
    gs = GridSpec(2, 2, fig, hspace=0.08, wspace=0.05)

    ax_mb, ax_ju, ax_bs, ax_si = [fig.add_subplot(gs[r, c])
                                   for r in range(2) for c in range(2)]
    for ax in (ax_mb, ax_ju, ax_bs, ax_si):
        ax.axis("off")
        ax.set_facecolor(DARK)

    # ── Mandelbrot: twilight is cyclic → colour-wave wraps seamlessly ──
    mb_max = float(mb.max())
    im_mb = ax_mb.imshow(mb, cmap="twilight", origin="lower",
                         vmin=0, vmax=mb_max, animated=True)
    ax_mb.set_title("Mandelbrot Set", color="white", fontsize=12, pad=6)

    # ── Julia: twilight_shifted + PowerNorm, title updates each frame ──
    j_max = float(max(f.max() for f in julia_frames))
    im_ju = ax_ju.imshow(julia_frames[0], cmap="twilight_shifted", origin="lower",
                         norm=mcolors.PowerNorm(gamma=0.45, vmin=0, vmax=j_max),
                         animated=True)
    ttl_ju = ax_ju.set_title("Julia Set  θ = 0°", color="white", fontsize=12, pad=6)

    # ── Burning Ship: hsv is cyclic → psychedelic colour wave ──
    bs_max = float(bs.max())
    im_bs = ax_bs.imshow(bs, cmap="hsv", origin="lower",
                         vmin=0, vmax=bs_max, animated=True)
    ax_bs.set_title("Burning Ship Fractal", color="white", fontsize=12, pad=6)

    # ── Sierpiński: progressive reveal ──
    chunk = max(1, len(sx) // N_FRAMES)
    sc = ax_si.scatter(sx[:chunk], sy[:chunk], s=0.1,
                       c=sy[:chunk], cmap="plasma",
                       vmin=sy.min(), vmax=sy.max(), linewidths=0)
    ttl_si = ax_si.set_title(f"Sierpiński  {chunk:,} pts",
                             color="white", fontsize=12, pad=6)
    ax_si.set_xlim(-0.05, 1.05)
    ax_si.set_ylim(-0.05, 0.92)

    # ── per-frame update ──────────────────────────────────────────────────────
    def update(frame):
        shift = frame / N_FRAMES

        # Mandelbrot — shift iteration values mod max with cyclic cmap
        im_mb.set_data((mb + shift * mb_max) % mb_max)

        # Julia — swap precomputed frame
        im_ju.set_data(julia_frames[frame])
        ttl_ju.set_text(f"Julia Set  θ = {frame * 360 / N_FRAMES:.0f}°")

        # Burning Ship — same colour-wave trick
        im_bs.set_data((bs + shift * bs_max) % bs_max)

        # Sierpiński — reveal more points
        n = min((frame + 1) * chunk, len(sx))
        sc.set_offsets(np.c_[sx[:n], sy[:n]])
        sc.set_array(sy[:n])
        ttl_si.set_text(f"Sierpiński  {n:,} pts")

        return im_mb, im_ju, im_bs, sc, ttl_ju, ttl_si

    anim = FuncAnimation(fig, update, frames=N_FRAMES,
                         interval=1000 / FPS, blit=False)

    gif = "fractals_animation.gif"
    print(f"💾  Saving  {gif}  ({N_FRAMES} frames @ {FPS} fps) …")
    anim.save(gif, writer=PillowWriter(fps=FPS), dpi=90)
    print(f"✅  Saved → {gif}")
    plt.show()


if __name__ == "__main__":
    animate()
