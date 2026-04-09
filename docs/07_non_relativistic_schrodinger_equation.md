# 07 — Non-Relativistic Schrödinger Equation

> **Source file:** `src/main/python/physics/non_relativistic_schrodinger_equation.py`
> **Renders:** Free Wave Packet · Quantum Tunnelling · Harmonic Oscillator · Infinite Square Well

---

## Table of Contents

1. [What Is Quantum Mechanics? (And Why Should I Care?)](#1-what-is-quantum-mechanics-and-why-should-i-care)
2. [The Big Idea — Particles as Waves](#2-the-big-idea--particles-as-waves)
3. [The Wave Function ψ](#3-the-wave-function-ψ)
4. [The Schrödinger Equation — The Main Formula](#4-the-schrödinger-equation--the-main-formula)
5. [Breaking Down Each Term](#5-breaking-down-each-term)
6. [Why "Non-Relativistic"?](#6-why-non-relativistic)
7. [Four Scenes Explained](#7-four-scenes-explained)
   - [Scene 1 — Free Gaussian Wave Packet](#scene-1--free-gaussian-wave-packet)
   - [Scene 2 — Quantum Tunnelling](#scene-2--quantum-tunnelling)
   - [Scene 3 — Harmonic Oscillator](#scene-3--harmonic-oscillator)
   - [Scene 4 — Infinite Square Well](#scene-4--infinite-square-well)
8. [The Numerical Method — Split-Step Fourier](#8-the-numerical-method--split-step-fourier)
9. [Natural Units (ℏ = m = 1)](#9-natural-units-ℏ--m--1)
10. [Quick Reference — Key Symbols](#10-quick-reference--key-symbols)
11. [Further Reading](#11-further-reading)

---

## 1. What Is Quantum Mechanics? (And Why Should I Care?)

Imagine you are playing billiards. You can predict exactly where the ball goes after every shot — classical (Newtonian) physics works perfectly at that scale.

Now shrink everything down to the size of an **electron** (about 10⁻¹⁰ metres). At that scale, things get *weird*:

- An electron can be **in two places at once** until you measure it.
- It can **pass through walls** that it classically has no energy to cross.
- You **cannot know** both its exact position and exact speed at the same time (Heisenberg's Uncertainty Principle).

Quantum mechanics is the set of rules that governs the behaviour of particles at this tiny scale. It is not just theoretical — it is the foundation of:

| Technology | How QM is involved |
|---|---|
| **Transistors & chips** | Electron behaviour in semiconductors |
| **MRI scanners** | Nuclear spin states |
| **Lasers** | Stimulated emission of photons |
| **Cryptography** | Quantum key distribution |
| **Atomic clocks** | Precise energy level transitions |

---

## 2. The Big Idea — Particles as Waves

In 1924, Louis de Broglie proposed something radical:

> **Every particle also behaves like a wave.**

The wavelength λ of a particle with momentum p is:

$$
\lambda = \frac{h}{p}
$$

where h is Planck's constant (h ≈ 6.626 × 10⁻³⁴ J·s).

Think of it like this: a thrown baseball has such a tiny wavelength (≈ 10⁻³⁴ m) that wave effects are invisible. But an electron's wavelength (≈ 10⁻¹⁰ m) is the same size as an atom — so wave effects dominate everything.

Erwin Schrödinger (1926) took this idea seriously and asked:

> *"If particles are waves, what equation describes how those waves evolve over time?"*

His answer — the **Schrödinger Equation** — changed physics forever.

---

## 3. The Wave Function ψ

The central object in quantum mechanics is the **wave function**, written as the Greek letter **ψ** (psi, pronounced "sigh").

$$
\Psi(x, t)
$$

It is a **complex-valued** function — meaning it can have both a real part and an imaginary part at every point in space and time.

> 💡 **Analogy:** Think of ψ as a "probability cloud". Where the cloud is thick, the particle is likely to be found; where it is thin, the particle is rarely found.

### What does |ψ|² mean?

The **modulus squared** of ψ gives the **probability density**:

$$
P(x, t) = |\Psi(x, t)|^2
$$

This means: "The probability of finding the particle between x and x + dx at time t is |ψ(x,t)|² dx."

### The normalisation condition

Since the particle must *exist somewhere*, all probabilities must add up to 1:

$$
\int_{-\infty}^{\infty} |\Psi(x,t)|^2\, dx = 1
$$

The animation monitors this value and displays it as **∫|ψ|²dx**. It should stay very close to **1.0000** throughout — a built-in sanity check.

---

## 4. The Schrödinger Equation — The Main Formula

Here it is — the star of the show:

$$
\boxed{i\hbar\,\frac{\partial\Psi}{\partial t} = \left[-\frac{\hbar^2}{2m}\,\nabla^2 + V(\mathbf{r},t)\right]\Psi}
$$

At first glance this looks intimidating. Let's read it in plain English:

> **"The rate of change of the wave function over time equals a combination of the particle's kinetic energy and potential energy acting on that wave function."**

It is essentially **F = ma rewritten for quantum waves**.

---

## 5. Breaking Down Each Term

### Left side — iℏ ∂Ψ/∂t

| Symbol | Name | Meaning |
|--------|------|---------|
| **i** | Imaginary unit | √(−1); makes the equation describe oscillating waves |
| **ℏ** | "h-bar" (reduced Planck constant) | h/(2π) ≈ 1.055 × 10⁻³⁴ J·s; the fundamental quantum of action |
| **∂Ψ/∂t** | Partial derivative | How fast ψ is changing at this instant in time |

Together, **iℏ ∂Ψ/∂t** is the quantum version of "rate of change of energy".

---

### Right side — the Hamiltonian operator

The expression in square brackets **[ ... ]** is called the **Hamiltonian** (H), named after William Rowan Hamilton. It represents the *total energy* of the system.

$$
\hat{H} = \underbrace{-\frac{\hbar^2}{2m}\nabla^2}_{\text{kinetic energy}} + \underbrace{V(\mathbf{r},t)}_{\text{potential energy}}
$$

#### Kinetic Energy term: −ℏ²∇²/2m

| Symbol | Meaning |
|--------|---------|
| **ℏ²** | Planck's constant squared |
| **m** | Mass of the particle |
| **∇²** | The Laplacian — measures how "curved" the wave is in space; in 1D this is just ∂²/∂x² |
| **−** | The minus sign comes from the math of Fourier analysis |

> 💡 **Intuition:** A sharply curved wave (short wavelength) corresponds to a particle with *high momentum*, which means *high kinetic energy*. The ∇² operator "detects" this curvature.

#### Potential Energy term: V(x, t)

This is the classical potential energy function — it describes the environment the particle is moving through:

| Potential V(x) | Physical situation |
|---|---|
| V = 0 everywhere | Free particle, no forces |
| V = ∞ outside a box | Particle trapped in a rigid box |
| V = ½mω²x² | Particle on a spring (harmonic oscillator) |
| V = V₀ in a region | A wall or barrier |

---

## 6. Why "Non-Relativistic"?

Einstein's Special Relativity says that nothing can travel faster than light, and that mass and energy are equivalent (E = mc²). The Schrödinger equation **ignores** these effects — it assumes the particle is moving **much slower than the speed of light**.

| | Non-Relativistic | Relativistic |
|---|---|---|
| **Equation** | Schrödinger | Dirac / Klein–Gordon |
| **Valid when** | v ≪ c (electrons in atoms, chemistry) | v ≈ c (particle accelerators) |
| **Handles spin naturally?** | ✗ | ✓ |
| **Complexity** | Moderate | Much higher |

For almost everything in chemistry, materials science, and everyday quantum devices, the non-relativistic Schrödinger equation is **perfectly accurate**.

---

## 7. Four Scenes Explained

### Scene 1 — Free Gaussian Wave Packet

**Setup:** A particle with no forces acting on it (V = 0 everywhere).

The initial wave function is a **Gaussian wave packet** — a bell-curve shaped envelope multiplied by an oscillating wave:

$$
\Psi(x, 0) = \frac{1}{(2\pi\sigma^2)^{1/4}}\, e^{-(x-x_0)^2/(4\sigma^2)}\, e^{ik_0 x}
$$

| Part | Role |
|------|------|
| Bell-curve envelope | Localises the particle near x₀ |
| e^(ik₀x) | Gives the particle momentum ℏk₀ (it moves to the right) |

**What you see:** The packet travels to the right and **spreads out** (disperses) over time. This is *wave dispersion* — different frequency components of the wave travel at slightly different speeds, so the packet smears out.

> 💡 **Analogy:** Drop a pebble in still water. The initial splash is localised, but the ripples spread outward over time — same idea.

---

### Scene 2 — Quantum Tunnelling

**Setup:** A rectangular potential barrier stands in the particle's path. The particle's kinetic energy (E ≈ k₀²/2 = 3.1) is **less than** the barrier height (V₀ = 4.0). Classically, the particle would always bounce back — it simply doesn't have enough energy to climb over.

**What you see:** Part of the wave function **passes through** the barrier and continues on the other side. This is **quantum tunnelling** — one of the most counter-intuitive phenomena in nature.

```
              Barrier (V₀ = 4)
               │████│
→→→→→→→→→→→→→│████│→ (tunnelled part)
              │████│
              ↑ some probability bounces back
```

**Real-world examples of quantum tunnelling:**
- ☀️ **Nuclear fusion in the Sun** — protons tunnel through the Coulomb barrier
- 💾 **Flash memory** — electrons tunnel through thin oxide layers to store data
- 🔬 **Scanning tunnelling microscope (STM)** — images individual atoms

---

### Scene 3 — Harmonic Oscillator (Coherent State)

**Setup:** The particle sits in a parabolic potential well:

$$
V(x) = \frac{1}{2}\omega^2 x^2 \qquad (\omega = 1)
$$

This is the quantum version of a **mass on a spring**. The initial state is a **coherent state** — a special quantum state that behaves most like a classical oscillating particle.

**What you see:** The probability cloud bounces back and forth inside the parabola **without changing shape**. This is remarkable — it is the closest quantum mechanics comes to classical motion.

> 💡 **Analogy:** Imagine a perfectly elastic ball bouncing in a bowl. In classical physics, it oscillates forever. In the quantum case, the whole probability cloud oscillates — the particle is delocalized but still "moves" like the classical ball.

**Why does the shape stay the same?** A coherent state is an eigenstate of the quantum annihilation operator — it is specifically the state that experiences minimum uncertainty while oscillating.

---

### Scene 4 — Infinite Square Well (Quantum Beating)

**Setup:** The particle is trapped inside a box of width L = 20. The walls are infinitely high — the particle can never escape. Inside the box, V = 0.

The allowed energy levels (called **eigenstates** or **stationary states**) are:

$$
E_n = \frac{n^2 \pi^2 \hbar^2}{2mL^2}, \qquad n = 1, 2, 3, \ldots
$$

The corresponding wave functions are standing waves:

$$
\phi_n(x) = \sqrt{\frac{2}{L}}\,\sin\!\left(\frac{n\pi x}{L}\right)
$$

**The superposition:** The simulation starts in a 50/50 mix of n=1 and n=2:

$$
\Psi(x, 0) = \frac{\phi_1(x) + \phi_2(x)}{\sqrt{2}}
$$

**What you see:** The probability cloud **sloshes back and forth** inside the box. This is called **quantum beating** — the two energy levels oscillate at different frequencies, and their interference creates a rhythmic back-and-forth motion.

> 💡 **Analogy:** Play two notes on a guitar that are almost the same pitch. You hear a "wah-wah" beating effect as the sound waves alternately reinforce and cancel each other. Quantum beating is the same phenomenon — but with probability waves.

---

## 8. The Numerical Method — Split-Step Fourier

Solving the Schrödinger equation exactly is only possible for a handful of simple potentials (free particle, harmonic oscillator, hydrogen atom). For anything more complex, we use **numerical methods**.

The code uses the **Split-Step Fourier Method** (also called the Suzuki–Trotter decomposition), which is accurate to second order in the time step.

### The key idea

Evolving by a time step dt involves the operator e^(−iĤdt/ℏ). Because kinetic and potential energy don't commute, we approximate:

$$
e^{-i(\hat{K}+\hat{V})\,dt} \approx e^{-i\hat{V}\,dt/2}\; e^{-i\hat{K}\,dt}\; e^{-i\hat{V}\,dt/2}
$$

This is the **Trotter–Suzuki decomposition**. The error is O(dt³) per step.

### Why split it?

| Operator | Best evaluated in... |
|---|---|
| Potential V(x) | **Real space** — just multiply by e^(−iV·dt/2) |
| Kinetic −ℏ²∇²/2m | **Momentum space** (Fourier space) — just multiply by e^(−iK·dt) |

### Algorithm (one time step)

```
1. Multiply ψ(x) by e^(−iV(x)·dt/2)          ← half step in real space
2. Fourier transform:   ψ(x) → ψ̃(k)
3. Multiply ψ̃(k) by e^(−iK(k)·dt)            ← full kinetic step in k-space
4. Inverse Fourier transform: ψ̃(k) → ψ(x)
5. Multiply ψ(x) by e^(−iV(x)·dt/2)          ← second half step in real space
```

```python
# From the code:
eV  = np.exp(-0.5j * V * dt)     # half-step potential phase
eK  = np.exp(-1j * K * dt)       # full-step kinetic phase (K = k²/2)

psi = eV * psi                   # step 1
psi = np.fft.ifft(eK * np.fft.fft(psi))  # steps 2–4
psi = eV * psi                   # step 5
```

This is elegant, fast (thanks to the FFT), and **conserves probability** to machine precision.

---

## 9. Natural Units (ℏ = m = 1)

Throughout the code, we set **ℏ = 1** and **m = 1**. This simplifies the equation dramatically:

$$
i\,\frac{\partial\Psi}{\partial t} = \left[-\frac{1}{2}\,\frac{\partial^2}{\partial x^2} + V(x)\right]\Psi
$$

The physical values of all quantities are then expressed in units of ℏ and m. For example:

| Quantity | In natural units |
|---|---|
| Energy | ℏ²/(m·length²) |
| Time | m·length²/ℏ |
| Momentum | ℏ/length |

This is standard practice in theoretical and computational physics — it removes clutter and makes the equations universal.

---

## 10. Quick Reference — Key Symbols

| Symbol | Name | Plain English |
|--------|------|---------------|
| Ψ (psi) | Wave function | The quantum "state" of the particle |
| \|Ψ\|² | Probability density | Chance of finding the particle here |
| ℏ | h-bar | Fundamental quantum of action ≈ 1.055×10⁻³⁴ J·s |
| ∂/∂t | Time derivative | Rate of change over time |
| ∇² | Laplacian | Measures spatial curvature of the wave |
| V(x,t) | Potential | The "landscape" the particle moves through |
| k₀ | Wave number | Initial momentum of the wave packet |
| σ | Sigma | Initial width (spread) of the wave packet |
| ⟨x⟩ | Expectation value | Average position of the particle |
| E_n | Energy eigenvalue | Allowed energy level n |
| ω | Omega | Angular frequency of the harmonic oscillator |
| FFT | Fast Fourier Transform | Converts between position space and momentum space |

---

## 11. Further Reading

| Resource | Level | Focus |
|---|---|---|
| **Griffiths — "Introduction to Quantum Mechanics"** | 1st year university | Best introductory textbook |
| **Feynman Lectures Vol. 3** | 1st year university | Conceptual depth, free online |
| **Khan Academy — Quantum Physics** | High school | Gentle intuitive introduction |
| **3Blue1Brown — "But what is the Fourier Transform?"** | High school+ | Visual explanation of FFT |
| **MIT OpenCourseWare 8.04** | University | Full QM course, free |
| **Sakurai — "Modern Quantum Mechanics"** | Advanced | Rigorous mathematical treatment |

---

> **See also:** [`06_fractals_julia_set.md`](06_fractals_julia_set.md) — another example of complex-valued mathematics producing beautiful patterns.

