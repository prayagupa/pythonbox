"""
Quadratic Formula Animation — show first, then save GIF.

Run:
    python quadratic_formula_animation_show_then_save_gif.py

Dependencies:
    pip install numpy matplotlib pillow
"""

import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import animation

# -------------------------
# Config
# -------------------------
FPS = 30
DURATION_SEC = 10
FRAMES = FPS * DURATION_SEC

X_MIN, X_MAX = -10, 10
N_CURVE = 2000

GIF_FILENAME = "quadratic_formula_animation.gif"

# Warm red->orange->yellow colormap (custom)
warm_cmap = mpl.colors.LinearSegmentedColormap.from_list(
    "red_orange_yellow", ["#ff2d00", "#ff7f00", "#ffd400"]
)

# -------------------------
# Math helpers
# -------------------------
def quadratic(a, b, c, x):
    return a * x**2 + b * x + c

def compute_roots(a, b, c):
    D = b**2 - 4 * a * c
    if a == 0:
        if b == 0:
            return D, None
        return D, (-c / b,)
    if D >= 0:
        sqrtD = math.sqrt(D)
    else:
        sqrtD = math.sqrt(abs(D)) * 1j
    r1 = (-b + sqrtD) / (2 * a)
    r2 = (-b - sqrtD) / (2 * a)
    return D, (r1, r2)

# -------------------------
# Visualization helpers
# -------------------------
def make_linecollection(x, y, cmap, linewidth=2.5, alpha=1.0, zorder=3):
    pts = np.array([x, y]).T.reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    t = np.linspace(0, 1, len(x))
    lc = LineCollection(segs, cmap=cmap, linewidth=linewidth, alpha=alpha, zorder=zorder)
    lc.set_array(t[:-1])
    return lc

def glow_collections(x, y, cmap, widths=(14, 9, 5), alphas=(0.08, 0.05, 0.03)):
    return [make_linecollection(x, y, cmap, linewidth=w, alpha=a, zorder=1)
            for w, a in zip(widths, alphas)]

# -------------------------
# Time-varying coefficients
# -------------------------
def param_coeffs(t_norm):
    # a crosses sign; b and c vary to make discriminant change sign
    a = 0.8 * np.sin(2 * np.pi * t_norm)
    b = 6.0 * np.cos(2 * np.pi * t_norm * 0.7)
    c = 8.0 * np.sin(2 * np.pi * t_norm * 0.4 + 0.3)
    # avoid extremely small a for too long
    if abs(a) < 0.02:
        a = 0.02 * np.sign(np.sin(2 * np.pi * t_norm) + 1e-6)
    return a, b, c

# -------------------------
# Precompute global y-limits so axes remain fixed and everything stays visible
# -------------------------
x_vals = np.linspace(X_MIN, X_MAX, N_CURVE)
all_y_min = np.inf
all_y_max = -np.inf

for frame in range(FRAMES):
    t_norm = frame / float(FRAMES)
    a, b, c = param_coeffs(t_norm)
    y_vals = quadratic(a, b, c, x_vals)
    all_y_min = min(all_y_min, np.min(y_vals))
    all_y_max = max(all_y_max, np.max(y_vals))

# Add margin and clamp to reasonable bounds to avoid extreme autoscaling
margin = 0.12 * max(abs(all_y_min), abs(all_y_max), 1.0)
Y_MIN = max(-500, all_y_min - margin)
Y_MAX = min(500, all_y_max + margin)

# If the computed range is too small, expand to a default view
if Y_MAX - Y_MIN < 20:
    Y_MIN, Y_MAX = -50, 50

# -------------------------
# Figure setup
# -------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_facecolor("black")
ax.grid(True, color="#333333", linestyle="--", linewidth=0.5)
ax.axhline(0, color="white", linewidth=1.0, zorder=0)

# Artists
vertex_point, = ax.plot([], [], "o", color="white", markersize=6, zorder=6)
roots_real_scatter, = ax.plot([], [], "o", color="#ffd400", markersize=8, linestyle="None", zorder=7)
roots_complex_scatter, = ax.plot([], [], "o", markerfacecolor="none", markeredgecolor="#ffd400",
                                 markersize=8, linestyle="None", zorder=7)
annotation_text = ax.text(0.01, 0.98, "", transform=ax.transAxes, color="white", fontsize=10,
                          va="top", ha="left", family="monospace", zorder=10)

# Container for dynamic LineCollections so we can remove them each frame
dynamic_collections = []

# -------------------------
# Animation functions
# -------------------------
def init():
    # clear dynamic collections
    for coll in dynamic_collections:
        try:
            coll.remove()
        except Exception:
            pass
    dynamic_collections.clear()
    vertex_point.set_data([], [])
    roots_real_scatter.set_data([], [])
    roots_complex_scatter.set_data([], [])
    annotation_text.set_text("")
    return []

def update(frame):
    # remove previous dynamic collections
    for coll in dynamic_collections:
        try:
            coll.remove()
        except Exception:
            pass
    dynamic_collections.clear()

    t_norm = frame / float(FRAMES)
    a, b, c = param_coeffs(t_norm)
    y_vals = quadratic(a, b, c, x_vals)

    # glow behind
    for g in glow_collections(x_vals, y_vals, warm_cmap):
        ax.add_collection(g)
        dynamic_collections.append(g)

    # main colored curve
    main_lc = make_linecollection(x_vals, y_vals, warm_cmap, linewidth=2.8, alpha=1.0, zorder=4)
    ax.add_collection(main_lc)
    dynamic_collections.append(main_lc)

    # vertex
    if a != 0:
        x_v = -b / (2 * a)
        y_v = quadratic(a, b, c, x_v)
        vertex_point.set_data([x_v], [y_v])
    else:
        vertex_point.set_data([], [])

    # roots
    D, roots = compute_roots(a, b, c)
    if roots is None:
        roots_real_scatter.set_data([], [])
        roots_complex_scatter.set_data([], [])
        roots_text = "No roots (degenerate)"
    else:
        if len(roots) == 1:
            r = roots[0]
            roots_real_scatter.set_data([r], [0])
            roots_complex_scatter.set_data([], [])
            roots_text = f"Linear root: x = {r:.3f}"
        else:
            r1, r2 = roots
            if D >= 0:
                roots_real_scatter.set_data([r1.real, r2.real], [0, 0])
                roots_complex_scatter.set_data([], [])
                roots_text = f"Roots: x₁ = {r1:.3f}, x₂ = {r2:.3f}"
            else:
                roots_real_scatter.set_data([], [])
                roots_complex_scatter.set_data([r1.real, r2.real], [0, 0])
                roots_text = f"Complex roots: {r1:.3f}, {r2:.3f}"

    # annotation
    quad_formula = "x = (-b ± √(b² - 4ac)) / (2a)"
    if roots is None:
        substituted = "No quadratic (a=0, b=0)"
    else:
        substituted = (
            f"x = ( -({b:.3f}) ± √(({b:.3f})² - 4·{a:.3f}·{c:.3f}) ) / (2·{a:.3f})"
            if a != 0 else "Linear: x = -c / b"
        )

    D_text = f"D = {D:.4f}"
    a_text = f"a = {a:.4f}"
    b_text = f"b = {b:.4f}"
    c_text = f"c = {c:.4f}"

    annotation = (
        f"{a_text}    {b_text}    {c_text}\n"
        f"{D_text}    {('Real roots' if D > 0 else ('Repeated root' if abs(D) < 1e-6 else 'Complex roots'))}\n\n"
        f"{quad_formula}\n{substituted}\n\n{roots_text}"
    )
    annotation_text.set_text(annotation)

    # return artists for blitting compatibility (we use blit=False)
    artists = [vertex_point, roots_real_scatter, roots_complex_scatter, annotation_text]
    artists.extend(dynamic_collections)
    return artists

# -------------------------
# Create animation
# -------------------------
anim = animation.FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    init_func=init,
    interval=1000.0 / FPS,
    blit=False
)

# -------------------------
# Show first, then save GIF only
# -------------------------
def save_gif(anim_obj):
    try:
        print("Saving GIF...")
        gif_writer = animation.PillowWriter(fps=FPS)
        anim_obj.save(GIF_FILENAME, writer=gif_writer, dpi=100)
        print(f"Saved GIF to '{GIF_FILENAME}'")
    except Exception as e:
        print("GIF save failed:", e)
        print("Install pillow (pip install pillow) to enable GIF export.")

if __name__ == "__main__":
    fig.suptitle("Quadratic Formula: y = a x² + b x + c\n(Interactive preview — close window to save GIF)", color="white", fontsize=12)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    print("Playing animation. Close the animation window when you want to save the GIF.")
    plt.show()   # blocks until window is closed

    # After the interactive window is closed, save the GIF
    save_gif(anim)

    print("Done.")
