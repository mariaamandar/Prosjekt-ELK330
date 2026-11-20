
import cmath

# Y-bus-matrise (per unit)
Y_bus = [
    [complex(18, -54), complex(-10, 30), complex(-8, 24)],
    [complex(-10, 30), complex(23.3333333333, -70), complex(-13.3333333333, 40)],
    [complex(-8, 24), complex(-13.3333333333, 40), complex(21.3333333333, -64)]
]

# Effektinjeksjon (per unit)
S = [
    complex(0, 0),
    complex(-0.5, -0.15),
    complex(0.7, 0)
]

# Startspenninger
V = [
    complex(1, 0),
    complex(1, 0),
    complex(1, 0)
]

max_iter = 1000
tol = 1e-10

for iteration in range(max_iter):
    max_error = 0.0

    for i in range(1, 3):

        sum_YV = 0j

        for j in range(3):
            if j != i:
                sum_YV += Y_bus[i][j] * V[j]

        V_new = (
            (S[i].conjugate() / V[i].conjugate()) - sum_YV
        ) / Y_bus[i][i]

        error = abs(V_new - V[i])
        max_error = max(max_error, error)

        V[i] = V_new

    print(f"Iterasjon {iteration + 1}: "
          f"V2 = {V[1]}, V3 = {V[2]}, feil = {max_error:.2e}")

    if max_error < tol:
        print("\nBeregningen har konvergert!")
        break

else:
    print("\nAdvarsel: Beregningen konvergerte ikke.")

print("\nEndelige bussspenninger:")

for i in range(3):
    print(f"Buss {i + 1}: {V[i]:.8f} pu")
    print(f"Beløp: {abs(V[i]):.8f} pu")
    print(f"Vinkel: {cmath.phase(V[i]) * 180 / cmath.pi:.6f} grader")
