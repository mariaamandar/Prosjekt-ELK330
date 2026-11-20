import requests
import pandas as pd
from io import StringIO


client_id = "0019155a-ab18-48b5-b9f5-b25bf922f8d7"

url = "https://frost.met.no/observations/v0.csv"

all_data = []

# Hent data for hvert år
for year in range(2018, 2022):

    print(f"Henter data for {year}...")

    params = {
        "sources": "SN18700",
        "referencetime": f"{year}-01-01/{year+1}-01-01",
        "elements": "wind_speed",
        "timeoffsets": "default",
        "levels": "default"
    }

    response = requests.get(
        url,
        params=params,
        auth=(client_id, "")
    )

    response.raise_for_status()

    # Les CSV-dataene
    df_year = pd.read_csv(StringIO(response.text))

    all_data.append(df_year)

# Slå sammen alle årene
df = pd.concat(all_data, ignore_index=True)

# Lagre samlet datasett
df.to_csv("vinddata_2018_2021.csv", index=False)

print(df.shape)

