import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("SOLWINDONOFF2025.csv", na_values=["n/e"])

# ikke helt sikker på denne her...
df["Tid"] = (
    df["MTU (CET/CEST)"]
    .str.split(" - ").str[0]
    .str.replace("(CET)", "", regex=False)
    .str.replace("(CEST)", "", regex=False)
    .str.strip()
)
# print(df["Tid"])
df["Tid"] = pd.to_datetime(df["Tid"], format="%d/%m/%Y %H:%M:%S")

df = df.set_index("Tid")

df["Generation (MW)"] = df["Generation (MW)"].astype(float)

df_sol = df[df["Production Type"]=="Solar"]
df_wind_onshore = df[df["Production Type"]=="Wind Onshore"]
df_wind_offshore = df[df["Production Type"]=="Wind Offshore"]
wind = (
    df_wind_onshore["Generation (MW)"]
    + df_wind_offshore["Generation (MW)"]
)

print(df_sol.head())
print(df_wind_onshore.head())
print(df_wind_offshore.head())
print(wind.head())

