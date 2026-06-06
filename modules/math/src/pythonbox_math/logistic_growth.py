import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# -----------------------
# Model: logistic growth
# -----------------------
r = 0.6
K = 100

dt = 0.1
steps = 200

L = 1
values = []

for _ in range(steps):
    dL = r * L * (1 - L / K)
    L += dL * dt
    values.append(L)

# -----------------------
# Setup plot (clean + modern)
# -----------------------
fig, ax = plt.subplots(figsize=(7, 5))

ax.set_xlim(0, steps)
ax.set_ylim(0, K * 1.1)

ax.set_xlabel("Time")
ax.set_ylabel("Learning Level")

ax.grid(True, alpha=0.3)

line, = ax.plot([], [], lw=2)

# optional: show current point
dot, = ax.plot([], [], 'o', markersize=6)

# -----------------------
# animation function
# -----------------------
def update(i):
    x = np.arange(i)
    y = values[:i]

    line.set_data(x, y)
    dot.set_data([i-1], [values[i-1]])

    return line, dot

# -----------------------
# animate
# -----------------------
ani = FuncAnimation(
    fig,
    update,
    frames=len(values),
    interval=30,
    blit=True
)

# -----------------------
# save GIF
# -----------------------
ani.save("learning_curve.gif", writer=PillowWriter(fps=30))

print("Saved: learning_curve.gif")

plt.show()
