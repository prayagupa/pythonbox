import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# -----------------------
# PARAMETERS
# -----------------------
W0 = 100
r = 0.07        # market return
c = 0.03        # impatience cost (fees + bad timing)

T = 80          # time horizon

t = np.arange(T)

# -----------------------
# WEALTH FUNCTIONS
# -----------------------
Wp = W0 * (1 + r) ** t
Wi = W0 * (1 + r - c) ** t
Transfer = Wp - Wi

# -----------------------
# PLOT SETUP
# -----------------------
fig, ax = plt.subplots(figsize=(8, 5))

ax.set_xlim(0, T)
ax.set_ylim(0, max(Wp) * 1.1)

ax.set_xlabel("Time")
ax.set_ylabel("Wealth")

ax.set_title("Impatience → Patience (Buffett Dynamics)")

ax.grid(True, alpha=0.3)

line_p, = ax.plot([], [], lw=2, label="Patient (Compounding)", color="green")
line_i, = ax.plot([], [], lw=2, label="Impatient (Churn)", color="red")
gap_line, = ax.plot([], [], lw=1.5, linestyle="--", label="Transfer Gap", color="orange")

ax.legend()

# -----------------------
# ANIMATION
# -----------------------
def update(i):
    x = t[:i]

    line_p.set_data(x, Wp[:i])
    line_i.set_data(x, Wi[:i])
    gap_line.set_data(x, Transfer[:i])

    return line_p, line_i, gap_line

ani = FuncAnimation(
    fig,
    update,
    frames=len(t),
    interval=50,
    blit=False
)

ani.save("impatient_patient_transfer.gif", writer=PillowWriter(fps=20))

plt.show()
