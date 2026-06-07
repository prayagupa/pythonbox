import matplotlib
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _probe  # noqa: F401
        break
    except Exception:
        continue

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path

years = [2010, 2011, 2012, 2014, 2016, 2017, 2018, 2025, 2026]
earnings = [0, 60, 2400, 4800, 85000, 120000, 130000, 220000, 235000]

FRAMES_PER_SEGMENT = 40
FPS = 24
OUT_PATH = Path(__file__).parent / "career_earnings.gif"

# Precompute a smooth path between anchor points.
interp_x: list[float] = []
interp_y: list[float] = []
for i in range(len(years) - 1):
    x0, x1 = years[i], years[i + 1]
    y0, y1 = earnings[i], earnings[i + 1]
    for t in np.linspace(0.0, 1.0, FRAMES_PER_SEGMENT, endpoint=False):
        interp_x.append(x0 + t * (x1 - x0))
        interp_y.append(y0 + t * (y1 - y0))
interp_x.append(float(years[-1]))
interp_y.append(float(earnings[-1]))

NFR = len(interp_x)
ANCHOR_FRAMES = [i * FRAMES_PER_SEGMENT for i in range(len(years))]

fig, ax = plt.subplots(figsize=(10, 6))

ax.set_title("Earnings Journey")
ax.set_xlabel("Year")
ax.set_ylabel("Annual Earnings ($)")
ax.grid(True)

line, = ax.plot([], [], linewidth=2.5)
highlight, = ax.plot([], [], "o", markersize=10, zorder=5)
anchor_labels = [
    ax.annotate(
        f"${e:,.0f}",
        (y, e),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center",
        fontsize=9,
    )
    for y, e in zip(years, earnings)
]
for lbl in anchor_labels:
    lbl.set_visible(False)

ax.set_xlim(min(years) - 1, max(years) + 1)
ax.set_ylim(0, max(earnings) * 1.1)
ax.set_xticks(years)


def init():
    line.set_data([], [])
    highlight.set_data([], [])
    for lbl in anchor_labels:
        lbl.set_visible(False)
    return (line, highlight, *anchor_labels)


def update(frame: int):
    x = interp_x[: frame + 1]
    y = interp_y[: frame + 1]

    line.set_data(x, y)

    if frame > 0:
        highlight.set_data([x[-1]], [y[-1]])
        highlight.set_visible(True)
    else:
        highlight.set_visible(False)

    for i, anchor_frame in enumerate(ANCHOR_FRAMES):
        anchor_labels[i].set_visible(frame >= anchor_frame)

    return (line, highlight, *anchor_labels)


ani = FuncAnimation(
    fig,
    update,
    frames=NFR,
    init_func=init,
    interval=1000 // FPS,
    blit=False,
    repeat=True,
)

print(f"Rendering {NFR} frames to GIF …")
ani.save(str(OUT_PATH), writer=PillowWriter(fps=FPS))
print(f"Saved → {OUT_PATH}")
print("Displaying animation in UI window …")
plt.show()
plt.close(fig)

if __name__ == "__main__":
    pass
