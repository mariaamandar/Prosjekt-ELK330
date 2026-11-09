import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("SOLWINDONOFF2025.csv", na_values=["n/e"])

df["Tid"] = (
    df["MTU (CET/CEST)"]
    .str.split(" - ").str[0]
    .str.replace("(CET)", "")
    .str.replace("(CEST)", "")
    .str.strip()
)
# print(df["Tid"])
df["Tid"] = pd.to_datetime(df["Tid"], format="%d/%m/%Y %H:%M:%S")

df = df.set_index("Tid")

df["Generation (MW)"] = df["Generation (MW)"].astype(float)

df_sol = df[df["Production Type"]=="Solar"]
df_wind_onshore = df[df["Production Type"]=="Wind Onshore"]
df_wind_offshore = df[df["Production Type"]=="Wind Offshore"]
wind = (df_wind_onshore["Generation (MW)"]+ df_wind_offshore["Generation (MW)"])

# ser først på korrelasjonen for timeverdiene for hele året, med sol plottet mot vindkraft
sol = df_sol["Generation (MW)"]
korrelasjon = sol.corr(wind)
print(f"Korrelasjon mellom sol og vindkraft: {korrelasjon}")

#Plotter solkraft mot vindkraft...
plt.scatter(sol, wind)

plt.xlabel("Solkraftproduksjon (MW)")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Solkraft mot vindkraft")
plt.grid()
plt.show()

# Plotter solkraft mot tid
plt.figure(figsize=(12, 5))
plt.plot(sol.index, sol)
plt.xlabel("Tid")
plt.ylabel("Solkraftproduksjon (MW)")
plt.title("Solkraftproduksjon gjennom 2025")
plt.grid()
plt.show()

# Plotter vindkraft mot tid
plt.figure(figsize=(12, 5))
plt.plot(wind.index, wind)
plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon gjennom 2025")
plt.grid()
plt.show()

#Redusere støy, lage mer "mykere" kurve:
#PLotter solkraft mot tid
sol_myk = sol.rolling(window=168).mean()
wind_myk = wind.rolling(window=168).mean()

plt.figure(figsize=(12, 5))
plt.plot(sol_myk.index, sol_myk)
plt.xlabel("Tid")
plt.ylabel("Solkraftproduksjon (MW)")
plt.title("Solkraftproduksjon gjennom 2025, redusert støy")
plt.grid()
plt.show()

# Plotter vindkraft mot tid
plt.figure(figsize=(12, 5))
plt.plot(wind_myk.index, wind_myk)
plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon gjennom 2025, redusert støy")
plt.grid()
plt.show()


#Enda mykere plot:

sol_trend = sol.rolling(window=24*30, center=True, min_periods=1).mean()
sol_trend2 = sol.rolling(window=24*30*3, center=True, min_periods=1).mean()

plt.figure(figsize=(12, 5))
plt.plot(sol_myk.index, sol_myk, label="Solkraft, 7 dagers gjennomsnitt")
plt.plot(sol_trend.index, sol_trend, color="orange",
         linewidth=2.5, label="Solkraft, 30 dagers gjennomsnitt")
plt.plot(sol_trend2.index, sol_trend2, color="red",
         linewidth=2.5, label="Solkraft, tre måneders gjennomsnitt")
plt.xlabel("Tid")
plt.ylabel("Solkraftproduksjon (MW)")
plt.title("Solkraftproduksjon gjennom 2025")
plt.legend()
plt.grid()
plt.show()

wind_trend = wind.rolling(window=24*30, center=True, min_periods=1).mean()
wind_trend2 = wind.rolling(window=24*30*3, center=True, min_periods=1).mean()

plt.figure(figsize=(12, 5))
plt.plot(wind_myk.index, wind_myk, label="Vindkraft, 7 dagers gjennomsnitt")
plt.plot(wind_trend.index, wind_trend, color="orange",
         linewidth=2.5, label="Vindkraft, 30 dagers gjennomsnitt")
plt.plot(wind_trend2.index, wind_trend2, color="red",
         linewidth=2.5, label="Vindkraft, tre måneders gjennomsnitt")
plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon gjennom 2025")
plt.legend()
plt.grid()
plt.show()

