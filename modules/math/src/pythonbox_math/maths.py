from sympy import isprime

# result = sum(p**p for p in range(2, 90) if isprime(p))
# print(f"Sum = {result}")
# print(f"Is prime: {isprime(result)}")

primes = [p for p in range(2, 90) if isprime(p)]
power_terms = {p: p**p for p in primes}

print("\nFirst few terms:")
for p in primes[]:
    print(f"  {p}^{p} = {power_terms[p]}")

total = sum(power_terms.values())
print(f"\nSum has {len(str(total))} digits")
print(f"Sum = {total}")

# Step 5: check if the sum itself is prime
print(f"\nIs the sum prime? {isprime(total)}")