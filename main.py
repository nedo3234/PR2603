import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset

avtomobili1 = pd.read_csv(
    "data/Vozila1.csv",
    sep=";",
    encoding="latin-1",
    quotechar='"',
    on_bad_lines="skip",
    low_memory=False
)

avtomobili2 = pd.read_csv(
    "data/Vozila2.csv",
    sep=";",
    encoding="latin-1",
    quotechar='"',
    on_bad_lines="skip",
    low_memory=False
)

avtomobili3 = pd.read_csv(
    "data/Vozila3.csv",
    sep=";",
    encoding="latin-1",
    quotechar='"',
    on_bad_lines="skip",
    low_memory=False
)




avtomobili = pd.concat([avtomobili1, avtomobili2, avtomobili3], ignore_index=True)

def starost_vozila_graf(avtomobili):
    avtomobili["B-Datum prve registracije vozila"] = pd.to_datetime(
    avtomobili["B-Datum prve registracije vozila"], errors='coerce'
    )

    avtomobili["starost_vozila"] = 2026 - avtomobili["B-Datum prve registracije vozila"].dt.year

    avtomobili["V7-CO2"] = pd.to_numeric(avtomobili["V7-CO2"], errors='coerce')
    avtomobili["P12-Nazivna moc"] = pd.to_numeric(avtomobili["P12-Nazivna moc"], errors='coerce')
    avtomobili["G-Masa vozila"] = pd.to_numeric(avtomobili["G-Masa vozila"], errors='coerce') 
    plt.figure()
    avtomobili["starost_vozila"].dropna().hist(bins=20)
    plt.title("Porazdelitev starosti vozil")
    plt.xlabel("Starost (leta)")
    plt.ylabel("Število vozil")
    plt.show()
    plt.figure()


def emisije_gorivo_graf(avtomobili):
    # pretvorba v numeric
    avtomobili["V7-CO2"] = (
        avtomobili["V7-CO2"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    avtomobili["V7-CO2"] = pd.to_numeric(avtomobili["V7-CO2"], errors="coerce")

    # odstrani NaN
    df = avtomobili.dropna(subset=["V7-CO2", "P13-Vrsta goriva (opis)"])
    df = df[df["V7-CO2"] < 1000]
    df.boxplot(column="V7-CO2", by="P13-Vrsta goriva (opis)", rot=45)

    plt.title("CO2 emisije glede na gorivo")
    plt.suptitle("")
    plt.xlabel("Vrsta goriva")
    plt.ylabel("CO2")

    plt.show()


def masa_moc_graf(avtomobili):
    import pandas as pd
    import matplotlib.pyplot as plt

    # --- CLEAN DATA ---
    for col in ["G-Masa vozila", "P12-Nazivna moc", "X-Poraba"]:
        avtomobili[col] = (
            avtomobili[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
        )
        avtomobili[col] = pd.to_numeric(avtomobili[col], errors="coerce")

    # odstrani NaN
    df = avtomobili.dropna(subset=["G-Masa vozila", "P12-Nazivna moc"])
    df = df[(df["G-Masa vozila"] < 3000) & (df["G-Masa vozila"] > 500)]
    df = df[df["P12-Nazivna moc"] < 500]
    df = df[(df["X-Poraba"] > 1) & (df["X-Poraba"] < 30)]

    # --- GRAF 1 ---
    plt.figure()
    plt.scatter(df["G-Masa vozila"], df["P12-Nazivna moc"], alpha=0.5)

    plt.title("Masa vs moč vozila")
    plt.xlabel("Masa (kg)")
    plt.ylabel("Moč (kW)")


    # --- GRAF 2 ---
    df2 = avtomobili.dropna(subset=["G-Masa vozila", "X-Poraba"])
    df2 = df2[(df2["G-Masa vozila"] < 3000) & (df2["G-Masa vozila"] > 500)]
    df2 = df2[(df2["X-Poraba"] > 1) & (df2["X-Poraba"] < 30)]

    plt.figure()
    plt.scatter(df2["G-Masa vozila"], df2["X-Poraba"], alpha=0.5)

    plt.title("Poraba goriva vs masa")
    plt.xlabel("Masa (kg)")
    plt.ylabel("Poraba (L/100 km)")
    plt.show()

def naj_obcine_graf(avtomobili):
    top_obcine = avtomobili["C13-Upravna enota uporabnika vozila (opis)"].value_counts().head(10)

    plt.figure()
    top_obcine.plot(kind="bar")

    plt.title("Top 10 občin po številu vozil")
    plt.xlabel("Občina")
    plt.ylabel("Število vozil")
    plt.xticks(rotation=45)
    plt.show()

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

def co2_razlike(avtomobili):
    
    # --- PRETVORBA DATUMA V STAROST ---
    avtomobili["datum"] = pd.to_datetime(
        avtomobili["B-Datum prve registracije vozila"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    today = pd.Timestamp.today()
    avtomobili["starost"] = (today - avtomobili["datum"]).dt.days // 365

    # --- CLEAN NUMERIC STOLPCEV ---
    for col in ["G-Masa vozila", "P12-Nazivna moc", "V7-CO2"]:
        avtomobili[col] = (
            avtomobili[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(" ", "", regex=False)
        )
        avtomobili[col] = pd.to_numeric(avtomobili[col], errors="coerce")

    # --- FEATURES + TARGET ---
    features = avtomobili[["G-Masa vozila", "P12-Nazivna moc", "starost"]]
    target = avtomobili["V7-CO2"]

    data = pd.concat([features, target], axis=1).dropna()
    # Remove missing CO2 values, but keep EVs
    data = data[
    (data["V7-CO2"] > 0) |
    (avtomobili["P13-Vrsta goriva (opis)"] == "Elektrika")
    ]
    

    X = data[["G-Masa vozila", "P12-Nazivna moc", "starost"]]
    y = data["V7-CO2"]

    # --- TRAIN TEST SPLIT ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # --- MODEL ---
    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # --- EVAL ---
    print("MAE:", mean_absolute_error(y_test, predictions))

    # --- GRAF ---
    plt.figure()
    plt.scatter(y_test, predictions, alpha=0.5)

    plt.title("Dejanski vs napovedani CO2")
    plt.xlabel("Dejanski CO2")
    plt.ylabel("Napovedani CO2")

    plt.show()

def trend_registracij(avtomobili):
    avtomobili["datum"] = pd.to_datetime(
        avtomobili["B-Datum prve registracije vozila"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    avtomobili["leto"] = avtomobili["datum"].dt.year


    avtomobili = avtomobili[avtomobili["leto"] > 1990]

    fuel_df = avtomobili[
        avtomobili["P13-Vrsta goriva (opis)"].isin(["Bencin", "Dizel"])
    ]

    trend = fuel_df.groupby(["leto", "P13-Vrsta goriva (opis)"]).size().unstack()
    trend = trend.fillna(0)

    trend.plot()

    plt.title("Trend registracij: Bencin vs Diesel (1991-2023)")
    plt.xlabel("Leto")
    plt.ylabel("Število vozil")

    plt.show()

# Še malo delat na tem, da je bolj lepo in smisleno
def naj_znamke_modeli(avtomobili):
    top_brands = avtomobili["D1-Znamka"].value_counts().head(10)

    plt.figure()
    top_brands.plot(kind="bar")

    plt.title("Top 10 znamk vozil")
    plt.xlabel("Znamka")
    plt.ylabel("Število vozil")
    plt.xticks(rotation=45)
    

    avtomobili["znamka_model"] = avtomobili["D1-Znamka"] + " " + avtomobili["D3-Komerc oznaka"]

    top_models = avtomobili["znamka_model"].value_counts().head(10)

    plt.figure()
    top_models.plot(kind="bar")

    plt.title("Top 10 modelov vozil")
    plt.xlabel("Model")
    plt.ylabel("Število")
    plt.xticks(rotation=45)
    plt.show()

def trend_po_regijah(avtomobili):
    dovoljene_regije = [
        "LJUBLJANA", "KRANJ", "MARIBOR", "MURSKA SOBOTA",
        "KOPER", "CELJE", "KRŠKO", "SLOVENJ GRADEC",
        "NOVO MESTO", "NOVA GORICA", "POSTOJNA"
    ]

    # normalizacija (velike črke + odstrani presledke)
    avtomobili["regija"] = (
        avtomobili["4A-Registrsko obmocje tablice prve registracije"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # --- FILTER REGIJ ---
    avtomobili = avtomobili[avtomobili["regija"].isin(dovoljene_regije)]

    # --- ZNAMKA + MODEL ---
    avtomobili["znamka_model"] = (
        avtomobili["D1-Znamka"].astype(str) + " " +
        avtomobili["D3-Komerc oznaka"].astype(str)
    )

    # --- TOP 5 ZNAMK PO REGIJI ---
    brand_region = pd.crosstab(
        avtomobili["regija"],
        avtomobili["D1-Znamka"]
    )

    top5_per_region = brand_region.apply(
        lambda x: x.sort_values(ascending=False).head(5), axis=1
    )

    print("Top 5 znamk po regijah:")
    print(top5_per_region)

    # --- TOP MODELI PO REGIJI ---
    model_region = pd.crosstab(
        avtomobili["regija"],
        avtomobili["znamka_model"]
    )

    for region in model_region.index:
        print(f"\nRegija: {region}")
        print(model_region.loc[region].sort_values(ascending=False).head(5))

    # --- HEATMAP ---
    top10 = avtomobili["D1-Znamka"].value_counts().head(10).index

    filtered = avtomobili[avtomobili["D1-Znamka"].isin(top10)]

    heatmap_data = pd.crosstab(
        filtered["regija"],
        filtered["D1-Znamka"]
    )

    plt.figure()
    plt.imshow(heatmap_data, aspect='auto')

    plt.xticks(range(len(heatmap_data.columns)), heatmap_data.columns, rotation=90)
    plt.yticks(range(len(heatmap_data.index)), heatmap_data.index)

    plt.title("Znamke po regijah (heatmap)")
    plt.colorbar()

    plt.show()

# Ima eden prazen graf, je treba to popraviti
def trend_ev(avtomobili):
    # --- DOVOLJENE REGIJE ---
    dovoljene_regije = [
        "LJUBLJANA", "KRANJ", "MARIBOR", "MURSKA SOBOTA",
        "KOPER", "CELJE", "KRŠKO", "SLOVENJ GRADEC",
        "NOVO MESTO", "NOVA GORICA", "POSTOJNA"
    ]

    # --- REGIJA CLEAN ---
    avtomobili["regija"] = (
        avtomobili["4A-Registrsko obmocje tablice prve registracije"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    avtomobili = avtomobili[avtomobili["regija"].isin(dovoljene_regije)]

    # --- DATUM ---
    avtomobili["datum"] = pd.to_datetime(
        avtomobili["B-Datum prve registracije vozila"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    avtomobili["leto"] = avtomobili["datum"].dt.year

    # --- GORIVO ---
    avtomobili["gorivo"] = avtomobili["P13-Vrsta goriva (opis)"].str.upper()

    avtomobili.loc[
        avtomobili["P24-Pogonske baterije"].notna() &
        (avtomobili["P24-Pogonske baterije"].astype(str).str.strip() != ""),
        "gorivo"
    ] = "ELEKTRIKA"

    # --- EV DATA ---
    ev_df = avtomobili[avtomobili["gorivo"] == "ELEKTRIKA"]

    # --- TREND ---
    ev_trend = ev_df.groupby("leto").size()

    plt.figure()
    ev_trend.plot(marker='o')
    plt.title("Rast električnih vozil po letih")
    plt.xlabel("Leto")
    plt.ylabel("Število EV")

    # --- DELEŽ ---
    all_trend = avtomobili.groupby("leto").size()
    share = (ev_trend / all_trend) * 100

    plt.figure()
    share.plot(marker='o')
    plt.title("Delež EV (%) po letih")
    plt.xlabel("Leto")
    plt.ylabel("Delež (%)")

    # --- KUMULATIVNO ---
    cumulative_ev = ev_trend.cumsum()

    plt.figure()
    cumulative_ev.plot()
    plt.title("Kumulativno število EV")
    plt.xlabel("Leto")
    plt.ylabel("Skupaj EV")

    # --- REGIJE TREND ---
    ev_region = pd.crosstab(
        ev_df["leto"],
        ev_df["regija"]   
    )

    plt.figure()
    ev_region.plot()
    plt.title("Rast EV po regijah")
    plt.xlabel("Leto")
    plt.ylabel("Število EV")

    # --- TOP ZNAMKE ---
    top_ev_brands = ev_df["D1-Znamka"].value_counts().head(10)

    plt.figure()
    top_ev_brands.plot(kind="bar")
    plt.title("Top EV znamke")
    plt.xlabel("Znamka")
    plt.ylabel("Število")
    plt.xticks(rotation=45)

    plt.show()


trend_ev(avtomobili)