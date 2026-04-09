# 06 — Fractals & the Julia Set

> **Source file:** `src/main/python/math/fractal.py`  
> **Renders:** Mandelbrot Set · Julia Set · Burning Ship · Sierpiński Triangle

---

## Table of Contents

1. [What Is a Fractal?](#1-what-is-a-fractal)
2. [Complex Number Primer](#2-complex-number-primer)
3. [The Iteration Formula](#3-the-iteration-formula)
4. [The Filled Julia Set & Its Boundary](#4-the-filled-julia-set--its-boundary)
5. [The Mandelbrot Set — A Map of All Julia Sets](#5-the-mandelbrot-set--a-map-of-all-julia-sets)
6. [Smooth (Continuous) Colouring](#6-smooth-continuous-colouring)
7. [Morphing Animation — Rotating c on the Circle](#7-morphing-animation--rotating-c-on-the-circle)
8. [Implementation Notes](#8-implementation-notes)
9. [Further Reading](#9-further-reading)

---

## 1. What Is a Fractal?

A **fractal** is a set that exhibits *self-similarity at every scale*: zooming in reveals structure identical (or statistically similar) to the whole.  
Formally, many fractals are characterised by a **Hausdorff dimension** $d_H$ that is *non-integer*:

$$
d_H = \lim_{\varepsilon \to 0} \frac{\log N(\varepsilon)}{\log(1/\varepsilon)}
$$

where $N(\varepsilon)$ is the minimum number of boxes of side $\varepsilon$ needed to cover the set.

| Fractal | $d_H$ |
|---------|-------|
| Sierpiński Triangle | $\approx 1.585$ |
| Mandelbrot boundary | $= 2$ (Brooks–Matelski, Shishikura 1998) |
| Julia set (typical) | $1 < d_H < 2$ |
| Koch snowflake curve | $\approx 1.262$ |

---

## 2. Complex Number Primer

All escape-time fractals live in the **complex plane** $\mathbb{C}$.  
A complex number $z$ is written:

$$
z = x + iy, \qquad x,y \in \mathbb{R},\quad i^2 = -1
$$

Key operations used in the iteration:

| Operation | Formula |
|-----------|---------|
| Modulus | $|z| = \sqrt{x^2 + y^2}$ |
| Squaring | $z^2 = (x^2 - y^2) + i(2xy)$ |
| Argument | $\arg(z) = \operatorname{atan2}(y,\, x)$ |
| Polar form | $z = r\,e^{i\theta} = r(\cos\theta + i\sin\theta)$ |
| Conjugate | $\bar{z} = x - iy$ |

---

## 3. The Iteration Formula

Both the Mandelbrot and Julia sets are defined by the same **quadratic map**:

$$
\boxed{z_{n+1} = z_n^2 + c}
$$

The difference is *which* of $z_0$ or $c$ is held fixed:

| Set | Fixed parameter | Varies over |
|-----|----------------|-------------|
| **Mandelbrot** | $z_0 = 0$ | $c \in \mathbb{C}$ (the grid) |
| **Julia** ($J_c$) | $c$ (chosen constant) | $z_0 \in \mathbb{C}$ (the grid) |

### Escape condition

For $|z_0| \le 2$ and $|c| \le 2$, if there exists some $n$ such that:

$$
|z_n| > 2
$$

then the orbit $\{z_n\}$ **escapes to infinity** — the starting point is *outside* the set.  
The **radius-2 bailout** is exact: once $|z_n| > 2$ it can be proved the sequence diverges.

### Orbit taxonomy

```
z₀ → z₁ → z₂ → … → ∞          (escaping orbit  — outside the set)
z₀ → z₁ → z₂ → …  bounded      (trapped orbit   — inside the set)
z₀ on ∂J_c                      (chaotic orbit   — the fractal boundary)
```

---

## 4. The Filled Julia Set & Its Boundary

**Definition.**  For a fixed $c \in \mathbb{C}$, the *filled* Julia set $K_c$ is:

$$
K_c = \bigl\{\, z_0 \in \mathbb{C} \;\bigm|\; \sup_{n \ge 0}|z_n| < \infty \,\bigr\}
$$

The **Julia set** $J_c$ is the *boundary* of $K_c$:

$$
J_c = \partial K_c
$$

### Connectivity theorem (Fatou–Julia, ~1918)

$$
c \in \mathcal{M} \;\Longleftrightarrow\; K_c \text{ is connected}
$$
$$
c \notin \mathcal{M} \;\Longleftrightarrow\; K_c \text{ is a Cantor dust (totally disconnected)}
$$

where $\mathcal{M}$ is the Mandelbrot set.  This is why the Mandelbrot set is sometimes called the *"index of all Julia sets"*.

### Fixed points

The map $f_c(z) = z^2 + c$ has two fixed points satisfying $z^* = z^{*2} + c$:

$$
z^* = \frac{1 \pm \sqrt{1 - 4c}}{2}
$$

Their stability (attracting / repelling / parabolic) dictates the large-scale topology of $J_c$.

---

## 5. The Mandelbrot Set — A Map of All Julia Sets

The **Mandelbrot set** $\mathcal{M}$ is:

$$
\mathcal{M} = \bigl\{\, c \in \mathbb{C} \;\bigm|\; \lim_{n\to\infty} |z_n| \not\to \infty,\; z_0 = 0 \,\bigr\}
$$

It acts as a *parameter space*: each point $c \in \mathbb{C}$ corresponds to a unique Julia set $J_c$.

```
         c ∈ interior of 𝓜  →  J_c is a Jordan curve  (smooth, connected)
         c ∈ boundary of 𝓜  →  J_c is a fractal curve  (infinitely detailed)
         c ∉ 𝓜              →  J_c is Cantor dust       (totally disconnected)
```

The main cardioid of $\mathcal{M}$ satisfies:

$$
|c| \le \frac{1}{4}, \quad \text{approximately}
$$

More precisely, a point $c$ is in the main cardioid if and only if:

$$
c = \frac{\mu}{2} - \frac{\mu^2}{4}, \quad |\mu| < 1, \quad \mu \in \mathbb{C}
$$

---

## 6. Smooth (Continuous) Colouring

The naive algorithm assigns integer escape-counts, creating **banding** artefacts.  
**Smooth colouring** (also called the *normalised iteration count* or *Milnor–Hubbard potential*) produces a continuous value:

$$
\nu(z_N) = N - \log_2 \!\left(\log_2 |z_N|\right)
$$

where $N$ is the first iteration at which $|z_N| > 2$.

**Derivation sketch.**  The Green's function of $K_c$ (the Böttcher coordinate) near infinity is:

$$
G_c(z) = \log|z| + \sum_{n=1}^{\infty} \frac{1}{2^n} \log\!\left|1 + \frac{c}{z_n^2}\right|
$$

For large $|z|$ this simplifies to $G_c(z) \approx \log|z|$, and the escape potential at step $N$ is:

$$
G_c(z_0) \approx \frac{\log|z_N|}{2^N}
$$

Taking $\log_2$ of both sides and rearranging:

$$
\nu = N - \log_2(\log_2|z_N|)
$$

This is exactly what the code computes:

```python
# fractal.py — _escape()
safe = np.clip(np.abs(z[escaped]), 1.0001, None)
iteration[escaped] = i - np.log2(np.log2(safe))
```

The clamp to `1.0001` prevents `log(log(|z|))` from becoming negative or undefined when $|z|$ is barely above 1.

---

## 7. Morphing Animation — Rotating *c* on the Circle

The animation in `fractal.py` continuously varies $c$ along the circle of radius $r = 0.7885$:

$$
c(\theta) = 0.7885\, e^{i\theta} = 0.7885\,(\cos\theta + i\sin\theta), \qquad \theta \in [0,\, 2\pi)
$$

```python
thetas = np.linspace(0, 2 * np.pi, N_FRAMES, endpoint=False)
julia_frames = [_julia(0.7885 * np.exp(1j * t)) for t in thetas]
```

### Why $r = 0.7885$?

The radius is chosen so the orbit of 0 under $f_c$ stays **near the boundary** of $\mathcal{M}$, producing the most visually complex Julia sets:

- $r \ll 0.25$: $c$ is deep inside $\mathcal{M}$ → $J_c$ is a smooth Jordan curve (boring circle-like)
- $r \approx 0.7885$: $c$ grazes the boundary of $\mathcal{M}$ → $J_c$ morphs between connected and nearly-Cantor (maximally dramatic)
- $r > 2$: $c$ is outside $\mathcal{M}$ → $J_c$ is Cantor dust (disconnected points)

The animation sweeps through representative angles, so the viewer sees Julia sets transform from **dendrite** forms to **dragon-like** shapes and back, completing one full revolution:

$$
\theta \in \{0°,\; 5°,\; 10°,\; \ldots,\; 355°\}  \quad (72 \text{ frames})
$$

---

## 8. Implementation Notes

### Vectorised escape loop

The inner loop operates on a boolean *alive mask* rather than iterating pixel-by-pixel, keeping all computation in NumPy:

```python
# Each iteration only touches un-escaped pixels
z[mask] = z[mask] ** 2 + (julia_c if julia_c is not None else grid[mask])
escaped  = mask & (np.abs(z) > 2.0)
mask[escaped] = False          # kill escaped pixels — never touch again
```

**Complexity:** $O(W \times H \times N_{\text{iter}})$ in the worst case, but pixels escape early so the effective inner loop shrinks each iteration.

### Memory layout

| Array | dtype | Size (RES=500) |
|-------|-------|----------------|
| `grid` | `complex64` | 500×500 × 8 B ≈ 2 MB |
| `iteration` | `float32` | 500×500 × 4 B ≈ 1 MB |
| `mask` | `bool` | 500×500 × 1 B ≈ 0.25 MB |

### Precomputation strategy

All $N_{\text{frames}} = 72$ Julia arrays are computed **once** before the animation loop starts.  
Total Julia memory: $72 \times 1\,\text{MB} \approx 72\,\text{MB}$ — comfortably fits in RAM.

### Colour cycling

For the Mandelbrot and Burning Ship panels, a colour wave is synthesised without recomputing by *shifting* the iteration values modulo the maximum:

$$
\tilde{v}_{ij}^{(t)} = \bigl(v_{ij} + t \cdot v_{\max}\bigr) \bmod v_{\max}
$$

Paired with a **cyclic** colormap (`twilight`, `hsv`), this produces a seamless flowing wave at zero recomputation cost.

---

## 9. Further Reading

| Resource | Notes |
|----------|-------|
| Mandelbrot, B. (1982). *The Fractal Geometry of Nature* | Foundational text |
| Milnor, J. (2006). *Dynamics in One Complex Variable* | Rigorous treatment of $f_c$, Julia/Fatou theory |
| Douady & Hubbard (1982). *Itération des polynômes quadratiques complexes* | Proof of Mandelbrot connectivity |
| Shishikura, M. (1998). *The Hausdorff dimension of the boundary of the Mandelbrot set* | $d_H(\partial\mathcal{M}) = 2$ |
| [math.bu.edu/DYSYS](https://math.bu.edu/DYSYS/) | Interactive applets, lecture notes |
| Wikipedia — *Julia set* | Good entry-level summary with diagrams |

