#!/usr/bin/env python3
"""
Qualia Modality Simulation
==========================
Models the emergence of subjective sensory experience (qualia) across
five perceptual modalities — Vision, Hearing, Touch, Taste, and Smell —
as populations of coupled phase oscillators (Kuramoto model).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THE BIG IDEA:
  Each sensory modality processes the world at its own characteristic
  neural frequency band (gamma, beta, alpha, theta).  When a stimulus
  arrives, the oscillators in each modality synchronise — the stronger
  the synchrony (order parameter r → 1), the more vivid the quale.
  The animation shows phase clouds in the complex plane and the
  time-course of synchrony for each channel.

  Key concepts
  ────────────
  • Kuramoto order parameter  r(t) ∈ [0, 1]
      r ≈ 0  →  incoherent, no conscious percept
      r ≈ 1  →  fully synchronised, clear quale

  • Five modalities and their dominant EEG-inspired bands:
      Vision  ~40 Hz   (gamma)
      Hearing ~30 Hz   (high-beta / gamma)
      Touch   ~20 Hz   (beta)
      Taste   ~10 Hz   (alpha)
      Smell    ~4 Hz   (theta)

  • A brief external stimulus (white vertical band in the timeline)
    injects extra coupling energy at t = 0.20 s, driving all modalities
    toward synchrony simultaneously — modelling a multimodal percept.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run from the repo root:
    python modules/physics/src/pythonbox_physics/qualia_modality.py

Output: qualia_modality.gif saved next to this script.

Dependencies: numpy, matplotlib, pillow  (all in requirements.txt)
"""

import numpy as np
import matplotlib

# macOS / headless backend fallback (mirrors spacetime_curvature.py)
for _backend in ("MacOSX", "TkAgg", "Qt5Agg", "Agg"):
    try:
        matplotlib.use(_backend)
        import matplotlib.pyplot as _probe  # noqa: F401
        break
    except Exception:
        continue

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from pathlib import Path

# ── Colour palette ────────────────────────────────────────────────────────────
BG      = "#0a0a12"
TEXT    = "#dde8ff"

# ── Modality definitions ──────────────────────────────────────────────────────
#   omega  : centre frequency (Hz) — converted to rad/s during init
#   color  : accent colour for this modality
#   n      : number of oscillators (neurons) in the population
MODALITIES = {
    "Vision":  {"omega": 40.0, "color": "#e74c3c", "n": 80},   # gamma
    "Hearing": {"omega": 30.0, "color": "#3498db", "n": 80},   # high-beta/γ
    "Touch":   {"omega": 20.0, "color": "#2ecc71", "n": 60},   # beta
    "Taste":   {"omega": 10.0, "color": "#f39c12", "n": 50},   # alpha
    "Smell":   {"omega":  4.0, "color": "#9b59b6", "n": 50},   # theta
}

# ── Simulation parameters ─────────────────────────────────────────────────────
K_COUPLING   = 2.5    # baseline Kuramoto coupling strength
SIGMA_SPREAD = 0.25   # fractional spread of natural frequencies (Lorentzian-ish)
DT           = 0.005  # Euler time step  [s]
T_MAX        = 2.0    # total simulation duration [s]
STIMULUS_T   = 0.20   # stimulus onset time [s]
STIMULUS_DUR = 0.12   # stimulus duration [s]
STIMULUS_K   = 7.0    # additional coupling injected during stimulus
FRAMES       = 140    # animation frames
FPS          = 20     # output GIF frame rate

# ── Initialise oscillator populations ────────────────────────────────────────
rng = np.random.default_rng(42)

populations: dict = {}
for _name, _m in MODALITIES.items():
    _n     = _m["n"]
    _omega = _m["omega"] * 2.0 * np.pi          # rad/s
    populations[_name] = {
        "phases": rng.uniform(0.0, 2.0 * np.pi, _n),
        "omegas": _omega + rng.normal(0.0, SIGMA_SPREAD * _omega, _n),
        "r_hist": [],
    }

# ── Kuramoto integrator ───────────────────────────────────────────────────────
def kuramoto_step(phases: np.ndarray, omegas: np.ndarray,
                  K: float, dt: float, stim_K: float = 0.0):
    """Single Euler step of the Kuramoto model.

    Returns (new_phases, order_parameter_r).
    """
    z   = np.mean(np.exp(1j * phases))
    r   = float(np.abs(z))
    psi = float(np.angle(z))
    K_eff  = K + stim_K
    dphi   = omegas + K_eff * r * np.sin(psi - phases)
    return phases + dphi * dt, r

# ── Pre-compute all time-steps (precompute-then-render pattern) ───────────────
n_steps  = int(T_MAX / DT)
times    = np.linspace(0.0, T_MAX, n_steps)
snap_interval = max(1, n_steps // FRAMES)

phase_snaps: dict = {name: [] for name in MODALITIES}
r_snaps:     dict = {name: [] for name in MODALITIES}

print("Pre-computing oscillator dynamics …")
for _i, _t in enumerate(times):
    _in_stim = STIMULUS_T <= _t <= STIMULUS_T + STIMULUS_DUR
    _sk      = STIMULUS_K if _in_stim else 0.0
    for _name, _pop in populations.items():
        _pop["phases"], _r = kuramoto_step(
            _pop["phases"], _pop["omegas"], K_COUPLING, DT, _sk
        )
        _pop["r_hist"].append(_r)
    if _i % snap_interval == 0:
        for _name, _pop in populations.items():
            phase_snaps[_name].append(_pop["phases"].copy())
            r_snaps[_name].append(_pop["r_hist"][-1])

actual_frames = len(phase_snaps[list(MODALITIES.keys())[0]])
frame_times   = np.linspace(0.0, T_MAX, actual_frames)
print(f"  {actual_frames} snapshots ready.")

# ── Figure / axes layout ──────────────────────────────────────────────────────
fig = plt.figure(figsize=(15, 9), facecolor=BG)
fig.suptitle(
    "Qualia Modality Simulation  ·  Kuramoto Phase Oscillators",
    color=TEXT, fontsize=13, y=0.98, fontweight="bold",
)

gs = GridSpec(3, 6, figure=fig,
              hspace=0.55, wspace=0.45,
              left=0.05, right=0.97, top=0.93, bottom=0.09)

# ── Phase-plane axes (top two rows, 3 columns × 2 grid units each) ───────────
modality_names = list(MODALITIES.keys())
ax_phase: dict = {}
_theta_ref = np.linspace(0.0, 2.0 * np.pi, 300)

for _i, _name in enumerate(modality_names):
    _row, _col = divmod(_i, 3)
    _ax = fig.add_subplot(gs[_row, _col * 2: _col * 2 + 2])
    _ax.set_facecolor("#111120")
    _ax.set_xlim(-1.4, 1.4)
    _ax.set_ylim(-1.4, 1.4)
    _ax.set_aspect("equal")
    _ax.set_title(
        f"{_name}  ({MODALITIES[_name]['omega']:.0f} Hz)",
        color=MODALITIES[_name]["color"], fontsize=9, pad=4,
    )
    _ax.tick_params(colors="#666688", labelsize=6)
    for _sp in _ax.spines.values():
        _sp.set_edgecolor("#333355")
    # unit circle guide
    _ax.plot(np.cos(_theta_ref), np.sin(_theta_ref),
             color="#222244", lw=0.8, zorder=1)
    # r = 0.5 guide
    _ax.plot(0.5 * np.cos(_theta_ref), 0.5 * np.sin(_theta_ref),
             color="#1a1a33", lw=0.6, zorder=1)
    _ax.axhline(0, color="#1a1a33", lw=0.5)
    _ax.axvline(0, color="#1a1a33", lw=0.5)
    ax_phase[_name] = _ax

# ── Synchrony timeline axis (bottom row, full width) ─────────────────────────
ax_time = fig.add_subplot(gs[2, :])
ax_time.set_facecolor("#111120")
ax_time.set_xlim(0.0, T_MAX)
ax_time.set_ylim(-0.05, 1.08)
ax_time.set_xlabel("Time  (s)", color=TEXT, fontsize=9)
ax_time.set_ylabel("Synchrony  r(t)", color=TEXT, fontsize=9)
ax_time.tick_params(colors="#666688", labelsize=8)
for _sp in ax_time.spines.values():
    _sp.set_edgecolor("#333355")
# stimulus window shading
ax_time.axvspan(STIMULUS_T, STIMULUS_T + STIMULUS_DUR,
                color="white", alpha=0.06, label="Stimulus window")
# r = 1 reference
ax_time.axhline(1.0, color="#333355", lw=0.8, ls="--")

# ── Artist initialisation ─────────────────────────────────────────────────────
scatter_arts: dict = {}
mean_arrow:   dict = {}   # will be replaced each frame (re-draw trick)
r_line_arts:  dict = {}
time_marker = ax_time.axvline(0.0, color=TEXT, lw=1.0, alpha=0.55)

for _name, _m in MODALITIES.items():
    _ax    = ax_phase[_name]
    _color = _m["color"]
    _n     = _m["n"]

    scatter_arts[_name] = _ax.scatter(
        np.zeros(_n), np.zeros(_n),
        s=14, c=_color, alpha=0.45, linewidths=0, zorder=3,
    )
    # placeholder arrow (zero length)
    mean_arrow[_name] = _ax.annotate(
        "", xy=(0.0, 0.0), xytext=(0.0, 0.0),
        arrowprops=dict(arrowstyle="->", color="white", lw=1.8),
        zorder=5,
    )
    r_line_arts[_name], = ax_time.plot(
        [], [], color=_color, lw=1.8, label=_name, alpha=0.90,
    )

# legend — drawn after all lines registered
ax_time.legend(
    fontsize=8, labelcolor=TEXT,
    facecolor="#15151f", edgecolor="#444466",
    loc="upper left", ncol=3,
)

# ── Annotation: r label inside each phase plot ───────────────────────────────
r_text_arts: dict = {}
for _name in modality_names:
    r_text_arts[_name] = ax_phase[_name].text(
        -1.30, 1.20, "r = 0.00",
        color="white", fontsize=7, va="top", zorder=6,
    )

# ── Update function ───────────────────────────────────────────────────────────
def update(frame: int):
    artists_out = []

    _t = frame_times[frame]
    time_marker.set_xdata([_t])
    artists_out.append(time_marker)

    for _name in modality_names:
        _phases = phase_snaps[_name][frame]
        _xs = np.cos(_phases)
        _ys = np.sin(_phases)

        # oscillator cloud
        scatter_arts[_name].set_offsets(np.c_[_xs, _ys])
        artists_out.append(scatter_arts[_name])

        # mean-field arrow (remove & redraw — FuncAnimation blit=False is fine)
        mean_arrow[_name].remove()
        _z   = np.mean(np.exp(1j * _phases))
        _r   = float(np.abs(_z))
        _psi = float(np.angle(_z))
        mean_arrow[_name] = ax_phase[_name].annotate(
            "",
            xy=(_r * np.cos(_psi), _r * np.sin(_psi)),
            xytext=(0.0, 0.0),
            arrowprops=dict(arrowstyle="->", color="white", lw=2.0),
            zorder=5,
        )
        artists_out.append(mean_arrow[_name])

        # r(t) label
        r_text_arts[_name].set_text(f"r = {_r:.2f}")
        artists_out.append(r_text_arts[_name])

        # timeline curve
        r_line_arts[_name].set_data(
            frame_times[:frame + 1],
            r_snaps[_name][:frame + 1],
        )
        artists_out.append(r_line_arts[_name])

    return artists_out

# ── Render & save ─────────────────────────────────────────────────────────────
anim = animation.FuncAnimation(
    fig, update, frames=actual_frames,
    interval=1000 // FPS, blit=False,
)

out_path = Path(__file__).parent / "qualia_modality.gif"
print(f"Rendering {actual_frames} frames to GIF …")
anim.save(str(out_path), writer=animation.PillowWriter(fps=FPS))
print(f"Saved → {out_path}")
print("Displaying animation in UI window …")
plt.show()
plt.close(fig)

if __name__ == "__main__":
    pass  # all work done at module level to match repo convention

