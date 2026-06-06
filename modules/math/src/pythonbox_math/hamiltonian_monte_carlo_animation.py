"""
Hamiltonian Monte Carlo (HMC) Animation Demo — 3D

Visualises the HMC trajectory on top of a 3D potential energy surface
U(q) = 0.5*(q1² + 4*q2²).  Leapfrog integration drives proposals;
the Metropolis criterion decides acceptance.

References:
- Neal, R. M. (2011). MCMC using Hamiltonian dynamics.
  Handbook of Markov Chain Monte Carlo.
- https://arxiv.org/abs/1206.1901
"""

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
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3D projection)
from pathlib import Path

# ── Hamiltonian mechanics ─────────────────────────────────────────────────────

def U(q: np.ndarray) -> float:
    """Potential energy: axis-aligned Gaussian bowl."""
    return 0.5 * (q[0] ** 2 + 4 * q[1] ** 2)


def grad_U(q: np.ndarray) -> np.ndarray:
    return np.array([q[0], 4 * q[1]])


def kinetic(p: np.ndarray) -> float:
    return 0.5 * float(np.sum(p ** 2))


def leapfrog(
    q: np.ndarray, p: np.ndarray, step_size: float, n_steps: int
):
    q, p = q.copy(), p.copy()
    p -= 0.5 * step_size * grad_U(q)
    for k in range(n_steps):
        q += step_size * p
        if k != n_steps - 1:
            p -= step_size * grad_U(q)
    p -= 0.5 * step_size * grad_U(q)
    return q, p


def hmc_step(q_current: np.ndarray, step_size: float, n_steps: int):
    p_current = np.random.randn(*q_current.shape)
    q_proposed, p_proposed = leapfrog(q_current, p_current, step_size, n_steps)
    current_H = U(q_current) + kinetic(p_current)
    proposed_H = U(q_proposed) + kinetic(p_proposed)
    if np.random.rand() < np.exp(current_H - proposed_H):
        return q_proposed, True
    return q_current, False


# ── Pre-compute HMC chain ─────────────────────────────────────────────────────

print("Pre-computing HMC samples …")
np.random.seed(42)
q = np.array([2.5, 2.5])
STEP_SIZE = 0.18
N_STEPS   = 18
N_SAMPLES = 40
FPS       = 3

positions: list = [q.copy()]
accepted:  list = []

for _ in range(N_SAMPLES):
    q_new, acc = hmc_step(q, STEP_SIZE, N_STEPS)
    positions.append(q_new.copy())
    accepted.append(acc)
    q = q_new

positions = np.array(positions)           # shape (N+1, 2)
z_pos     = np.array([U(p) for p in positions])

# ── Potential surface grid ────────────────────────────────────────────────────

grid     = np.linspace(-4, 4, 80)
X, Y     = np.meshgrid(grid, grid)
Z_surf   = 0.5 * (X ** 2 + 4 * Y ** 2)

# ── Figure ────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(9, 7))
ax  = fig.add_subplot(111, projection="3d")

ax.plot_surface(
    X, Y, Z_surf,
    cmap="viridis", alpha=0.40,
    linewidth=0, antialiased=True,
)

ax.set_xlabel("q₁  (position 1)")
ax.set_ylabel("q₂  (position 2)")
ax.set_zlabel("U(q)  potential energy")
ax.set_title("Hamiltonian Monte Carlo — 3D Potential Surface")
ax.view_init(elev=28, azim=-55)

OFFSET = 0.20   # lift artists above the surface so they are always visible

(trace_line,)   = ax.plot([], [], [], "w-",  lw=2,   alpha=0.85, label="Trajectory")
(particle_dot,) = ax.plot([], [], [], "ro",  ms=8,               label="Current")
(accept_dot,)   = ax.plot([], [], [], "go",  ms=11,  alpha=0.55, label="Accepted")

ax.legend(loc="upper right", fontsize=9)

# ── Animation callbacks ───────────────────────────────────────────────────────

def init():
    for artist in (trace_line, particle_dot, accept_dot):
        artist.set_data([], [])
        artist.set_3d_properties([])
    return trace_line, particle_dot, accept_dot


def animate(i: int):
    xs = positions[:i + 1, 0]
    ys = positions[:i + 1, 1]
    zs = z_pos[:i + 1] + OFFSET

    trace_line.set_data(xs, ys)
    trace_line.set_3d_properties(zs)

    particle_dot.set_data([positions[i, 0]], [positions[i, 1]])
    particle_dot.set_3d_properties([z_pos[i] + OFFSET])

    if i > 0 and accepted[i - 1]:
        accept_dot.set_data([positions[i, 0]], [positions[i, 1]])
        accept_dot.set_3d_properties([z_pos[i] + OFFSET])
    else:
        accept_dot.set_data([], [])
        accept_dot.set_3d_properties([])

    return trace_line, particle_dot, accept_dot


# ── Render & save ─────────────────────────────────────────────────────────────

n_frames = len(positions)
print(f"Rendering {n_frames} frames to GIF …")

anim = animation.FuncAnimation(
    fig, animate,
    frames=n_frames,
    init_func=init,
    interval=350,
    blit=False,       # blit must be False for 3-D axes
    repeat=False,
)

out_path = Path(__file__).parent / "hmc_animation.gif"
anim.save(str(out_path), writer=animation.PillowWriter(fps=FPS))
print(f"Saved → {out_path}")
print("Displaying animation in UI window …")
plt.show()
plt.close(fig)

if __name__ == "__main__":
    pass
