import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

solkraft = pd.read_csv("solkraft_klargjort.csv", index_col="time", parse_dates=["time"])

sol_dag = solkraft.loc["2020-06-01", "P"]

sol_test1 = solkraft.loc["2020-06-06", "P"]
sol_test2 = solkraft.loc["2020-06-10", "P"]

A = sol_dag.max()
my = sol_dag.idxmax().hour
sigma = 2.5

t = np.linspace(0, 24, 500)

G = A * np.exp(-(t-my)**2 / (2 * sigma**2))

plt.plot(t, G, label="Gauss-modell fra 1. juni")
plt.plot(sol_test1.index.hour, sol_test1, label="PVGIS-data fra 6. juni")
plt.plot(sol_test2.index.hour, sol_test2, label="PVGIS-data fra 10. juni")
plt.xlabel("Klokkeslett [UTC]")
plt.ylabel("Solkraft [W]")
plt.legend(["Gauss-modell", "PVGIS-data 6. juni", "PVGIS-data 10. juni"])
plt.grid()
plt.savefig("PVGIS_gauss_sommer.png", dpi=300)
plt.show()