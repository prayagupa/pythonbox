import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib as mpl

# Create a custom red->orange->yellow colormap
warm_cmap = mpl.colors.LinearSegmentedColormap.from_list(
    "red_orange_yellow", ["#ff2d00", "#ff7f00", "#ffd400"]
)

def radial_creature(k1, k2, amp=0.6, n=4000, phase=0.0):
    t = np.linspace(0, 2*np.pi, n)
    r = 1.0 + amp * (np.sin(k1 * t + phase) * np.cos(k2 * t * 0.5 + phase*0.7))
    x = r * np.cos(t)
    y = r * np.sin(t)
    return x, y, t

def gradient_linecollection(x, y, t, cmap, linewidth=2.0, alpha=1.0):
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, linewidth=linewidth, alpha=alpha, zorder=3)
    lc.set_array(t[:-1])
    return lc

def draw_cell(ax, k1, k2, cmap):
    phases = np.linspace(0, 2*np.pi, 6, endpoint=False)

    # Glow layers (thick, faint strokes)
    for glow_width, glow_alpha in [(14, 0.08), (9, 0.05), (5, 0.03)]:
        xg, yg, tg = radial_creature(k1, k2, amp=0.6, n=3000, phase=0.0)
        lcg = gradient_linecollection(xg, yg, tg, cmap=cmap, linewidth=glow_width, alpha=glow_alpha)
        ax.add_collection(lcg)

    # Layered colored strokes with phase offsets
    for i, ph in enumerate(phases):
        x, y, t = radial_creature(k1 + 0.5*i, k2 + 0.3*i, amp=0.45 - 0.05*i, n=3000, phase=ph)
        lc = gradient_linecollection(x, y, t, cmap=cmap, linewidth=2.4, alpha=0.98)
        ax.add_collection(lc)

    # Subtle filled band for volume
    x, y, t = radial_creature(k1+1.2, k2+0.8, amp=0.35, n=1200, phase=0.4)
    color = cmap(0.65)
    ax.fill(x, y, color=color, alpha=0.06, zorder=1)

    ax.set_aspect("equal")
    ax.axis("off")

def make_grid(save_path="algebraic_creatures_warm_prayag.png", dpi=300, cmap=warm_cmap):
    fig, axes = plt.subplots(3, 3, figsize=(9, 9), facecolor="black")
    plt.subplots_adjust(wspace=0.05, hspace=0.05)

    params = [
        (3, 5), (4, 7), (5, 9),
        (6, 11), (7, 13), (8, 15),
        (9, 17), (10, 19), (11, 21)
    ]

    for ax, (k1, k2) in zip(axes.flatten(), params):
        ax.set_facecolor("black")
        draw_cell(ax, k1, k2, cmap)

    # Signature changed to your name
    fig.text(0.98, 0.02, "Upadhyay", color="white", ha="right", va="bottom", fontsize=8, alpha=0.6)

    plt.savefig(save_path, dpi=dpi, bbox_inches="tight", pad_inches=0.02, facecolor=fig.get_facecolor())
    plt.show()

if __name__ == "__main__":
    make_grid(save_path="./algebraic_creatures_warm_upadhyay.png", dpi=300, cmap=warm_cmap)
