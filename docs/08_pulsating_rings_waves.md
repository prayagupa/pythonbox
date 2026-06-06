# 08 — Pulsating Rings & Radiating Waves

> **Source files:**
> - `modules/physics/src/pythonbox_physics/pulsating_rings_waves.py` — full 5-scene 3-D animation
> - `modules/physics/src/pythonbox_physics/pulsating_rings_title_splash_3d.py` — Scene 0: title card
> - `modules/physics/src/pythonbox_physics/single_pulsating_source_3d.py` — Scene 1: single source
> - `modules/physics/src/pythonbox_physics/two_source_interference_3d.py` — Scene 2: two-source interference
> - `modules/physics/src/pythonbox_physics/standing_wave_rings_3d.py` — Scene 3: standing wave
> - `modules/physics/src/pythonbox_physics/ridge_wave_propagation.py` — bonus: ridge-peak tracking

> **Shows:** Circular wavefronts · Cylindrical spreading · Two-source interference · Standing waves · 3-D surface displacement

---

## Table of Contents

1. [What Is a Wave?](#1-what-is-a-wave)
2. [What the 3-D Surface Means](#2-what-the-3-d-surface-means)
3. [A Vibrating Point Source](#3-a-vibrating-point-source)
4. [The Wave Equation](#4-the-wave-equation)
5. [Why Do Ridges Fade with Distance?](#5-why-do-ridges-fade-with-distance)
6. [Wave Speed, Wavelength, and Frequency](#6-wave-speed-wavelength-and-frequency)
7. [Where Are the Crests at Any Moment?](#7-where-are-the-crests-at-any-moment)
8. [Two Sources: Interference](#8-two-sources-interference)
9. [Standing Waves: Pulsating Rings](#9-standing-waves-pulsating-rings)
10. [The Five Animations](#10-the-five-animations)
11. [How the Code Works](#11-how-the-code-works)
12. [Symbol Cheat Sheet](#12-symbol-cheat-sheet)
13. [Want to Learn More?](#13-want-to-learn-more)

---

## 1. What Is a Wave?

Drop a pebble into a still pond. You will see rings spreading outward from where it landed. Each ring is a **wave crest** — a place where the water surface is raised above its resting height. Between each pair of crests is a **trough**, where the surface dips below rest.

Now the key question: **is anything travelling across the pond, or is the water just going up and down?**

The answer is: the **pattern** travels — the *energy* travels — but the water itself mostly bobs up and down in place. The ripple you see is not water rushing outward; it is a disturbance spreading through the water.

This is the central idea behind all waves:

> **A wave is a pattern of disturbance that carries energy through a medium, without permanently transporting the medium itself.**

This applies to:

| Wave type | Medium | What oscillates |
|---|---|---|
| Water ripple | Water | Surface height |
| Sound | Air | Air pressure |
| Seismic | Ground | Rock displacement |
| Light | (no medium needed) | Electric & magnetic fields |

The visualizations in this document show **circular waves** spreading from a vibrating source — like the pond ripple, but in a controlled mathematical form you can see in 3-D.

---

## 2. What the 3-D Surface Means

In the 2-D pond picture you look down from above and see a top view of the rings. These simulations show a **3-D surface** instead:

- The **x** and **y** axes span the "pond" — the flat 2-D domain where the wave lives.
- The **z** axis (vertical, up-down) shows the **displacement** — how far above or below rest each point of the surface is right now.

| Z value | Physical meaning |
|---|---|
| z > 0, bright peak | Crest — surface is pushed up |
| z = 0, at rest level | Zero crossing — surface is momentarily flat |
| z < 0, dark valley | Trough — surface is pulled down |

The wave travels outward in the **horizontal plane**; the vertical direction is purely a readout of "how disturbed is this point right now?"

---

## 3. A Vibrating Point Source

Imagine a tiny piston at the origin, oscillating up and down at frequency $f$. Every time it pushes up it creates a new crest; every time it pulls down it creates a trough. These disturbances spread outward in **all horizontal directions equally**, because there is nothing to prefer one direction over another. The result is a set of **concentric circular wavefronts** — the rings you see in the simulation.

Each ring marks the current position of one outgoing crest. The rings are not standing still; they expand outward at the **wave speed** $v$ while new rings are continuously born at the source.

> 💡 **Analogy:** Think of a loudspeaker cone. It pushes air in and out at a fixed frequency. Each push creates a pressure crest that travels outward as a spherical shell of compressed air — the sound wave you hear. The 2-D version of that shell is the circular ring you see on the 3-D surface.

---

## 4. The Wave Equation

The mathematical description of the wave field is:

$$
u(r,\, t) = \frac{\cos(k r - \omega t)}{\sqrt{r}} \cdot e^{-\alpha r}
$$

Let's break that into three parts.

### Part 1 — The oscillation: $\cos(kr - \omega t)$

This is the "wave" part. It oscillates between −1 and +1 as either **position** $r$ or **time** $t$ changes.

- Fix $t$ and move outward in $r$: you see the crests and troughs frozen in space — a snapshot of the rings.
- Fix $r$ and let $t$ advance: you see that point bobbing up and down at frequency $f$.

The argument $kr - \omega t$ is called the **phase**. When the phase equals $2\pi n$ for any integer $n$, you are sitting on a crest. As $t$ increases, the phase condition moves outward — the crest radiates away.

### Part 2 — Cylindrical spreading: $1/\sqrt{r}$

As a crest ring expands, its circumference grows as $2\pi r$. The total energy in the wave is shared equally around the ring. So the energy per unit length — and therefore the amplitude — falls as $1/r$. Because amplitude is the *square root* of energy density, amplitude falls as:

$$
\text{amplitude} \propto \frac{1}{\sqrt{r}}
$$

This is why the inner rings (freshly born, small $r$) are tall on the 3-D surface, and the outer rings (old, large $r$) have shrunk to gentle ripples. It is not because the wave is "dying" — it is because the same energy is spread over a bigger circle.

### Part 3 — Extra damping: $e^{-\alpha r}$

Real waves also lose energy through friction, viscosity, and scattering. The exponential factor $e^{-\alpha r}$ models this. Here $\alpha = 0.055$, which means the amplitude falls to $1/e \approx 37\%$ of its value after travelling $1/\alpha \approx 18$ spatial units. This keeps the visualization tidy by preventing rings from wrapping around indefinitely.

---

## 5. Why Do Ridges Fade with Distance?

Put together, the amplitude of a crest ring at radius $r$ is:

$$
A(r) = \frac{e^{-\alpha r}}{\sqrt{r}}
$$

Here is how that looks at a few distances from the source (with $\alpha = 0.055$):

| Distance $r$ | $1/\sqrt{r}$ | $e^{-\alpha r}$ | Combined $A(r)$ |
|---|---|---|---|
| 0.5 | 1.41 | 0.973 | 1.37 |
| 1.0 | 1.00 | 0.946 | 0.95 |
| 2.0 | 0.71 | 0.895 | 0.63 |
| 4.0 | 0.50 | 0.800 | 0.40 |
| 8.0 | 0.35 | 0.641 | 0.23 |

The 3-D surface makes this visible: the innermost ring towers above the outer rings. The energy is not disappearing — it is spreading out.

---

## 6. Wave Speed, Wavelength, and Frequency

Four numbers govern how a wave moves. They are not independent — three of them determine the fourth.

| Symbol | Name | Meaning |
|---|---|---|
| $\lambda$ | Wavelength | Distance between two neighbouring crests |
| $f$ | Frequency | Number of crests passing a fixed point per second |
| $T = 1/f$ | Period | Time for one full oscillation |
| $v$ | Wave speed | How fast a crest travels outward |

The fundamental link between them:

$$
\boxed{v = \lambda \cdot f = \frac{\omega}{k}}
$$

where $\omega = 2\pi f$ is the **angular frequency** and $k = 2\pi/\lambda$ is the **wave number**.

In the simulation:

$$
\lambda = 1.5 \quad v = 2.5 \quad f = v/\lambda \approx 1.67 \text{ Hz} \quad T \approx 0.60 \text{ s}
$$

> 💡 **Intuition check:** If you double the frequency (make the source vibrate twice as fast) while holding the wave speed fixed, the crests are born twice as often. They still travel at the same speed, so they pile up closer together — the wavelength halves. That is exactly what $v = \lambda f$ says.

---

## 7. Where Are the Crests at Any Moment?

The crest condition is: phase $= 2\pi n$

$$
kr - \omega t = 2\pi n \qquad (n = 0,\; 1,\; 2,\; \ldots)
$$

Solving for $r$:

$$
\boxed{r_n(t) = v \cdot t - n\lambda}
$$

The outermost ring ($n = 0$) is the **leading wavefront** — the first crest born at $t = 0$, now at $r = vt$. Each subsequent ring ($n = 1, 2, \ldots$) was born one period $T$ later, so it is one wavelength $\lambda$ behind.

The simulation draws these rings in red directly on the 3-D surface so you can see exactly where the formula predicts the crests to be.

---

## 8. Two Sources: Interference

Place a second identical source at $(+d, 0)$ and the first at $(-d, 0)$. Each emits the same wave independently. The total displacement at any point is just the **sum** of the two individual waves:

$$
u_\text{total}(x, y, t) = u_{S_1}(r_A, t) + u_{S_2}(r_B, t)
$$

where $r_A$ and $r_B$ are the distances from each source to the point $(x, y)$.

### Constructive interference — tall peaks

When the two waves arrive **in phase** (crest meets crest), they add to double the amplitude. This happens when the path difference is an integer number of wavelengths:

$$
|r_A - r_B| = 0,\; \lambda,\; 2\lambda,\; \ldots
$$

On the 3-D surface these points form tall ridges — you can see them as bright peaks towering above the surroundings.

### Destructive interference — flat lanes

When the two waves arrive **out of phase** (crest meets trough), they cancel and the surface stays flat:

$$
|r_A - r_B| = \tfrac{\lambda}{2},\; \tfrac{3\lambda}{2},\; \tfrac{5\lambda}{2},\; \ldots
$$

These are the **nodal lines** — quiet lanes where the surface never moves, visible on the 3-D surface as flat valleys between the tall interference peaks.

> 💡 **Real-world connection:** This is the exact principle behind **Young's double-slit experiment** (1801), which first proved that light is a wave. Two tiny slits act like two point sources; their interference pattern is the bright and dark bands on the screen. Wi-Fi routers, noise-cancelling headphones, and phased-array radar all exploit the same constructive/destructive interference.

The spacing between nodal lines depends on the source separation $2d$ and the wavelength $\lambda$:

$$
\theta_n \approx \frac{n \lambda}{2d} \qquad \text{(angle to the } n\text{-th dark lane)}
$$

In the simulation: $2d = 3.2$, $\lambda = 1.5$, so the first nodal lane is at $\approx 28°$ from the centre axis.

---

## 9. Standing Waves: Pulsating Rings

What happens when a wave reflects back from a boundary and returns toward the source? The outgoing and reflected waves superpose:

$$
u_\text{out}  = \frac{\cos(kr - \omega t)}{\sqrt{r}} e^{-\alpha r}
$$

$$
u_\text{ref}  = \frac{\cos(kr + \omega t)}{\sqrt{r}} e^{-\alpha r}
$$

Adding them with the product-to-sum identity:

$$
u_\text{out} + u_\text{ref} = \underbrace{\frac{2\cos(kr)}{\sqrt{r}} e^{-\alpha r}}_{\text{spatial envelope}} \cdot \underbrace{\cos(\omega t)}_{\text{time pulsation}}
$$

This is a **standing wave**. The key difference from a travelling wave is:

| Travelling wave | Standing wave |
|---|---|
| Crest positions move outward with time | Crest/trough positions are **fixed in space** |
| Any given point oscillates with a phase that depends on its distance from the source | The **whole surface** scales up and down together |
| No permanent zeros (except at $t$ when $\cos = 0$) | **Node rings** are permanently at $z = 0$ |

### Node rings — always zero

Node rings are where $\cos(kr) = 0$, i.e. $kr = \pi/2 + n\pi$:

$$
\boxed{r_n = \frac{(2n+1)\,\lambda}{4}} \qquad n = 0,\; 1,\; 2,\; \ldots
$$

These rings never move and never have any displacement. The violet ring overlays in the simulation mark their exact positions.

### Antinodes — maximum pulsation

Between node rings the surface alternates between a crest (when $\cos(\omega t) = +1$) and a trough (when $\cos(\omega t) = -1$). The entire surface "breathes" — inhaling to its maximum shape, collapsing to flat, exhaling to its minimum shape, then back.

> 💡 **Guitar string analogy:** A plucked guitar string forms a standing wave. The bridge and nut are nodes (always still). The middle of the string is an antinode (maximum vibration). The frequency you hear is $f = v/(2L)$ where $L$ is the string length — exactly the standing-wave condition. The pulsating rings are the circular analogue of that string.

---

## 10. The Five Animations

### Scene 0 — Title Splash (`pulsating_rings_title_splash_3d.py`)

A calm title card. The wave runs at `0.65×` speed with amplitude scaled down so it does not overpower the text. Indigo teaser rings rise gently from the surface. Title, subtitle, equation, and credits fade in at staggered delays so the eye has time to register each element. The camera holds a fixed oblique angle — no orbit — to keep the scene still and readable.

**Output:** `pulsating_rings_title_splash_3d.gif`

---

### Scene 1 — Single Pulsating Source (`single_pulsating_source_3d.py`)

The core demonstration. One source at the origin drives the full wave field. Red ring overlays mark the analytic crest positions $r_n = vt - n\lambda$ directly on the surface. The source dot pulsates at $\omega$ to show what is driving the outgoing ridges. A live readout in the top-left shows the current time $t$, the radius of the leading crest, and the number of visible rings. The camera slowly orbits so the 3-D ridge-and-valley topology is seen from all angles.

**Key things to observe:**
- Innermost ring: tallest (most energy, small $r$).
- Outermost ring: shortest (energy spread over large circumference).
- All rings advance at the same speed $v$ — the pattern is self-similar.

**Output:** `single_pulsating_source_3d.gif`

---

### Scene 2 — Two-Source Interference (`two_source_interference_3d.py`)

Two sources $S_1$ (violet rings) and $S_2$ (orange rings) are placed at $(\pm 1.6,\, 0)$. Their individual ring overlays are drawn on the combined surface so you can visually match where one source's crest coincides with the other's crest (tall peak) versus where a crest meets a trough (flat lane). The live readout shows the ratio $2d/\lambda$ — the number that controls how tightly the nodal lanes are spaced. The orbiting camera reveals the fringe structure in three dimensions, which looks like a warped egg-carton.

**Key things to observe:**
- Peaks along the centre axis ($r_A = r_B$, path difference = 0): maximum constructive.
- Flat lanes fanning out diagonally: destructive, path difference = $\lambda/2$.
- The pattern is stationary (does not rotate or drift) because both sources are identical.

**Output:** `two_source_interference_3d.gif`

---

### Scene 3 — Standing Wave (`standing_wave_rings_3d.py`)

The superposition of outgoing and reflected waves. The violet ring overlays are now **fixed** — they mark the permanent node radii $r_n = (2n+1)\lambda/4$ and never move. The surface oscillates between its maximum shape and a flat plane; the rings become brightest when $\cos(\omega t) \approx 0$ (surface collapses to flat) because that is when the node positions are most visually distinguishable. The live readout shows $\omega t$ in degrees and the instantaneous value of $\cos(\omega t)$ so you can correlate the phase with the surface shape.

**Key things to observe:**
- Node rings: always at $z = 0$, never displaced.
- Antinodes (midpoints between nodes): maximum pulsation.
- The whole surface reaches maximum simultaneously — unlike a travelling wave where crests are spread out.

**Output:** `standing_wave_rings_3d.gif`

---

### Bonus — Ridge Peak Tracking (`ridge_wave_propagation.py`)

A stripped-down, single-focus version of Scene 1 designed for studying the outward march of individual crests. Adds a live readout showing $t$, leading-crest radius, and ring count. The camera orbits at a slightly faster rate than the main scenes, giving a more dramatic sense of depth. Wave amplitude is not scaled down, so the full height contrast between inner and outer rings is visible.

**Output:** `ridge_wave_propagation.gif`

---

## 11. How the Code Works

### Grid and wave field

All five scripts share the same spatial setup:

```python
GRID_N = 80
LIM    = 5.0
_grid  = np.linspace(-LIM, LIM, GRID_N)
XX, YY = np.meshgrid(_grid, _grid)
```

This creates an 80 × 80 grid of $(x, y)$ points. The wave displacement $u(x, y, t)$ is computed as a NumPy array of the same shape.

`GRID_N = 80` (rather than the 300 of the original 2-D version) is a deliberate performance trade-off: `plot_surface` draws 80 × 80 = 6 400 quad patches per frame, which is about 14× fewer than 300 × 300. The visual difference on screen is minimal.

### Surface removal and redraw

`plot_surface` does not support in-place updates (unlike `imshow`). Instead the scripts keep a one-element list `SURF = [None]` and replace the surface every frame:

```python
def _set_surface(U):
    if SURF[0] is not None:
        SURF[0].remove()          # delete the previous surface
    SURF[0] = AX.plot_surface(    # draw a brand-new one
        XX, YY, U,
        cmap=WAVE_CMAP, vmin=-1.2, vmax=1.2,
        alpha=0.90, antialiased=False, linewidth=0,
        rcount=GRID_N, ccount=GRID_N,
    )
```

### 3-D ring overlays

Each ring is a `Line3D` artist pre-allocated at startup:

```python
RINGS = [AX.plot([], [], [], lw=1.8, color=RED, alpha=0)[0]
         for _ in range(N_RINGS)]
```

Every frame, `set_data(rx, ry)` and `set_3d_properties(rz)` update the ring's position. The $z$ values are computed from the analytic wave height at the ring radius:

```python
rz = np.full(len(_THETA), ring_height(r, t))
```

This places the ring **on** the surface rather than floating above or below it.

### Camera orbit

```python
azim = _AZ0 + frame * ORBIT_SPEED
elev = _ELEV + 6.0 * np.sin(2 * np.pi * frame / TOTAL_FRAMES)
AX.view_init(elev=elev, azim=azim)
```

The azimuth increments linearly (continuous rotation); the elevation bobs sinusoidally so the view dips slightly toward plan-view and back, giving a natural feeling of depth exploration.

### Saving

All scripts save with `PillowWriter` at 20 fps and 110 dpi — the same settings used across this codebase:

```python
ani.save(OUT, writer=PillowWriter(fps=FPS), dpi=110)
```

---

## 12. Symbol Cheat Sheet

| Symbol | Name | Value in simulation | Meaning |
|---|---|---|---|
| $\lambda$ | Wavelength | 1.5 | Distance between neighbouring crests |
| $k = 2\pi/\lambda$ | Wave number | 4.19 | Spatial frequency — how quickly phase changes with distance |
| $v$ | Wave speed | 2.5 | Speed at which a crest travels outward |
| $\omega = vk$ | Angular frequency | 10.47 | Phase change per unit time at a fixed point |
| $f = \omega/2\pi$ | Frequency | 1.67 Hz | Crests passing a fixed point per second |
| $T = 1/f$ | Period | 0.60 s | Time for one complete oscillation |
| $\alpha$ | Damping constant | 0.055 | Sets the exponential decay length ($1/\alpha \approx 18$ units) |
| $r$ | Radial distance | — | Distance from source to field point |
| $u(r,t)$ | Displacement | — | Surface height (z value) at radius $r$, time $t$ |
| $r_n(t) = vt - n\lambda$ | Crest radius | — | Position of the $n$-th outgoing crest ring at time $t$ |
| $r_n = (2n+1)\lambda/4$ | Node radius | — | Position of the $n$-th permanent node in a standing wave |

---

## 13. Want to Learn More?

### Classic textbooks

- **French, A. P.** — *Vibrations and Waves* (MIT Introductory Physics Series). The clearest undergraduate introduction to wave mechanics; the 1-D and 2-D wave equations are derived step by step.
- **Crawford, F. S.** — *Waves* (Berkeley Physics Course Vol. 3). Loaded with physical intuition and experiments you can try at home.

### Historical papers (readable summaries)

- **Huygens' Principle (1678):** Every point on a wavefront acts as a new source of secondary wavelets — the principle behind why waves bend around corners.
- **Young's double-slit (1801):** The experiment that proved light is a wave by demonstrating the interference pattern.

### Online resources

- [PhET Waves Intro](https://phet.colorado.edu/en/simulations/wave-on-a-string) — interactive string-wave simulation from University of Colorado
- [PhET Wave Interference](https://phet.colorado.edu/en/simulations/wave-interference) — 2-D point-source interference, directly related to Scenes 2 and 3

### Next steps in this codebase

| Script | What it adds |
|---|---|
| `physics/free_wave_packet.py` | A wave packet (localised group of waves) — what happens when you add many frequencies together |
| `physics/non_relativistic_schrodinger_equation.py` | The quantum-mechanical wave equation — the wave function obeys a very similar spreading equation |
| `math/dirac_delta_animation.py` | The point-source limit — what a wave looks like when the source is infinitely sharp |
