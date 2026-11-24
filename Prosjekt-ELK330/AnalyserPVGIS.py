import pandas as pd
import matplotlib.pyplot as plt


# Leser inn PVGIS-data
pvgis = pd.read_csv(
    "PVGISBlindern2018-2021.csv",
    skiprows=10,
    engine="python"
)


# Beholder kun rader der time-kolonnen faktisk inneholder dato
pvgis = pvgis[
    pvgis["time"].astype(str).str.match(r"^\d{8}:\d{4}$")
].copy()


# Konverterer tidspunkt
pvgis["time"] = pd.to_datetime(
    pvgis["time"],
    format="%Y%m%d:%H%M"
)

pvgis = pvgis.set_index("time")


# PVGIS-tidspunktene behandles som UTC
pvgis.index = pvgis.index.tz_localize("UTC")


# Rund av til nærmeste hele time
pvgis.index = pvgis.index.round("h")

# Konverterer PV power til numeriske verdier
pvgis["P"] = pd.to_numeric(pvgis["P"], errors="coerce")

# Konverterer vindhastighet til numeriske verdier
pvgis["WS10m"] = pd.to_numeric(pvgis["WS10m"], errors="coerce")


# Korrigerer vindhastighet fra 96 m til 150 m
alpha = 0.14

vind_100m = pvgis["WS10m"] * (150 / 96) ** alpha


# Parametere for vindturbin
P_nominell = 3       # MW
v_start = 3          # m/s
v_nominell = 12      # m/s
v_stopp = 25         # m/s


# Beregner vindkraftproduksjon
def vindkraft(v):

    if pd.isna(v):
        return float("nan")

    if v < v_start:
        return 0

    elif v < v_nominell:
        return P_nominell * (
            (v**3 - v_start**3) /
            (v_nominell**3 - v_start**3)
        )

    elif v <= v_stopp:
        return P_nominell

    else:
        return 0


vind_MW = vind_100m.apply(vindkraft)


# Samler solinnstråling og vindkraft i ett datasett
data = pd.concat(
    [
        pvgis["P"] / 1_000_000,
        vind_MW
    ],
    axis=1,
    keys=["Solkraftproduksjon", "Vindkraft"]
)


# Sørger for at begge kolonnene inneholder tall
data["Solkraftproduksjon"] = pd.to_numeric(
    data["Solkraftproduksjon"],
    errors="coerce"
)

data["Vindkraft"] = pd.to_numeric(
    data["Vindkraft"],
    errors="coerce"
)


# Fjerner manglende verdier
data = data.dropna()


# Kontrollerer datasettet
print("\n--- Datakontroll ---")

print("Antall observasjoner:", len(data))

print("Antall manglende verdier:")
print(data.isna().sum())

print(
    "Antall dupliserte tidspunkter:",
    data.index.duplicated().sum()
)

print("Første tidspunkt:", data.index.min())
print("Siste tidspunkt:", data.index.max())


# Beregner korrelasjon for timesverdier
korrelasjon_time = data["Solkraftproduksjon"].corr(
    data["Vindkraft"]
)

print("\n--- Korrelasjon per time ---")
print(korrelasjon_time)


# Beregner daglig gjennomsnitt
daglig_data = data.resample("D").mean()

# Fjerner dager uten målinger
daglig_data = daglig_data.dropna()
daglig_data = data.resample("D").mean()

antall_timer = data.resample("D").count()

daglig_data = daglig_data[
    (antall_timer["Solkraftproduksjon"] >= 18) &
    (antall_timer["Vindkraft"] >= 18)
]

print("\n--- Daglige målinger ---")
print(daglig_data.head())

print("Antall dager:", len(daglig_data))


# Beregner korrelasjon for dagsverdier
korrelasjon_daglig = daglig_data["Solkraftproduksjon"].corr(
    daglig_data["Vindkraft"]
)

print("\nDaglig korrelasjon:", korrelasjon_daglig)

maaned = daglig_data.index.month
sommer = daglig_data.loc["2020-06-01":"2020-08-31"]
vinter = daglig_data.loc["2020-12-01":"2021-02-28"]

korrelasjon_sommer = sommer["Solkraftproduksjon"].corr(sommer["Vindkraft"])
korrelasjon_vinter = vinter["Solkraftproduksjon"].corr(vinter["Vindkraft"])

print(f"Sommer 2020: r = {korrelasjon_sommer:.3f} ({len(sommer)} døgn)")
print(f"Vinter 2020/2021: r = {korrelasjon_vinter:.3f} ({len(vinter)} døgn)")


# Plotter solinnstråling mot vindkraft
plt.figure(figsize=(9, 6))

plt.scatter(
    data["Solkraftproduksjon"],
    data["Vindkraft"],
    alpha=0.35,
    s=12
)

plt.xlabel("Solkraftproduksjon (MW)")
plt.ylabel("Beregnet vindkraftproduksjon (MW)")

plt.title(
    "Solkraftproduksjon mot vindkraftproduksjon (2018–2021)"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("Solkraft_mot_vindkraftPVGIS.png", dpi=300)
plt.show()

# Plotter daglig solinnstråling mot daglig vindkraft
plt.figure(figsize=(9, 6))

plt.scatter(
    daglig_data["Solkraftproduksjon"],
    daglig_data["Vindkraft"],
    alpha=0.5,
    s=15
)

plt.xlabel("Daglig gjennomsnittlig Solkraftproduksjon (MW)")
plt.ylabel("Daglig gjennomsnittlig vindkraftproduksjon (MW)")

plt.title(
    "Daglig Solkraftproduksjon mot vindkraftproduksjon (2018–2021)"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("Daglig_solkraft_mot_vindkraftPVGIS.png", dpi=300)
plt.show()

# Konverterer solinnstråling (G(i)) til numeriske verdier
pvgis["G(i)"] = pd.to_numeric(
    pvgis["G(i)"],
    errors="coerce"
)


# Plotter solinnstråling gjennom årene
plt.figure(figsize=(14, 6))

plt.plot(
    pvgis.index,
    pvgis["G(i)"],
    linewidth=0.5
)

plt.xlabel("Tid")
plt.ylabel("Solinnstråling (W/m²)")

plt.title(
    "Solinnstråling gjennom perioden 2018–2021"
)

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("Solinnstraling_2018_2021.png", dpi=300)

plt.show()


plt.figure(figsize=(14, 6))

plt.plot(
    pvgis.index,
    pvgis["WS10m"],
    linewidth=0.5
)

plt.xlabel("Tid")
plt.ylabel("Vindhastighet (m/s)")

plt.title(
    "Vindhastighet gjennom perioden 2018–2021"
)

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("Vindhastighet_2018_2021.png", dpi=300)

plt.show()

plt.figure(figsize=(14, 6))

plt.plot(
    data["Vindkraft"].index,
    data["Vindkraft"],
    linewidth=0.5
)

plt.xlabel("Tid")
plt.ylabel("Vindproduksjon (MW)")

plt.title(
    "Vindproduksjon gjennom perioden 2018–2021"
)

plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("Vindproduksjon_2018_2021.png", dpi=300)

plt.show()
