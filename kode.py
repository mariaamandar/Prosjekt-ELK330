import pandas as pd
import matplotlib.pyplot as plt

filer = [f"Prosjekt-ELK330/Data{år}.csv" for år in range (2020,2026)]

df_liste =[]

for fil in filer:
    data = pd.read_csv(fil, na_values=["n/e"])
    df_liste.append(data)

df = pd.concat(df_liste, ignore_index = True)


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
data = pd.concat([sol, wind], axis=1, keys=["Sol", "Wind"])
data = data.dropna()

korrelasjon = data["Sol"].corr(data["Wind"])

#Databehandling. sjekk om antall observasjoner stemmer, 
# manglende verdier, og diverse
print("Antall observasjoner: ", len(data))
print("Antall manglende verdier: ", data.isna().sum())
print("Antall dupliserte tidspunkter: ", data.index.duplicated().sum())
duplikater = data[data.index.duplicated(keep=False)]
print(duplikater.sort_index())
# Finnes 6, duplikate lokale tidspunkt pga overgangen
# fra sommertid til vintertid. Alle observasjoner beholdes.
print(f"Korrelasjon mellom sol og vindkraft: {korrelasjon}")
print("Første tidspunkt:", data.index.min())
print("Siste tidspunkt:", data.index.max())

#Sjekk antall observasjoner per år:
antall_per_aar = data.groupby(data.index.year).size()
print("Antall observasjoner per år: ", antall_per_aar)
# Forventede tidspunkter i 2025
forventet_tid = pd.date_range(
    start="2025-01-01 00:00:00",
    end="2025-12-31 23:00:00"
)

# Finn tidspunkter som ikke finnes i datasettet
mangler = forventet_tid.difference(data.loc["2025"].index)
print("Manglende tidspunkter:", mangler)
#Mangler 5 verdier, men setter dem ikke lik null
# da vi vet at det mest sannsynligvis finnes noen verdier her
# den 30. mars er det overgang fra vintertid til sommertid
# 8. april er det en manglende observasjon
# 8. mai er det fire sammenhengende manglende observasjoner

#Prøver å undersøke daglig gjennomsnitt og korrelasjon:
daglig = data.resample("D").mean()

print("Daglig korrelasjon: ", daglig["Sol"].corr(daglig["Wind"]))

#Prøver å undersøke månedlig gjennomsnitt og korrelasjon:
manedlig = data.resample("ME").mean()

print("Månedlig korrelasjon: ", manedlig["Sol"].corr(manedlig["Wind"]))
maned_korrelasjon = data.groupby(data.index.month).apply(
    lambda x: x["Sol"].corr(x["Wind"])
)
print(maned_korrelasjon)
maned_korrelasjon.plot(kind="bar")
plt.xlabel("Måned")
plt.ylabel("Korrelasjon")
plt.title("Korrelasjon mellom solkraft og vindkraft per måned")
plt.axhline(0, color="black")
plt.show()

# Fjern årstidseffekten ved å trekke fra gjennomsnittet
# for samme kalendermåned
manedlig["Sol_avvik"] = (
    manedlig["Sol"] - manedlig.groupby(manedlig.index.month)["Sol"].transform("mean")
)

manedlig["Wind_avvik"] = (
    manedlig["Wind"] - manedlig.groupby(manedlig.index.month)["Wind"].transform("mean")
)

# Beregn korrelasjon mellom avvikene
print("Korrelasjon etter fjerning av sesongmønster:")
print(manedlig["Sol_avvik"].corr(manedlig["Wind_avvik"]))

# Beregn korrelasjon mellom månedlige avvik for hvert år

for år in range(2020, 2026):
    år_data = manedlig[manedlig.index.year == år]

    korrelasjon1 = år_data["Sol_avvik"].corr(
        år_data["Wind_avvik"]
    )

    print(år, round(korrelasjon1, 3))
# Ser at det er 5 av 6 år so ar en svak til moderat negatv korrelasjon.

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
plt.title("Solkraftproduksjon")
plt.grid()
plt.show()

# Plotter vindkraft mot tid
plt.figure(figsize=(12, 5))
plt.plot(wind.index, wind)
plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon")
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
plt.title("Solkraftproduksjon, redusert støy")
plt.grid()
plt.show()

# Plotter vindkraft mot tid
plt.figure(figsize=(12, 5))
plt.plot(wind_myk.index, wind_myk)
plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon, redusert støy")
plt.grid()
plt.show()


#Enda mykere plot:

sol_trend = sol.rolling(window=24*30, center=True, min_periods=1).mean()

plt.figure(figsize=(12, 5))
plt.plot(sol_myk.index, sol_myk, label="Solkraft, 7 dagers gjennomsnitt")
plt.plot(sol_trend.index, sol_trend, color="orange",
         linewidth=2.5, label="Solkraft, 30 dagers gjennomsnitt")
plt.xlabel("Tid")
plt.ylabel("Solkraftproduksjon (MW)")
plt.title("Solkraftproduksjon")
plt.legend()
plt.grid()
plt.show()

wind_trend = wind.rolling(window=24*30, center=True, min_periods=1).mean()

plt.figure(figsize=(12, 5))
plt.plot(wind_myk.index, wind_myk, label="Vindkraft, 7 dagers gjennomsnitt")
plt.plot(wind_trend.index, wind_trend, color="orange",
         linewidth=2.5, label="Vindkraft, 30 dagers gjennomsnitt")
plt.xlabel("Tid")
plt.ylabel("Vindkraftproduksjon (MW)")
plt.title("Vindkraftproduksjon")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(10,5))

maned_korrelasjon.plot(kind="bar")
plt.xlabel("Måned")
plt.ylabel("Pearsons korrelasjonskoeffisient")
plt.title("Korrelasjon mellom solkraft og vindkraft per måned")

plt.xticks(
    range(12), ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Des"],
)
# Sammenligning av korrelasjon

navn = ["Time", "Daglig", "Månedlig"]
verdier = [korrelasjon, daglig["Sol"].corr(daglig["Wind"]), manedlig["Sol"].corr(manedlig["Wind"])]

plt.figure(figsize=(8, 5))
plt.bar(navn, verdier)
plt.ylabel("Pearsons korrelasjonskoeffisient")
plt.title("Korrelasjon ved ulik tidsoppløsning")

plt.grid()
plt.show()