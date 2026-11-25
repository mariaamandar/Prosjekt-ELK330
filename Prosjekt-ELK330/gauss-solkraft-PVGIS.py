import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

solkraft = pd.read_csv("solkraft_klargjort.csv", index_col="time", parse_dates=["time"])

sol_dag = solkraft.loc["2020-06-01", "P"]


A = sol_dag.max()
my = sol_dag.idxmax().hour
sigma = 2.5

t = np.linspace(0, 24, 500)

G = A * np.exp(-(t-my)**2 / (2 * sigma**2))

plt.plot(t, G)
plt.xlabel("Tid [timer]")
plt.ylabel("Solkraft [MW]")
plt.grid()
plt.show()