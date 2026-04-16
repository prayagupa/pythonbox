"""Animate a family of quartic implicit curves and save as a GIF.

This script draws the zero-contour of the quartic implicit function

    F(x,y) = (x^2 + y^2)**2 - A*(x^2 - y^2) - R**4

where the parameter `A` is animated over time to morph the shape.

Run as a script. Produces `quartic_implicit.gif` next to this file.
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def F(X: np.ndarray, Y: np.ndarray, A: float, R: float = 1.0) -> np.ndarray:
    """Quartic implicit function returning values on a grid.

    F(x,y) = (x^2 + y^2)^2 - A*(x^2 - y^2) - R^4
    The zero level set F==0 is a quartic curve.
    """
    return (X ** 2 + Y ** 2) ** 2 - A * (X ** 2 - Y ** 2) - R ** 4


def make_animation(outpath: str, frames: int = 60, dpi: int = 100) -> None:
    # grid
    lim = 1.8
    n = 400
    x = np.linspace(-lim, lim, n)
    y = np.linspace(-lim, lim, n)
    X, Y = np.meshgrid(x, y)

    # colors
    background_color = '#2b0000'  # dark red
    graph_color = '#ff4500'  # orange-red for better visibility

    fig = plt.figure(figsize=(6, 6), dpi=dpi, facecolor=background_color)
    fig.patch.set_facecolor(background_color)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(background_color)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    # z will be the parameter A
    azim_min, azim_max = 0, 360
    ax.set_zlim(-2.6, 2.6)
    ax.set_box_aspect((1, 1, 0.8))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # Remove the background box for x, y, z axis planes
    ax.grid(False)  # Disable grid lines
    ax.xaxis.pane.set_visible(False)  # Remove x-axis plane
    ax.yaxis.pane.set_visible(False)  # Remove y-axis plane
    ax.zaxis.pane.set_visible(False)  # Remove z-axis plane

    A0 = 0.0
    R = 1.0

    violet = graph_color

    def plot_contour_at_A(A: float, alpha: float = 1.0, linewidth: float = 1.2):
        # compute 2D contour on a temporary axis to extract paths
        Z = F(X, Y, A, R=R)
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)
        cs = ax2.contour(X, Y, Z, levels=[0])
        # use allsegs to extract raw segment arrays (works across mpl versions)
        for seglist in cs.allsegs:
            for seg in seglist:
                v = seg
                if v.shape[0] < 2:
                    continue
                ax.plot(v[:, 0], v[:, 1], zs=A, zdir='z', color=violet, alpha=alpha, linewidth=linewidth)
        plt.close(fig2)

    # initial draw
    plot_contour_at_A(A0)

    def animate(i: int):
        A = 2.5 * np.sin(2 * np.pi * i / frames)
        ax.cla()
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-2.6, 2.6)
        ax.set_box_aspect((1, 1, 0.8))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        # rotation for nicer 3D view
        azim = azim_min + (azim_max - azim_min) * (i / frames)
        ax.view_init(elev=25, azim=azim)
        # draw a short trail of previous slices for context
        trail = 6
        for k in range(trail):
            t = max(0, i - (trail - 1 - k))
            A_trail = 2.5 * np.sin(2 * np.pi * t / frames)
            alpha = 0.15 + 0.85 * (k + 1) / trail
            lw = 0.6 + 0.6 * (k + 1) / trail
            plot_contour_at_A(A_trail, alpha=alpha, linewidth=lw)
        # highlight current
        plot_contour_at_A(A, alpha=1.0, linewidth=1.6)
        title = f'Quartic implicit curve — A = {A:.2f}'
        ax.set_title('', pad=10, color='#ffffff')
        return []

    anim = FuncAnimation(fig, animate, frames=frames, interval=80, blit=False)

    # save
    writer = PillowWriter(fps=15)
    anim.save(outpath, writer=writer)
    plt.close(fig)


if __name__ == '__main__':
    outdir = os.path.dirname(__file__)
    outpath = os.path.join(outdir, 'quartic_implicit.gif')
    print('Rendering animation — this may take a few seconds...')
    make_animation(outpath, frames=60, dpi=120)
    print('Saved animation to', outpath)
