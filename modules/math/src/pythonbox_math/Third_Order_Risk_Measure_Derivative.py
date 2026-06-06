"""
Animate a third-order risk measure for a European call option.

This script computes the third derivative of the Black-Scholes call price
with respect to the underlying price (approximated with finite differences),
and animates how that third-order sensitivity changes as implied volatility
varies over time.

Saves an animated GIF beside this script named
`third_order_risk_measure.gif`.

Usage:
		python modules/math/src/pythonbox_math/Third_Order_Risk_Measure_Derivative.py

Dependencies: numpy, matplotlib, pillow (for GIF writer) or ffmpeg (for MP4).

Background — what is the third derivative?

- Definition: the third derivative of the option price with respect to the
	underlying, written d^3P/dS^3, is the derivative of the option's gamma with
	respect to the underlying price. It is sometimes called "speed" in the
	practitioner literature (naming varies).
- Relation to Greeks: delta = dP/dS, gamma = d^2P/dS^2, so
	speed = d(gamma)/dS = d^3P/dS^3. It measures how quickly curvature
	(gamma) changes as the spot moves.
- Interpretation: a positive third derivative means gamma increases as S rises;
	negative means gamma decreases. Around the strike, gamma typically peaks,
	so the third derivative changes sign near that peak. Speed matters when
	managing second-order exposure (gamma hedging), because it quantifies how
	quickly the hedge itself will become less/more effective for small moves.
- Practical notes: the third derivative is numerically fragile — finite
	differences and coarse grids amplify noise — so use fine grids or analytic
	formulas where available. In risk systems it is used for stress-testing and
	to anticipate changes in gamma-driven P&L for large moves.

"""

from __future__ import annotations

import math
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def black_scholes_call(S, K, r, q, sigma, T):
	"""Black-Scholes European call price."""
	if T <= 0 or sigma <= 0:
		return max(S - K, 0.0)
	sqrtT = math.sqrt(T)
	d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
	d2 = d1 - sigma * sqrtT
	from math import erf, sqrt

	# Normal CDF using erf
	def N(x):
		return 0.5 * (1.0 + erf(x / sqrt(2.0)))

	return S * math.exp(-q * T) * N(d1) - K * math.exp(-r * T) * N(d2)


def third_derivative_price_wrt_S(price_func, S_grid, eps=1e-3, *args, **kwargs):
	"""Approximate third derivative d^3 Price / dS^3 on S_grid using central differences.

	We compute f'''(S) using a 5-point stencil for third derivative.
	"""
	prices = np.array([price_func(S, *args, **kwargs) for S in S_grid])
	# Use numpy gradient repeatedly is noisy; prefer finite difference stencil.
	# For interior points use central differences; for boundaries fall back to np.gradient.
	n = len(S_grid)
	h = np.gradient(S_grid)
	third = np.zeros_like(prices)

	# Fallback: compute numerical derivative using np.gradient three times
	try:
		first = np.gradient(prices, S_grid)
		second = np.gradient(first, S_grid)
		third = np.gradient(second, S_grid)
	except Exception:
		third = np.zeros_like(prices)

	return third


def make_animation(out_path: Path | str):
	out_path = Path(out_path)
	# Parameters
	K = 100.0
	r = 0.01
	q = 0.0
	T = 0.5

	S_min, S_max = 40.0, 160.0
	S_grid = np.linspace(S_min, S_max, 300)

	# Volatility will oscillate between 10% and 60%
	frames = 80
	t = np.linspace(0, 2 * math.pi, frames)
	sigmas = 0.25 + 0.15 * np.sin(t)  # around 25% +/-15%

	# Precompute third derivatives for each sigma
	third_grid = np.zeros((frames, S_grid.size))
	for i, sigma in enumerate(sigmas):
		third_grid[i] = third_derivative_price_wrt_S(
			black_scholes_call, S_grid, 1e-3, K, r, q, sigma, T
		)

	# Create figure
	fig, ax = plt.subplots(figsize=(8, 5))
	# draw in green and prepare title
	line, = ax.plot([], [], lw=2, color="green")
	title = ax.set_title("")
	ax.set_xlim(S_min, S_max)
	# choose symmetric y-limits for stability
	ymax = np.max(np.abs(third_grid))
	ax.set_ylim(-1.1 * ymax, 1.1 * ymax)
	# hide x and y axes (ticks and spines)
	ax.set_xticks([])
	ax.set_yticks([])
	for spine in ax.spines.values():
		spine.set_visible(False)
	# remove axis labels since axes are hidden
	ax.set_xlabel("")
	ax.set_ylabel("")


	def init():
		line.set_data([], [])
		title.set_text("")
		return line, title


	def update(frame):
		y = third_grid[frame]
		line.set_data(S_grid, y)
		texto = f"Sigma = {sigmas[frame]:.3f}"
		title.set_text('')
		return line, title


	anim = FuncAnimation(fig, update, frames=frames, init_func=init, blit=True)

	# Try to save as GIF using Pillow, fallback to mp4 via ffmpeg
	try:
		from matplotlib.animation import PillowWriter

		print(f"Saving GIF to {out_path} (PillowWriter)")
		anim.save(out_path, writer=PillowWriter(fps=15))
	except Exception as e_gif:
		try:
			from matplotlib.animation import FFMpegWriter

			mp4_path = out_path.with_suffix(".mp4")
			print(f"PillowWriter failed: {e_gif}. Saving MP4 to {mp4_path} (FFMpegWriter)")
			writer = FFMpegWriter(fps=15)
			anim.save(mp4_path, writer=writer)
		except Exception as e_mp4:
			print("Failed to save animation:", e_gif, e_mp4)
			print("You can still display interactively with plt.show().")

	plt.close(fig)


def main():
	# Save next to this script
	script_dir = Path(__file__).resolve().parent
	out_file = script_dir / "third_order_risk_measure.gif"
	make_animation(out_file)
	print("Animation generation finished. File:", out_file)


if __name__ == "__main__":
	main()

