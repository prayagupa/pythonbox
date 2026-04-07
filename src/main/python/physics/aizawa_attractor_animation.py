import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# -----------------------
# Aizawa parameters
# -----------------------
a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
dt = 0.01
steps = 15000

# -----------------------
# simulate system
# -----------------------
x, y, z = 0.1, 0.0, 0.0

xs = []
ys = []

for _ in range(steps):
    dx = (z - b) * x - d * y
    dy = d * x + (z - b) * y
    dz = c + a * z - (z**3)/3 - (x**2 + y**2)*(1 + e*z) + f*z*x**3

    x += dx * dt
    y += dy * dt
    z += dz * dt

    # SIMPLE 2D projection (this is the key fix)
    xs.append(x)
    ys.append(y)

# -----------------------
# plot setup
# -----------------------
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_title("Aizawa Attractor (Simple Chaos View)")

ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)

line, = ax.plot([], [], lw=0.8)

# -----------------------
# animation
# -----------------------
stride = 5

def update(i):
    j = i * stride
    line.set_data(xs[:j], ys[:j])
    return line,

ani = FuncAnimation(
    fig,
    update,
    frames=len(xs)//stride,
    interval=20,
    blit=False
)

# -----------------------
# SAVE GIF (safe + simple)
# -----------------------
ani.save("aizawa_simple.gif", writer=PillowWriter(fps=30))

print("Saved: aizawa_simple.gif")

plt.show()