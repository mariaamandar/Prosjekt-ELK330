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
pvgis[["P"]].to_csv("solkraft_klargjort.csv")
# Konverterer vindhastighet til numeriske verdier
pvgis["WS10m"] = pd.to_numeric(pvgis["WS10m"], errors="coerce")



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


vind_MW = pvgis["WS10m"].apply(vindkraft)


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

# kunne nok lagt dette inn i en funksjon...
sommer1 = daglig_data.loc["2020-06-01":"2020-08-31"]
sommer2 = daglig_data.loc["2018-06-01":"2018-08-31"]
sommer3 = daglig_data.loc["2019-06-01":"2019-08-31"]
vinter1 = daglig_data.loc["2020-12-01":"2021-02-28"]
vinter2 = daglig_data.loc["2018-12-01":"2019-02-28"]
vinter3 = daglig_data.loc["2019-12-01":"2020-02-29"]

korrelasjon_sommer1 = sommer1["Solkraftproduksjon"].corr(sommer1["Vindkraft"])
korrelasjon_sommer2 = sommer2["Solkraftproduksjon"].corr(sommer2["Vindkraft"])
korrelasjon_sommer3 = sommer3["Solkraftproduksjon"].corr(sommer3["Vindkraft"])
korrelasjon_vinter1 = vinter1["Solkraftproduksjon"].corr(vinter1["Vindkraft"])
korrelasjon_vinter2 = vinter2["Solkraftproduksjon"].corr(vinter2["Vindkraft"])
korrelasjon_vinter3 = vinter3["Solkraftproduksjon"].corr(vinter3["Vindkraft"])

print(f"Sommer 2020: r = {korrelasjon_sommer1:.3f} ({len(sommer1)} dager)")
print(f"Sommer 2018: r = {korrelasjon_sommer2:.3f} ({len(sommer2)} dager)")
print(f"Sommer 2019: r = {korrelasjon_sommer3:.3f} ({len(sommer3)} dager)")
print(f"Vinter 2020/2021: r = {korrelasjon_vinter1:.3f} ({len(vinter1)} dager)")
print(f"Vinter 2018/2019: r = {korrelasjon_vinter2:.3f} ({len(vinter2)} dager)")
print(f"Vinter 2019/2020: r = {korrelasjon_vinter3:.3f} ({len(vinter3)} dager)")

# standardavvik for sommer1 og vinter1
standardavvik_sommer = sommer1[["Solkraftproduksjon", "Vindkraft"]].std()
standardavvik_vinter = vinter1[["Solkraftproduksjon", "Vindkraft"]].std()

print(f"Sommer 2020: Standardavvik = {standardavvik_sommer}")
print(f"Vinter 2020/2021: Standardavvik = {standardavvik_vinter}")

fig, (ax_sommer, ax_vinter) = plt.subplots(
    1, 2, figsize=(12, 5), sharex=True, sharey=True
)

ax_sommer.scatter(
    sommer1["Solkraftproduksjon"] * 1_000_000,
    sommer1["Vindkraft"],
    color="tab:orange",
    alpha=0.6,
    s=25
)
ax_sommer.set_title(f"Sommer 2020 ($r = {korrelasjon_sommer1:.3f}$)")
ax_sommer.grid(alpha=0.3)

ax_vinter.scatter(
    vinter1["Solkraftproduksjon"] * 1_000_000,
    vinter1["Vindkraft"],
    color="tab:blue",
    alpha=0.6,
    s=25
)
ax_vinter.set_title(f"Vinter 2020/2021 ($r = {korrelasjon_vinter1:.3f}$)")
ax_vinter.grid(alpha=0.3)

fig.supxlabel("Gjennomsnittlig solkraftproduksjon per døgn (W)")
fig.supylabel("Gjennomsnittlig beregnet vindkraft per døgn (MW)")

fig.tight_layout()
fig.savefig("PVGISanalyse/PVGIS_sommer_vinter.png", dpi=300)
plt.show()

# Scatterplot sommer: juni, julig, august 2020
plt.scatter(
    sommer1["Solkraftproduksjon"], 
    sommer1["Vindkraft"],
    alpha = 0.5,
    s=12
)

plt.xlabel("Gjennomsnittlig solkraftproduksjon per døgn (MW)")
plt.ylabel("Gjennomsnittlig beregnet vindkraft per døgn (MW)")
plt.title("Sommer 2020: Solkraft mot beregnet vindkraft")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("Sommer2020_Solkraft_mot_vindkraftPVGIS.png", dpi=300)
plt.show()

# Scatterplot vinter: desember, januar, februar 2020/2021
plt.scatter(
    vinter1["Solkraftproduksjon"], 
    vinter1["Vindkraft"],
    alpha = 0.5,
    s=12
)

plt.xlabel("Gjennomsnittlig solkraftproduksjon per døgn (MW)")
plt.ylabel("Gjennomsnittlig beregnet vindkraft per døgn (MW)")
plt.title("Vinter 2020/2021: Solkraft mot beregnet vindkraft")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("PVGISanalyse/Vinter2020_2021_Solkraft_mot_vindkraftPVGIS.png", dpi=300)
plt.show()

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
plt.savefig("PVGISanalyse/Solkraft_mot_vindkraftPVGIS.png", dpi=300)
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
plt.savefig("PVGISanalyse/Daglig_solkraft_mot_vindkraftPVGIS.png", dpi=300)
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

plt.savefig("PVGISanalyse/Solinnstraling_2018_2021.png", dpi=300)

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

plt.savefig("PVGISanalyse/Vindhastighet_2018_2021.png", dpi=300)

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

plt.savefig("PVGISanalyse/Vindproduksjon_2018_2021.png", dpi=300)

plt.show()
