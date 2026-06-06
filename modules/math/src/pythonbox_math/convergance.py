import matplotlib.pyplot as plt

# Number of terms
n_terms = 50

partial_sums = []
current_sum = 0

# Compute partial sums
for n in range(1, n_terms + 1):
    term = 1 / (2 ** n)
    current_sum += term
    partial_sums.append(current_sum)

# Plot
plt.figure()
plt.plot(range(1, n_terms + 1), partial_sums)
plt.axhline(1)  # Limit the series converges to

plt.xlabel("Number of terms (n)")
plt.ylabel("Partial sum")
plt.title("Convergence of Series: sum(1/2^n) → 1")

plt.show()
