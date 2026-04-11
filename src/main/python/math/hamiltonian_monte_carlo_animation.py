"""
Hamiltonian Monte Carlo (HMC) Animation Demo

This script visualizes the trajectory of a particle under Hamiltonian dynamics as used in Hamiltonian Monte Carlo (HMC) sampling. The animation shows the evolution of position and momentum in a 2D potential energy landscape, with leapfrog integration and Metropolis acceptance steps.

References:
- Neal, R. M. (2011). MCMC using Hamiltonian dynamics. Handbook of Markov Chain Monte Carlo.
- https://arxiv.org/abs/1206.1901

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Potential energy function: 2D Gaussian

def U(q):
    return 0.5 * (q[0] ** 2 + 4 * q[1] ** 2)

def grad_U(q):
    return np.array([q[0], 4 * q[1]])

def kinetic(p):
    return 0.5 * np.sum(p ** 2)

def leapfrog(q, p, step_size, n_steps):
    q = q.copy()
    p = p.copy()
    p -= 0.5 * step_size * grad_U(q)
    for _ in range(n_steps):
        q += step_size * p
        if _ != n_steps - 1:
            p -= step_size * grad_U(q)
    p -= 0.5 * step_size * grad_U(q)
    return q, p

def hmc_step(q_current, step_size, n_steps):
    p_current = np.random.randn(*q_current.shape)
    q_proposed, p_proposed = leapfrog(q_current, p_current, step_size, n_steps)
    current_H = U(q_current) + kinetic(p_current)
    proposed_H = U(q_proposed) + kinetic(p_proposed)
    accept_prob = np.exp(current_H - proposed_H)
    if np.random.rand() < accept_prob:
        return q_proposed, True
    else:
        return q_current, False

# Animation setup
np.random.seed(42)
q = np.array([2.5, 2.5])
step_size = 0.18
n_steps = 18
n_samples = 40

positions = [q.copy()]
accepted = []

for _ in range(n_samples):
    q_new, acc = hmc_step(q, step_size, n_steps)
    positions.append(q_new.copy())
    accepted.append(acc)
    q = q_new
positions = np.array(positions)

# Create a grid for the potential
x = np.linspace(-4, 4, 100)
y = np.linspace(-4, 4, 100)
X, Y = np.meshgrid(x, y)
Z = U(np.array([X, Y]))

fig, ax = plt.subplots(figsize=(6, 6))
ax.contourf(X, Y, Z, levels=30, cmap="viridis", alpha=0.7)
ax.set_xlabel("q1 (position 1)")
ax.set_ylabel("q2 (position 2)")
ax.set_title("Hamiltonian Monte Carlo Trajectory Animation")

particle, = ax.plot([], [], "ro", markersize=8, label="Current Position")
trace, = ax.plot([], [], "w-", lw=2, alpha=0.8, label="Trajectory")
accept_marker, = ax.plot([], [], "go", markersize=10, alpha=0.5, label="Accepted")

ax.legend(loc="upper right")

# Animation function
def init():
    particle.set_data([], [])
    trace.set_data([], [])
    accept_marker.set_data([], [])
    return particle, trace, accept_marker

def animate(i):
    # set_data expects sequences, not scalars
    particle.set_data([positions[i][0]], [positions[i][1]])
    trace.set_data(positions[:i+1, 0], positions[:i+1, 1])
    if i > 0 and accepted[i-1]:
        accept_marker.set_data([positions[i][0]], [positions[i][1]])
    else:
        accept_marker.set_data([], [])
    return particle, trace, accept_marker

anim = FuncAnimation(fig, animate, frames=len(positions), init_func=init,
                     interval=350, blit=True, repeat=False)

# Save as GIF (optional)
try:
    anim.save("hmc_animation.gif", writer=PillowWriter(fps=3))
    print("Animation saved as hmc_animation.gif")
except Exception as e:
    print(f"Could not save GIF: {e}")

plt.show()
