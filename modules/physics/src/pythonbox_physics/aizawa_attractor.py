import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# =========================
# Aizawa system parameters
# =========================
a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1

dt = 0.01
steps = 20000  # smaller = faster + clearer

# =========================
# simulate system
# =========================
x, y, z = 0.1, 0.0, 0.0

xs = np.empty(steps)
ys = np.empty(steps)
zs = np.empty(steps)

for i in range(steps):
    dx = (z - b) * x - d * y
    dy = d * x + (z - b) * y
    dz = c + a * z - (z**3) / 3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3

    x += dx * dt
    y += dy * dt
    z += dz * dt

    xs[i] = x
    ys[i] = y
    zs[i] = z

# =========================
# keep it stable inside box
# =========================
lim = 10
xs = np.clip(xs, -lim, lim)
ys = np.clip(ys, -lim, lim)
zs = np.clip(zs, -lim, lim)

# =========================
# plot setup (simple)
# =========================
fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection='3d')

ax.set_title("Aizawa Attractor Visualization")
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_zlim(-lim, lim)

line, = ax.plot([], [], [], lw=0.8)

# =========================
# animation
# =========================
stride = 10

def update(i):
    j = i * stride
    line.set_data(xs[:j], ys[:j])
    line.set_3d_properties(zs[:j])
    return line,

ani = FuncAnimation(
    fig,
    update,
    frames=len(xs)//stride,
    interval=20,
    blit=False
)

# =========================
# SAVE GIF
# =========================
writer = PillowWriter(fps=30)
ani.save("aizawa_simple.gif", writer=writer)

print("Saved: aizawa_simple.gif")