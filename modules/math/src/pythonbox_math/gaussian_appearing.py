"""
gaussian_appearing.py

Create a smooth "appearing" animation of a Gaussian (normal) distribution.
The curve is progressively drawn from left-to-right while its alpha ramps
from 0 -> 1 so it looks like the bell curve is appearing.

Usage: run the script to open an interactive window and (optionally) save a GIF.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Parameters
MU = 0.0
SIGMA = 1.0
N_POINTS = 400
FRAMES = 120
FPS = 30
GIF_FILENAME = "gaussian_linga.gif"

# Visual theme
GRAPH_COLOR = "#0b0b0b"         # very dark black for the curve
BACKROUND_RED = "#8B0000"       # dark red background (DeepRed)
BACKGROUND_COLOR = BACKROUND_RED
# labels/ticks are removed, but keep a contrasting title color
TITLE_COLOR = "white"
GRID_COLOR = None


def gaussian(x: np.ndarray, mu: float = 0.0, sigma: float = 1.0) -> np.ndarray:
    """Return Gaussian PDF values for x.
    Not using scipy so this remains dependency-free.
    """
    norm = 1.0 / (sigma * np.sqrt(2 * np.pi))
    return norm * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


# Build data
x = np.linspace(MU - 4 * SIGMA, MU + 4 * SIGMA, N_POINTS)
y = gaussian(x, MU, SIGMA)

# Figure & axis
fig, ax = plt.subplots(figsize=(7, 4.5))
# set figure and axis background to black
fig.patch.set_facecolor(BACKGROUND_COLOR)
ax.set_facecolor(BACKGROUND_COLOR)
line, = ax.plot([], [], lw=3, color=GRAPH_COLOR)
fill = None  # will hold the fill_between PolyCollection
ax.set_xlim(x.min(), x.max())
ax.set_ylim(0, y.max() * 1.15)
ax.set_title("", color=TITLE_COLOR)
ax.set_xticks([])
ax.set_yticks([])
ax.grid(False)
for spine in ax.spines.values():
    spine.set_visible(False)

# Precompute alpha ramp and progressive indices, to control the "appearing" effect
alpha_ramp = np.linspace(0.0, 1.0, FRAMES)
# For drawing left-to-right we compute the index at each frame
indices = (np.linspace(1, N_POINTS, FRAMES)).astype(int)


def init():
    """Initialize the animation artists."""
    line.set_data([], [])
    return (line,)


def update(frame: int):
    """Update called once per frame by FuncAnimation.

    We progressively reveal the curve up to indices[frame] and set the alpha
    according to alpha_ramp so it fades in smoothly.
    """
    global fill

    n = indices[frame]
    current_x = x[:n]
    current_y = y[:n]

    # Update line data
    line.set_data(current_x, current_y)
    line.set_alpha(alpha_ramp[frame])

    # Update filled area under the curve: remove old and draw new so it follows the line
    if fill is not None:
        # fill is a PolyCollection (FillBetweenPolyCollection); remove it directly
        try:
            fill.remove()
        except Exception:
            # if removal fails for any reason, ignore and continue
            pass
    # Slightly stronger fill alpha to be visible on black background
    fill = ax.fill_between(current_x, current_y, color=GRAPH_COLOR, alpha=alpha_ramp[frame] * 0.35)

    # Return the artists that were modified. Returning the fill helps some backends.
    return (line, fill)


def build_and_save():
    """Construct the animation and save it as a GIF using PillowWriter."""
    anim = FuncAnimation(fig, update, frames=FRAMES, init_func=init, blit=False)
    print("Saving GIF to", GIF_FILENAME)
    writer = PillowWriter(fps=FPS)
    anim.save(GIF_FILENAME, writer=writer)
    print("Saved GIF.")


if __name__ == "__main__":
    # Show the animation interactively. The user can close the window to continue and save.
    anim = FuncAnimation(fig, update, frames=FRAMES, init_func=init, blit=False)
    plt.show()

    # After closing the interactive window we optionally save the gif. Keep this step
    # non-mandatory: uncomment the next line to automatically save on exit.
    try:
        build_and_save()
    except Exception as exc:  # pragma: no cover - friendly fallback
        print("Could not save GIF:", exc)
