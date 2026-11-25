
import pandas as pd
import matplotlib.pyplot as plt

# Leser inn CSV-filer fra 2020 til 2025
filer = [f"Prosjekt-ELK330/Data{år}.csv" for år in range(2023, 2026)]

df_liste = []

for fil in filer:
    data = pd.read_csv(fil, na_values=["n/e"])
    df_liste.append(data)

# Slår sammen alle filene
df = pd.concat(df_liste, ignore_index=True)


# Databehandling av tidspunkt
df["Tid"] = (
    df["MTU (CET/CEST)"]
    .str.split(" - ").str[0]
    .str.replace("(CET)", "", regex=False)
    .str.replace("(CEST)", "", regex=False)
    .str.strip()
)

# Konverterer tidspunkt til datetime
df["Tid"] = pd.to_datetime(
    df["Tid"],
    format="%d/%m/%Y %H:%M:%S"
)

# Setter tidspunkt som indeks
df = df.set_index("Tid")

# Konverterer produksjonsverdier til tall
df["Generation (MW)"] = pd.to_numeric(
    df["Generation (MW)"],
    errors="coerce"
)


# Skiller mellom solkraft og vindkraft
df_sol = df[df["Production Type"] == "Solar"]
df_wind_onshore = df[df["Production Type"] == "Wind Onshore"]

sol = df_sol["Generation (MW)"]
wind = df_wind_onshore["Generation (MW)"]


# Slår sammen sol- og vinddata etter tidspunkt
data = pd.concat(
    [sol, wind],
    axis=1,
    keys=["Sol", "Wind"]
)

# Fjerner manglende verdier
data = data.dropna()


# Beregner korrelasjon mellom sol og vind
korrelasjon = data["Sol"].corr(data["Wind"])


# Databehandling: kontrollerer datasettet
print("Antall observasjoner:", len(data))
print("Antall manglende verdier:", data.isna().sum())

print(
    "Antall dupliserte tidspunkter:",
    data.index.duplicated().sum()
)

duplikater = data[data.index.duplicated(keep=False)]

print("Dupliserte tidspunkter:")
print(duplikater.sort_index())

# Det finnes duplikate lokale tidspunkt på grunn av
# overgangen fra sommertid til vintertid.
# Alle observasjonene beholdes.


print("Korrelasjon mellom sol og vindkraft:", korrelasjon)
print("Første tidspunkt:", data.index.min())
print("Siste tidspunkt:", data.index.max())


# Sjekker antall observasjoner per år
antall_per_aar = data.groupby(data.index.year).size()

print("Antall observasjoner per år:")
print(antall_per_aar)


# Kontrollerer manglende tidspunkter i 2025
forventet_tid = pd.date_range(
    start="2025-01-01 00:00:00",
    end="2025-12-31 23:00:00",
    freq="h"
)

mangler = forventet_tid.difference(data.loc["2025"].index)

print("Manglende tidspunkter:", mangler)

# Merk: Kontrollen over bruker lokal tid uten tidssone.
# Overgangen mellom CET og CEST gjør derfor at resultatet
# må tolkes med forsiktighet.


# Undersøker daglig gjennomsnitt og korrelasjon
daglig = data.resample("D").mean().dropna()

print(
    "Daglig korrelasjon:",
    daglig["Sol"].corr(daglig["Wind"])
)


# Plotter solkraft mot vindkraft (timeverdier)
plt.figure(figsize=(8, 5))

plt.scatter(data["Sol"], data["Wind"], alpha=0.3)

plt.xlabel("Solkraftproduksjon (MW)")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Solkraft mot vindkraft")
plt.grid()
plt.savefig("ENTSO-ETreAarAnalyse/Solkraft_mot_vindkraftENTSO-E2.png", dpi=300)
plt.show()


# Plotter daglig solkraft mot daglig vindkraft
plt.figure(figsize=(8, 5))

plt.scatter(daglig["Sol"], daglig["Wind"], alpha=0.5)

plt.xlabel("Daglig gjennomsnittlig solkraftproduksjon (MW)")
plt.ylabel("Daglig gjennomsnittlig vindkraftproduksjon (MW)")
plt.title("Daglig solkraft mot vindkraft")
plt.grid()
plt.savefig("ENTSO-ETreAarAnalyse/Daglig_solkraft_mot_vindkraftENTSO-E2.png", dpi=300)
plt.show()


# Plotter solkraft mot tid
# Viser utvikling og sesongvariasjoner
plt.figure(figsize=(12, 5))

plt.plot(data.index, data["Sol"])

plt.xlabel("Tid")
plt.ylabel("Solkraftproduksjon (MW)")
plt.title("Solkraftproduksjon")
plt.grid()
plt.savefig("ENTSO-ETreAarAnalyse/SolkraftproduksjonMotTidENTSO-E2.png", dpi=300)
plt.show()


# Plotter vindkraft mot tid
# Viser utvikling og sesongvariasjoner
plt.figure(figsize=(12, 5))

plt.plot(data.index, data["Wind"])

plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon")
plt.grid()
plt.savefig("ENTSO-ETreAarAnalyse/VindkraftproduksjonMotTidENTSO-E2.png", dpi=300)
plt.show()


# Reduserer støy ved å lage et glidende gjennomsnitt
# 24 * 7 = 168 timer (én uke)

sol_myk = data["Sol"].rolling(window=24*7).mean()
wind_myk = data["Wind"].rolling(window=24*7).mean()


# Plotter solkraft med redusert støy
plt.figure(figsize=(12, 5))

plt.plot(sol_myk.index, sol_myk)

plt.xlabel("Tid")
plt.ylabel("Solkraftproduksjon (MW)")
plt.title("Solkraftproduksjon, redusert støy (7 dagers gjennomsnitt)")
plt.grid()
plt.savefig("ENTSO-ETreAarAnalyse/Solkraftproduksjon_redusert_stoyENTSO-E2.png", dpi=300)
plt.show()


# Plotter vindkraft med redusert støy
plt.figure(figsize=(12, 5))

plt.plot(wind_myk.index, wind_myk)

plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon, redusert støy (7 dagers gjennomsnitt)")
plt.grid()
plt.savefig("ENTSO-ETreAarAnalyse/Vindkraftproduksjon_redusert_stoyENTSO-E2.png", dpi=300)
plt.show()
