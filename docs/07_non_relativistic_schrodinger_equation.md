# 07 — The Schrödinger Equation (For Normal People)

> **Source file:** `src/main/python/physics/non_relativistic_schrodinger_equation.py`
> **Shows:** Free Wave Packet · Quantum Tunnelling · Harmonic Oscillator · Infinite Square Well

---

## Table of Contents

1. [What Is Quantum Mechanics?](#1-what-is-quantum-mechanics)
2. [Particles Are Also Waves — Seriously](#2-particles-are-also-waves--seriously)
3. [The Wave Function ψ — The Particle's "Mood"](#3-the-wave-function-ψ--the-particles-mood)
4. [The Schrödinger Equation — The Main Formula](#4-the-schrödinger-equation--the-main-formula)
5. [What Does Each Part Mean?](#5-what-does-each-part-mean)
6. [Why "Non-Relativistic"?](#6-why-non-relativistic)
7. [Four Cool Simulations](#7-four-cool-simulations)
   - [Simulation 1 — Free Wave Packet](#simulation-1--free-wave-packet)
   - [Simulation 2 — Quantum Tunnelling](#simulation-2--quantum-tunnelling)
   - [Simulation 3 — Harmonic Oscillator](#simulation-3--harmonic-oscillator)
   - [Simulation 4 — Particle in a Box](#simulation-4--particle-in-a-box)
8. [How the Computer Solves It](#8-how-the-computer-solves-it)
9. [Why Does the Code Use ℏ = 1?](#9-why-does-the-code-use-ℏ--1)
10. [Symbol Cheat Sheet](#10-symbol-cheat-sheet)
11. [Want to Learn More?](#11-want-to-learn-more)

---

## 1. What Is Quantum Mechanics?

Imagine you kick a soccer ball. You can figure out exactly where it will land using simple physics — speed, angle, gravity. Easy.

Now imagine you're trying to track an **electron** (a tiny particle inside every atom). It is about **100,000 times smaller** than the width of a hair. At that size, the normal rules of physics completely break down:

- An electron has **no definite location** until you actually measure it — before that, it exists as a "smear" of possibilities.
- It can **pass through solid walls** even if it doesn't have enough energy to climb over them.
- You **cannot know** its exact position and speed at the same time — knowing one makes the other fuzzier (this is called the **Heisenberg Uncertainty Principle**).

This is not science fiction. It is how nature actually works at tiny scales, and it is called **quantum mechanics**.

You use quantum mechanics every single day without knowing it:

| Technology | Why quantum mechanics matters |
|---|---|
| **Your phone's processor** | Transistors only work because of how electrons behave in tiny semiconductors |
| **MRI scanner** | Uses quantum spin states of atoms inside your body |
| **Lasers** | Every laser pointer is quantum mechanics in action |
| **USB flash drive** | Stores data using quantum tunnelling (more on that below!) |

---

## 2. Particles Are Also Waves — Seriously

In 1924, a French physics student named **Louis de Broglie** had a wild idea for his PhD thesis:

> **Every moving particle also acts like a wave.**

The wavelength (the "size" of the wave) depends on how fast the particle is moving:

$$
\lambda = \frac{h}{p}
$$

- **λ** (lambda) = wavelength — how long one full wave cycle is
- **h** = Planck's constant — a tiny number (6.626 × 10⁻³⁴ J·s) that shows up everywhere in quantum physics
- **p** = momentum = mass × speed

**Why don't we see this for big objects?**
A baseball moving at 30 m/s has a wavelength of about 10⁻³⁴ metres — so unimaginably tiny that the wave effects are completely invisible. But an electron moving at the same speed has a wavelength around 10⁻¹⁰ metres — roughly the size of an atom! At that scale, the wave nature takes over completely.

Erwin Schrödinger (1926) then asked the obvious next question:

> *"OK, particles are waves — so what equation tells us how those waves move and change over time?"*

He figured it out in a weekend at a ski resort. The result is named after him.

---

## 3. The Wave Function ψ — The Particle's "Mood"

The **wave function** is written as the Greek letter **ψ** (psi, pronounced like "sigh"). It is a mathematical function that describes **everything we can possibly know** about a particle:

$$
\Psi(x, t)
$$

- **x** = position
- **t** = time

Think of ψ like a **weather probability map**. Just like a weather map doesn't say "it WILL rain here", it says "there's a 70% chance of rain here" — ψ doesn't say where the particle IS, it says where the particle is **likely to be found** if you look.

> 💡 **Simple analogy:** Imagine you have a friend who could be anywhere in your school. ψ is like a heatmap of the building — red where they're most likely hiding, blue where they probably aren't. The moment you spot them, the whole heatmap "collapses" to one spot.

### So what IS the probability?

To get the actual probability, you square the wave function:

$$
\text{Probability} = |\Psi(x, t)|^2
$$

This is the **#1 rule of quantum mechanics**. Wherever |ψ|² is large, the particle is likely there. Wherever it is small or zero, the particle won't be found there.

### The total must equal 1

Since the particle has to *exist somewhere*, all the probabilities added up must equal exactly 1 (100%):

$$
\int_{-\infty}^{\infty} |\Psi(x,t)|^2\, dx = 1
$$

The simulation displays this as **∫|ψ|²dx** and it should always stay close to **1.0000** — like a running sanity check.

---

## 4. The Schrödinger Equation — The Main Formula

Here it is:

$$
\boxed{i\hbar\,\frac{\partial\Psi}{\partial t} = \left[-\frac{\hbar^2}{2m}\,\frac{\partial^2}{\partial x^2} + V(x,t)\right]\Psi}
$$

This looks scary, but the core message is actually simple:

> **"The way the wave changes over time is controlled by the particle's kinetic energy (how fast it moves) plus its potential energy (what forces are acting on it)."**

It plays the same role in quantum physics that **F = ma** plays in regular physics. F = ma tells you how a ball moves. The Schrödinger equation tells you how a quantum wave moves.

---

## 5. What Does Each Part Mean?

### The left side: iℏ ∂Ψ/∂t

This is asking: *"How fast is the wave changing right now?"*

| Symbol | What it is | Simple meaning |
|--------|-----------|----------------|
| **i** | Imaginary unit (√−1) | Makes the math produce oscillating waves instead of exploding values |
| **ℏ** | "h-bar" | A very tiny number (≈ 10⁻³⁴ J·s) — the fundamental "unit" of the quantum world |
| **∂Ψ/∂t** | Partial derivative | The rate of change of the wave in time — like asking "how fast is this changing?" |

---

### The right side: kinetic energy + potential energy

This is asking: *"What is the total energy affecting the particle?"*

#### Kinetic energy: −ℏ²/2m · ∂²Ψ/∂x²

Think of **∂²Ψ/∂x²** as measuring the *curviness* or *wiggliness* of the wave. A wave that wiggles a lot has short wavelength → high momentum → high kinetic energy. This term captures that.

> 💡 **Analogy:** Imagine drawing waves on paper. A wave with tight, frequent ups-and-downs represents a fast-moving particle. A wave with gentle, wide curves represents a slow-moving one.

#### Potential energy: V(x, t)

This is just the environment the particle is in — like the "terrain" it has to move through:

| V(x) shape | What it means |
|---|---|
| Flat line at zero | No forces — particle moves freely |
| Very tall wall in the middle | A barrier (used for the tunnelling demo) |
| U-shaped bowl (parabola) | A spring — particle gets pulled back to centre |
| Tall vertical walls on both sides | A box — particle is trapped |

---

## 6. Why "Non-Relativistic"?

Einstein showed that when things move close to the speed of light, the rules change — time slows down, mass increases, etc. (Special Relativity, E = mc²).

The Schrödinger equation **ignores all of that**. It assumes the particle is moving much slower than light. This is fine for:
- Electrons in atoms
- Chemistry
- Most everyday quantum devices

When particles move close to light speed (like in a particle collider), you need a different, much harder equation called the **Dirac equation**.

| | Schrödinger (this doc) | Dirac |
|---|---|---|
| Works when | Speed ≪ speed of light | Speed ≈ speed of light |
| Difficulty | Manageable | Much harder |
| Used for | Chemistry, semiconductors | Particle physics |

---

## 7. Four Cool Simulations

### Simulation 1 — Free Wave Packet

**The setup:** A particle is released with no walls, no forces, nothing — just empty space.

The particle starts as a **Gaussian wave packet** — a shape that looks like a hill (or a bell curve) that wiggles:

$$
\Psi(x, 0) = \underbrace{e^{-(x-x_0)^2/(4\sigma^2)}}_{\text{bell-curve shape}} \times \underbrace{e^{ik_0 x}}_{\text{wiggles → gives it momentum}}
$$

**What happens:** The wave packet moves to the right (because of the momentum we gave it) and slowly **spreads out and gets flatter** over time.

> 💡 **Real-life version:** Think of dropping a single drop of ink into a glass of still water. The ink starts concentrated in one spot, 
> but gradually spreads out to fill the glass. The quantum wave packet does the same thing — it "spreads" because different parts of the wave travel at slightly different speeds.

---

### Simulation 2 — Quantum Tunnelling

**The setup:** A solid wall (barrier) is placed in the particle's path. The particle does NOT have enough energy to jump over it. In normal everyday physics, it would just bounce back — end of story.

```
      Particle →→→→→     │ WALL │     ← should be impossible to pass
```

**What actually happens:** A portion of the wave function "leaks through" the wall and keeps going on the other side. This is **quantum tunnelling** — the particle literally passes through a barrier it shouldn't be able to cross.

> 💡 **Analogy:** Imagine throwing a tennis ball at a wall and some of the time it just magically appears on the other side. That is impossible with big objects, but electrons do this all the time.

**You use tunnelling every day:**
- 💾 **USB drives and SSDs** — your data is stored by pushing electrons through a thin barrier using tunnelling
- ☀️ **The Sun shines** because protons tunnel through a barrier to fuse together inside the Sun's core
- 🔬 **Scanning tunnelling microscopes** use tunnelling to "feel" individual atoms on a surface

---

### Simulation 3 — Harmonic Oscillator

**The setup:** The particle is placed inside a bowl-shaped potential (like a U or parabola). This is the quantum version of a **ball rolling back and forth in a bowl**, or a weight on a spring.

$$
V(x) = \frac{1}{2}\omega^2 x^2 \quad \text{(a parabola)}
$$

**What happens:** The probability cloud bounces back and forth inside the bowl, like a pendulum, and its shape stays perfectly the same throughout. This special starting state is called a **coherent state**.

> 💡 **Analogy:** Imagine a water balloon bouncing inside a bowl — the whole blob moves back and forth without deforming. That's what this simulation looks like, but with a probability wave instead of water.

This is the quantum behaviour closest to what we see in everyday objects. Vibrating atoms in solids (which produce heat and sound) behave exactly like this.

---

### Simulation 4 — Particle in a Box

**The setup:** Imagine an electron is completely trapped inside a tiny box. The walls are infinitely hard — the particle can never escape.

Inside the box, only certain wave shapes are allowed — ones that fit perfectly like standing waves on a guitar string:

$$
\phi_n(x) = \sqrt{\frac{2}{L}}\,\sin\!\left(\frac{n\pi x}{L}\right), \qquad n = 1, 2, 3, \ldots
$$

> 💡 **Guitar string analogy:** When you pluck a guitar string, only certain notes are allowed — the ones where the wave fits evenly between the two fixed ends (the frets). Quantum particles in a box work the same way. Only certain "notes" (energy levels) are allowed.

Each allowed wave has a specific energy:

$$
E_n = \frac{n^2 \pi^2 \hbar^2}{2mL^2}
$$

Notice that n = 0 is **not allowed** — the particle always has some minimum energy. It can never be completely still. This is called **zero-point energy**.

**The simulation** starts with a 50/50 mix of the first two allowed waves (n=1 and n=2). Their combination causes the blob to **slosh back and forth** — this rhythmic motion is called **quantum beating**.

> 💡 **Analogy:** Strum two guitar strings that are slightly out of tune at the same time. You'll hear a "wah-wah" wobble as the two sounds alternately add together and cancel out. Quantum beating is the exact same idea — two quantum waves going in and out of sync.

---

## 8. How the Computer Solves It

Most forms of the Schrödinger equation cannot be solved with pen and paper. The code uses a clever trick called the **Split-Step Fourier Method**.

### The basic idea

The total energy has two parts:
- **Kinetic energy** — easy to calculate if you know the momentum
- **Potential energy** — easy to calculate if you know the position

The trick is that **position** and **momentum** live in different mathematical spaces. To switch between them, the code uses a **Fast Fourier Transform (FFT)** — an algorithm that converts a position-space wave into a momentum-space wave and back.

### Each time step works like this:

```
Step 1:  Apply half of the potential energy  (in position space)
Step 2:  Switch to momentum space  (using FFT)
Step 3:  Apply the full kinetic energy  (in momentum space)
Step 4:  Switch back to position space  (using inverse FFT)
Step 5:  Apply the second half of the potential energy
```

```python
# The core of the simulation — just 5 lines!
eV  = np.exp(-0.5j * V * dt)    # potential energy "kick" (half step)
eK  = np.exp(-1j * K * dt)      # kinetic energy "kick" (full step)

psi = eV * psi                                      # step 1
psi = np.fft.ifft(eK * np.fft.fft(psi))            # steps 2–4
psi = eV * psi                                      # step 5
```

This is repeated hundreds of times per second to create the animation. It is fast, accurate, and always keeps the total probability at exactly 1.

---

## 9. Why Does the Code Use ℏ = 1?

If you look at the code, you'll notice there's no `hbar = 1.055e-34` anywhere. That's because the code uses **natural units**, where ℏ = 1 and m = 1.

This is like how a recipe might say "1 cup of flour" instead of "236.6 millilitres" — the numbers are cleaner and easier to work with. The physics is identical; we just chose convenient units.

With these units, the equation becomes much cleaner:

$$
i\,\frac{\partial\Psi}{\partial t} = \left[-\frac{1}{2}\,\frac{\partial^2}{\partial x^2} + V(x)\right]\Psi
$$

All professional physics simulations and research papers do this.

---

## 10. Symbol Cheat Sheet

| Symbol | Name | What it means in plain English |
|--------|------|-------------------------------|
| **Ψ** (psi) | Wave function | The full description of the particle's quantum state |
| **\|Ψ\|²** | Probability density | How likely you are to find the particle at that spot |
| **ℏ** | h-bar | Planck's constant ÷ 2π; the "quantum of action" |
| **m** | Mass | The particle's mass |
| **V(x)** | Potential energy | The "landscape" or forces the particle experiences |
| **∂/∂t** | Time derivative | "How fast is this changing right now?" |
| **∂²/∂x²** | Second spatial derivative | "How wiggly / curved is the wave?" |
| **k₀** | Wave number | Sets the particle's initial speed/direction |
| **σ** | Sigma | How spread out the initial wave packet is |
| **E_n** | Energy level | The nth allowed energy value inside a box |
| **FFT** | Fast Fourier Transform | Converts between position-space and momentum-space waves |

---

## 11. Want to Learn More?

| Resource | Where to find it | Good for... |
|---|---|---|
| **Khan Academy — Quantum Physics** | khanacademy.org | Starting from scratch, free |
| **Veritasium — "Quantum Tunnelling"** | YouTube | Visual, engaging 10-min video |
| **3Blue1Brown — "But what is a Fourier Transform?"** | YouTube | Understanding the FFT visually |
| **Feynman Lectures Vol. 3** | feynmanlectures.caltech.edu | Free online, deep intuition |
| **Griffiths — "Introduction to QM"** | Library / Amazon | First proper university textbook |

---

> **See also:** [`06_fractals_julia_set.md`](06_fractals_julia_set.md) — another place where simple math rules create wildly complex and beautiful patterns.
