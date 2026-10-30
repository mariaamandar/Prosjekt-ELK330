import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("SOLWINDONOFF2025.csv")

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

df_sol_vind = df[df["Production Type"].isin(["Solar", "Wind Onshore", "Wind Offshore"])
                 ].copy()

print(df_sol_vind.head())
