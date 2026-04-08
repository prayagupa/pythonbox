"""
vega_vomma_surface.py — Options Greeks: Vega & Vomma 3-D Surface
=================================================================
Plots two Black-Scholes surfaces side-by-side:

  • Vega   (ν)   — sensitivity of option price to implied volatility (σ)
                   ν = S · φ(d₁) · √T

  • Vomma / Volga — second derivative of option price w.r.t. σ  (dVega/dσ)
                   Vomma = ν · (d₁ · d₂) / σ

Axes:
  X — Spot price  S  ∈ [50, 150]
  Y — Volatility  σ  ∈ [0.05, 0.80]
  Z — Greek value (Vega or Vomma)

Fixed parameters (editable below):
  K = 100   (strike price)
  T = 1.0   (time to expiry, years)
  r = 0.05  (risk-free rate)

Run:  python vega_vomma_surface.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.stats import norm

# ── Parameters ────────────────────────────────────────────────────────────────
K = 100.0     # Strike price
T = 1.0       # Time to expiry (years)
r = 0.05      # Risk-free interest rate
RES = 200     # Grid resolution (higher → smoother, slower)

# ── Grid ──────────────────────────────────────────────────────────────────────
S_vals   = np.linspace(50,  150,  RES)   # Spot prices
sig_vals = np.linspace(0.05, 0.80, RES)  # Implied volatility

S, SIG = np.meshgrid(S_vals, sig_vals)

# ── Black-Scholes d1, d2 ──────────────────────────────────────────────────────
sqrt_T = np.sqrt(T)
d1 = (np.log(S / K) + (r + 0.5 * SIG ** 2) * T) / (SIG * sqrt_T)
d2 = d1 - SIG * sqrt_T

phi_d1 = norm.pdf(d1)    # Standard normal PDF at d1

# ── Greeks ────────────────────────────────────────────────────────────────────
VEGA  = S * phi_d1 * sqrt_T                       # Vega
VOMMA = VEGA * (d1 * d2) / SIG                   # Vomma (Volga)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 7))
fig.patch.set_facecolor("#0d1117")

def make_ax(pos):
    ax = fig.add_subplot(pos, projection="3d")
    ax.set_facecolor("#0d1117")
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#2a2a3e")
    ax.tick_params(colors="#c9d1d9", labelsize=8)
    ax.xaxis.label.set_color("#c9d1d9")
    ax.yaxis.label.set_color("#c9d1d9")
    ax.zaxis.label.set_color("#c9d1d9")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a3e")
    return ax

# ── Vega surface ──────────────────────────────────────────────────────────────
ax1 = make_ax(121)
surf1 = ax1.plot_surface(S, SIG, VEGA, cmap=cm.plasma,
                         linewidth=0, antialiased=True, alpha=0.92)
ax1.set_xlabel("Spot Price  S", labelpad=10)
ax1.set_ylabel("Volatility  σ", labelpad=10)
ax1.set_zlabel("Vega  ν", labelpad=10)
ax1.set_title("Vega  ν = S · φ(d₁) · √T", fontsize=13, pad=14, fontweight="bold")
cb1 = fig.colorbar(surf1, ax=ax1, shrink=0.45, pad=0.1)
cb1.ax.yaxis.set_tick_params(color="#c9d1d9")
cb1.outline.set_edgecolor("#2a2a3e")
plt.setp(cb1.ax.yaxis.get_ticklabels(), color="#c9d1d9", fontsize=7)

# ── Vomma surface ─────────────────────────────────────────────────────────────
ax2 = make_ax(122)
# Clip extreme outliers for a clean colour scale
vomma_clipped = np.clip(VOMMA, np.percentile(VOMMA, 1), np.percentile(VOMMA, 99))
surf2 = ax2.plot_surface(S, SIG, vomma_clipped, cmap=cm.viridis,
                         linewidth=0, antialiased=True, alpha=0.92)
ax2.set_xlabel("Spot Price  S", labelpad=10)
ax2.set_ylabel("Volatility  σ", labelpad=10)
ax2.set_zlabel("Vomma", labelpad=10)
ax2.set_title("Vomma = ν · (d₁ · d₂) / σ", fontsize=13, pad=14, fontweight="bold")
cb2 = fig.colorbar(surf2, ax=ax2, shrink=0.45, pad=0.1)
cb2.ax.yaxis.set_tick_params(color="#c9d1d9")
cb2.outline.set_edgecolor("#2a2a3e")
plt.setp(cb2.ax.yaxis.get_ticklabels(), color="#c9d1d9", fontsize=7)

# ── Shared annotation ─────────────────────────────────────────────────────────
params_text = (f"K={K:.0f}   T={T:.1f} yr   r={r:.0%}   "
               f"S ∈ [50, 150]   σ ∈ [0.05, 0.80]")
fig.text(0.5, 0.01, params_text, ha="center", va="bottom",
         color="#8b949e", fontsize=9)

fig.suptitle("Black-Scholes Greeks — Vega & Vomma Surfaces",
             color="white", fontsize=15, fontweight="bold", y=1.01)

plt.tight_layout()
plt.savefig("vega_vomma_surface.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved → vega_vomma_surface.png")
plt.show()

