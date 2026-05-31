import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

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
avtomobili = avtomobili[
    avtomobili["J-Kategorija in vrsta vozila (opis)"] == "osebni avtomobil"
]

def starost_vozila_graf(avtomobili):
    avtomobili["B-Datum prve registracije vozila"] = pd.to_datetime(
    avtomobili["B-Datum prve registracije vozila"], errors='coerce'
    )

    avtomobili["starost_vozila"] = 2026 - avtomobili["B-Datum prve registracije vozila"].dt.year

    avtomobili["V7-CO2"] = pd.to_numeric(avtomobili["V7-CO2"], errors='coerce')
    avtomobili["P12-Nazivna moc"] = pd.to_numeric(avtomobili["P12-Nazivna moc"], errors='coerce')
    avtomobili["G-Masa vozila"] = pd.to_numeric(avtomobili["G-Masa vozila"], errors='coerce')
    fig, ax = plt.subplots()
    avtomobili["starost_vozila"].dropna().hist(bins=20, ax=ax)
    ax.set_title("Porazdelitev starosti vozil")
    ax.set_xlabel("Starost (leta)")
    ax.set_ylabel("Število vozil")
    return fig




#rabi izboljšave
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
    fig, ax = plt.subplots()
    df.boxplot(column="V7-CO2", by="P13-Vrsta goriva (opis)", rot=45, ax=ax)
    ax.set_title("CO2 emisije glede na gorivo")
    fig.suptitle("")
    ax.set_xlabel("Vrsta goriva")
    ax.set_ylabel("CO2")
    return fig





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
    fig1, ax1 = plt.subplots()
    ax1.scatter(df["G-Masa vozila"], df["P12-Nazivna moc"], alpha=0.5)
    ax1.set_title("Masa vs moč vozila")
    ax1.set_xlabel("Masa (kg)")
    ax1.set_ylabel("Moč (kW)")

    # --- GRAF 2 ---
    df2 = avtomobili.dropna(subset=["G-Masa vozila", "X-Poraba"])
    df2 = df2[(df2["G-Masa vozila"] < 3000) & (df2["G-Masa vozila"] > 500)]
    df2 = df2[(df2["X-Poraba"] > 1) & (df2["X-Poraba"] < 30)]

    fig2, ax2 = plt.subplots()
    ax2.scatter(df2["G-Masa vozila"], df2["X-Poraba"], alpha=0.5)
    ax2.set_title("Poraba goriva vs masa")
    ax2.set_xlabel("Masa (kg)")
    ax2.set_ylabel("Poraba (L/100 km)")
    return fig1, fig2

fig = masa_moc_graf(avtomobili)
st.pyplot(fig[0])
st.pyplot(fig[1])
plt.close("all")

def masa_poraba_graf(avtomobili):
    import matplotlib.pyplot as plt
    import pandas as pd

    # numeric conversion
    cols = ["G-Masa vozila", "X-Poraba"]

    for col in cols:
        avtomobili[col] = (
            avtomobili[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )
        avtomobili[col] = pd.to_numeric(avtomobili[col], errors="coerce")

    # clean
    df = avtomobili.dropna(subset=cols)

    # odstrani outlierje
    df = df[(df["G-Masa vozila"] > 500) &
        (df["G-Masa vozila"] < 4000) &
        (df["X-Poraba"] < 30)
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    hb = ax.hexbin(df["G-Masa vozila"], df["X-Poraba"], gridsize=40, mincnt=1)
    fig.colorbar(hb, ax=ax, label="Število vozil")
    ax.set_title("Poraba goriva glede na maso vozila")
    ax.set_xlabel("Masa vozila (kg)")
    ax.set_ylabel("Poraba (L/100 km)")
    return fig

        




def naj_obcine_graf(avtomobili):
    top_obcine = avtomobili["C13-Upravna enota uporabnika vozila (opis)"].value_counts().head(10)

    fig, ax = plt.subplots()
    top_obcine.plot(kind="bar", ax=ax)
    ax.set_title("Top 10 občin po številu vozil")
    ax.set_xlabel("Občina")
    ax.set_ylabel("Število vozil")
    plt.xticks(rotation=45)
    return fig



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
    fig, ax = plt.subplots()
    ax.scatter(y_test, predictions, alpha=0.5)
    ax.set_title("Dejanski vs napovedani CO2")
    ax.set_xlabel("Dejanski CO2")
    ax.set_ylabel("Napovedani CO2")
    return fig


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

    fig, ax = plt.subplots()
    trend.plot(ax=ax)
    ax.set_title("Trend registracij: Bencin vs Diesel (1991-2023)")
    ax.set_xlabel("Leto")
    ax.set_ylabel("Število vozil")
    return fig


# Še malo delat na tem, da je bolj lepo in smisleno
def naj_znamke_modeli(avtomobili):
    top_brands = avtomobili["D1-Znamka"].value_counts().head(10)

    fig1, ax1 = plt.subplots()
    top_brands.plot(kind="bar", ax=ax1)
    ax1.set_title("Top 10 znamk vozil")
    ax1.set_xlabel("Znamka")
    ax1.set_ylabel("Število vozil")
    plt.xticks(rotation=45)

    avtomobili["znamka_model"] = avtomobili["D1-Znamka"] + " " + avtomobili["D3-Komerc oznaka"]
    top_models = avtomobili["znamka_model"].value_counts().head(10)

    fig2, ax2 = plt.subplots()
    top_models.plot(kind="bar", ax=ax2)
    ax2.set_title("Top 10 modelov vozil")
    ax2.set_xlabel("Model")
    ax2.set_ylabel("Število")
    plt.xticks(rotation=45)
    return fig1, fig2

def trenutni_trend(avtomobili):
    top_goriva = avtomobili["P13-Vrsta goriva (opis)"].value_counts().head(2)
    fig, ax = plt.subplots()
    top_goriva.plot(kind="bar", ax=ax)
    ax.set_title("Trenutni trend goriv")
    ax.set_xlabel("Vrsta goriva")
    ax.set_ylabel("Število vozil")
    plt.xticks(rotation=45)
    return fig

   


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
        lambda x: x.sort_values(ascending=False).head(10), axis=1
    )

    print("Top 10 znamk po regijah:")
    print(top5_per_region)

    # --- TOP MODELI PO REGIJI ---
    model_region = pd.crosstab(
        avtomobili["regija"],
        avtomobili["znamka_model"]
    )

    for region in model_region.index:
        print(f"\nRegija: {region}")
        print(model_region.loc[region].sort_values(ascending=False).head(10))

    # --- HEATMAP ---
    top10 = avtomobili["D1-Znamka"].value_counts().head(10).index

    filtered = avtomobili[avtomobili["D1-Znamka"].isin(top10)]

    heatmap_data = pd.crosstab(
        filtered["regija"],
        filtered["D1-Znamka"]
    )

    fig, ax = plt.subplots()
    im = ax.imshow(heatmap_data, aspect='auto')
    ax.set_xticks(range(len(heatmap_data.columns)))
    ax.set_xticklabels(heatmap_data.columns, rotation=90)
    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)
    ax.set_title("Znamke po regijah (heatmap)")
    fig.colorbar(im, ax=ax)
    return fig



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

    fig1, ax1 = plt.subplots()
    ev_trend.plot(marker='o', ax=ax1)
    ax1.set_title("Rast električnih vozil po letih")
    ax1.set_xlabel("Leto")
    ax1.set_ylabel("Število EV")

    # --- DELEŽ ---
    all_trend = avtomobili.groupby("leto").size()
    share = (ev_trend / all_trend) * 100

    fig2, ax2 = plt.subplots()
    share.plot(marker='o', ax=ax2)
    ax2.set_title("Delež EV (%) po letih")
    ax2.set_xlabel("Leto")
    ax2.set_ylabel("Delež (%)")

    # --- KUMULATIVNO ---
    cumulative_ev = ev_trend.cumsum()

    fig3, ax3 = plt.subplots()
    cumulative_ev.plot(ax=ax3)
    ax3.set_title("Kumulativno število EV")
    ax3.set_xlabel("Leto")
    ax3.set_ylabel("Skupaj EV")

    # --- REGIJE TREND ---
    ev_region = pd.crosstab(ev_df["leto"], ev_df["regija"])

    fig4, ax4 = plt.subplots()
    ev_region.plot(ax=ax4)
    ax4.set_title("Rast EV po regijah")
    ax4.set_xlabel("Leto")
    ax4.set_ylabel("Število EV")

    # --- TOP ZNAMKE ---
    top_ev_brands = ev_df["D1-Znamka"].value_counts().head(10)

    fig5, ax5 = plt.subplots()
    top_ev_brands.plot(kind="bar", ax=ax5)
    ax5.set_title("Top EV znamke")
    ax5.set_xlabel("Znamka")
    ax5.set_ylabel("Število")
    plt.xticks(rotation=45)

    return fig1, fig2, fig3, fig4, fig5

def korelacijski_graf(avtomobili):
    stolpci = ["G-Masa vozila", "P12-Nazivna moc", "V7-CO2", "P11-Delovna prostornina"]
    df = avtomobili[stolpci].copy()

    for stolpec in stolpci:
        df[stolpec] = (
            df[stolpec]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )
        df[stolpec] = pd.to_numeric(df[stolpec], errors="coerce")

    df = df.dropna()
    fig, ax = plt.subplots()
    sns.heatmap(df.corr(), annot=True, ax=ax)
    ax.set_title("Korelacija med lastnostmi vozil")
    return fig

def starost_co2(avtomobili):
    avtomobili["datum"] = pd.to_datetime(
        avtomobili["B-Datum prve registracije vozila"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    avtomobili["starost"] = 2026 - avtomobili["datum"].dt.year
    avtomobili["gorivo"] = avtomobili["P13-Vrsta goriva (opis)"].str.upper()

    avtomobili.loc[
        avtomobili["P24-Pogonske baterije"].notna() &
        (avtomobili["P24-Pogonske baterije"].astype(str).str.strip() != ""),
        "gorivo"
    ] = "ELEKTRIKA"

    avtomobili["V7-CO2"] = pd.to_numeric(avtomobili["V7-CO2"], errors="coerce")

    df = avtomobili[
        (avtomobili["V7-CO2"] > 0) |
        (avtomobili["gorivo"] == "ELEKTRIKA")
    ]

    df = df.dropna(subset=["starost", "V7-CO2"])
    df = df[df["V7-CO2"] < 500]

    fig, ax = plt.subplots()
    ax.scatter(df["starost"], df["V7-CO2"], alpha=0.3)
    ax.set_title("CO2 emisije glede na starost vozila")
    ax.set_xlabel("Starost (leta)")
    ax.set_ylabel("CO2 (g/km)")
    return fig


def top3_modeli(avtomobili):

    # združi znamko + model
    avtomobili["znamka_model"] = (
        avtomobili["D1-Znamka"].astype(str).str.strip() + " " +
        avtomobili["D3-Komerc oznaka"].astype(str).str.strip()
    )

    # odstrani prazne / nan
    df = avtomobili[
        avtomobili["znamka_model"].notna() &
        (avtomobili["znamka_model"] != "")
    ]

    # top 3 modeli
    top3 = df["znamka_model"].value_counts().head(10)

    print("\nTOP 10 najbolj pogosti modeli v Sloveniji:\n")

    for i, (model, count) in enumerate(top3.items(), start=1):
        print(f"{i}. {model} -> {count} vozil")

top3_modeli(avtomobili)