"""
Animated visualization of the Dirac delta function as the limit of a sequence of Gaussians.

This script animates how a normalized Gaussian function becomes increasingly narrow and tall, approaching the Dirac delta function in the limit. The animation is saved as a GIF.

References:
- https://en.wikipedia.org/wiki/Dirac_delta_function
- For educational context, see docs/06_fractals_julia_set.md for similar visualization style.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Set up the figure and axis
x_bg = '#FFA500'  # Orange
fig, ax = plt.subplots(figsize=(6, 4), facecolor=x_bg)
ax.set_facecolor(x_bg)
x = np.linspace(-2, 2, 400)

# Parameters for the animation
sigmas = np.logspace(-0.3, -2, 40)  # From wide to very narrow

line, = ax.plot([], [], lw=3, color='red')
ax.set_xlim(-2, 2)
ax.set_ylim(0, 2.5)
# Remove axis labels, title, ticks, and axes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("")
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

# Gaussian function normalized to area 1
def gaussian(x, sigma):
    return 1/(np.sqrt(2 * np.pi) * sigma) * np.exp(-x**2 / (2 * sigma**2))


def init():
    line.set_data([], [])
    return line,


def animate(i):
    sigma = sigmas[i]
    y = gaussian(x, sigma)
    line.set_data(x, y)
    return line,

ani = FuncAnimation(fig, animate, frames=len(sigmas), init_func=init, blit=True, interval=80)

# Save the animation as a GIF next to this script
import os
outfile = os.path.join(os.path.dirname(__file__), 'awareness_dd_animation.gif')
ani.save(outfile, writer=PillowWriter(fps=12))

print(f"Animation saved to {outfile}")

if __name__ == "__main__":
    plt.show()
