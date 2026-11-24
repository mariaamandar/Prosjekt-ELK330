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


# Konverterer PV power fra W til MW
pvgis["P"] = pd.to_numeric(
    pvgis["P"],
    errors="coerce"
)

pvgis["P"] = pvgis["P"] / 1_000_000


# Leser inn Frost-data
frost = pd.read_csv("vinddata_2018_2021.csv")


# Konverterer Frost-tidspunkt til datetime
frost["referenceTime"] = pd.to_datetime(
    frost["referenceTime"],
    utc=True
)

# Bruker tidspunkt som indeks
frost = frost.set_index("referenceTime")


# Velger vindhastighet og konverterer til numerisk verdi
frost["wind_speed(m/s)"] = pd.to_numeric(
    frost["wind_speed(m/s)"],
    errors="coerce"
)


# Beregner gjennomsnittlig vindhastighet per time
frost_hourly = frost["wind_speed(m/s)"].resample("h").mean()


# Parametere for vindturbinen
P_nominell = 3      # MW
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


# Korrigerer vindhastigheten fra 10 m til 100 m
alpha = 0.14

frost_hourly_100m = frost_hourly * (100 / 10) ** alpha


# Bruker effektkurven på alle vindmålingene
vind_MW = frost_hourly_100m.apply(vindkraft)


# Samler solkraft og vindkraft i ett datasett
data = pd.concat(
    [
        pvgis["P"],
        vind_MW
    ],
    axis=1
)

# Gir kolonnene navn
data.columns = [
    "Sol",
    "Vind_Frost"
]


# Sørger for at begge kolonnene inneholder tall
data["Sol"] = pd.to_numeric(
    data["Sol"],
    errors="coerce"
)

data["Vind_Frost"] = pd.to_numeric(
    data["Vind_Frost"],
    errors="coerce"
)


# Fjerner manglende verdier
data = data.dropna()


# Datakontroll
print("\n--- Datakontroll ---")

print("Antall observasjoner:", len(data))
print("Antall manglende verdier:")
print(data.isna().sum())

print("Dupliserte tidspunkter:", data.index.duplicated().sum())

print("Første tidspunkt:", data.index.min())
print("Siste tidspunkt:", data.index.max())

print("PVGIS første tidspunkt:", pvgis.index.min())
print("PVGIS siste tidspunkt:", pvgis.index.max())

print("Frost første tidspunkt:", frost_hourly.index.min())
print("Frost siste tidspunkt:", frost_hourly.index.max())


# Beregner korrelasjon for timesverdier
korrelasjon_time = data["Sol"].corr(data["Vind_Frost"])

print("\nKorrelasjon per time:")
print(korrelasjon_time)


# Beregner daglig gjennomsnitt
daglig_data = data.resample("D").mean()

# Fjerner dager uten målinger
daglig_data = daglig_data.dropna()


print("\nDaglige målinger:")
print(daglig_data.head())

print("Antall dager:", len(daglig_data))


# Beregner korrelasjon for dagsverdier
korrelasjon_daglig = daglig_data["Sol"].corr(
    daglig_data["Vind_Frost"]
)

print("\nDaglig korrelasjon:")
print(korrelasjon_daglig)


# Plotter daglig solkraft mot daglig vindkraft
plt.figure(figsize=(9, 6))

plt.scatter(
    daglig_data["Sol"],
    daglig_data["Vind_Frost"],
    alpha=0.35,
    s=12
)

plt.xlabel("Daglig gjennomsnittlig solkraftproduksjon (MW)")
plt.ylabel("Daglig gjennomsnittlig vindkraftproduksjon (MW)")

plt.title(
    "Korrelasjon mellom solkraft og vindkraft (2018–2021)"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("Daglig_solkraft_mot_vindkraftPVGISFROST.png", dpi=300)
plt.show()
