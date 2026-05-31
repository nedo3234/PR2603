import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import json, glob


st.set_page_config(page_title="Analiza vozil", layout="wide")


@st.cache_data
def load_data():
    return joblib.load("data/cars_clean.pkl")

@st.cache_data
def load_combos(min_count=3):
    files = glob.glob("data/top5/*.json")
    dfs = []
    for f in files:
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        dfs.append(pd.json_normalize(data))
    df = pd.concat(dfs, ignore_index=True)

    df["power_kw"]   = df["attributes.Power"].str.extract(r"(\d+)").astype(float)
    df["cubic_ccm"]  = (
        df["attributes.Cubic Capacity"]
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")
        .astype(float)
    )
    df["brand"] = df["brand"]
    df["model"] = df["model"]
    df["fuel"]  = df["attributes.Fuel"].astype(str).str.split(",").str[0].str.strip()
    df["transmission"] = df["attributes.Transmission"].astype(str)
    df["year"]  = df["attributes.First Registration"].str[-4:].astype(float)
    df["mileage"] = (
        df["attributes.Mileage"].astype(str)
        .str.replace("km", "").str.replace(",", "").str.replace("\xa0", "").str.strip()
    )
    df["mileage"]    = pd.to_numeric(df["mileage"], errors="coerce")
    df["price"]      = pd.to_numeric(df["price.total.amount"], errors="coerce")
    df["previous_owners"] = pd.to_numeric(df["attributes.Number of Vehicle Owners"], errors="coerce")
    df["condition"]  = df["attributes.Vehicle condition"].astype(str).apply(
        lambda x: "Accident-free" if "Accident-free" in x else ("Damaged" if "Damaged" in x else "Used")
    )

    combos = (
        df.groupby(["brand", "model", "cubic_ccm", "power_kw"])
        .size()
        .reset_index(name="count")
    )
    combos = combos[combos["count"] >= min_count]
    return combos, df

@st.cache_resource
def load_model():
    return joblib.load("data/model.pkl"), joblib.load("data/model_columns.pkl")

df           = load_data()
combos, raw  = load_combos(min_count=3)
model, cols  = load_model()


st.sidebar.title("Navigacija")
stran = st.sidebar.radio("Izberi razdelek:", ["Analiza podatkov", "Napoved cene"])


if stran == "Analiza podatkov":

    st.title("Interaktivna analiza vozil")

    with st.expander("Filtri", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            izbrane_znamke = st.multiselect(
                "Znamka", sorted(df["brand"].unique()),
                default=sorted(df["brand"].unique())
            )
        with col2:
            izbrano_gorivo = st.multiselect(
                "Gorivo", sorted(df["fuel"].unique()),
                default=sorted(df["fuel"].unique())
            )
        with col3:
            leto_min, leto_max = int(df["year"].min()), int(df["year"].max())
            leto_range = st.slider("Leto registracije", leto_min, leto_max,
                                   (leto_min, leto_max))

    fdf = df[
        df["brand"].isin(izbrane_znamke) &
        df["fuel"].isin(izbrano_gorivo) &
        df["year"].between(leto_range[0], leto_range[1])
    ]

    st.caption(f"Prikazano vozil: **{len(fdf)}** / {len(df)}")

    graf = st.selectbox("Izberi graf:", [
        "Porazdelitev cen",
        "Cena glede na znamko",
        "Cena glede na gorivo",
        "Cena glede na leto",
        "Cena vs prevozeni km",
        "Cena vs moc (kW)",
        "Porazdelitev prevozenih km",
        "Stevilo vozil po znamki",
    ])

    fig, ax = plt.subplots(figsize=(10, 5))

    if graf == "Porazdelitev cen":
        ax.hist(fdf["price"].dropna(), bins=40, color="steelblue", edgecolor="white")
        ax.set_title("Porazdelitev cen vozil")
        ax.set_xlabel("Cena (EUR)")
        ax.set_ylabel("Stevilo vozil")

    elif graf == "Cena glede na znamko":
        order = fdf.groupby("brand")["price"].median().sort_values(ascending=False).index
        data  = [fdf[fdf["brand"] == b]["price"].dropna().values for b in order]
        ax.boxplot(data, labels=order)
        ax.set_title("Cena glede na znamko")
        ax.set_xlabel("Znamka")
        ax.set_ylabel("Cena (EUR)")
        plt.xticks(rotation=30)

    elif graf == "Cena glede na gorivo":
        order = fdf.groupby("fuel")["price"].median().sort_values(ascending=False).index
        data  = [fdf[fdf["fuel"] == g]["price"].dropna().values for g in order]
        ax.boxplot(data, labels=order)
        ax.set_title("Cena glede na vrsto goriva")
        ax.set_xlabel("Gorivo")
        ax.set_ylabel("Cena (EUR)")
        plt.xticks(rotation=30)

    elif graf == "Cena glede na leto":
        povp = fdf.groupby("year")["price"].median()
        ax.plot(povp.index, povp.values, marker="o", color="steelblue")
        ax.set_title("Mediana cene po letu registracije")
        ax.set_xlabel("Leto")
        ax.set_ylabel("Cena (EUR)")

    elif graf == "Cena vs prevozeni km":
        sample = fdf.dropna(subset=["mileage", "price"]).sample(min(500, len(fdf)), random_state=1)
        ax.scatter(sample["mileage"], sample["price"], alpha=0.5, color="steelblue")
        ax.set_title("Cena glede na prevozene km")
        ax.set_xlabel("Prevozeni km")
        ax.set_ylabel("Cena (EUR)")

    elif graf == "Cena vs moc (kW)":
        sample = fdf.dropna(subset=["power_kw", "price"]).sample(min(500, len(fdf)), random_state=1)
        ax.scatter(sample["power_kw"], sample["price"], alpha=0.5, color="darkorange")
        ax.set_title("Cena glede na moc motorja")
        ax.set_xlabel("Moc (kW)")
        ax.set_ylabel("Cena (EUR)")

    elif graf == "Porazdelitev prevozenih km":
        ax.hist(fdf["mileage"].dropna(), bins=40, color="seagreen", edgecolor="white")
        ax.set_title("Porazdelitev prevozenih km")
        ax.set_xlabel("Km")
        ax.set_ylabel("Stevilo vozil")

    elif graf == "Stevilo vozil po znamki":
        counts = fdf["brand"].value_counts()
        ax.bar(counts.index, counts.values, color="steelblue")
        ax.set_title("Stevilo vozil po znamki")
        ax.set_xlabel("Znamka")
        ax.set_ylabel("Stevilo")
        plt.xticks(rotation=30)

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Tabela vozil")
    st.dataframe(
        fdf[["brand", "model", "fuel", "year", "mileage", "power_kw", "price"]]
        .rename(columns={
            "brand": "Znamka", "model": "Model", "fuel": "Gorivo",
            "year": "Leto", "mileage": "Km", "power_kw": "Moc (kW)", "price": "Cena (EUR)"
        })
        .sort_values("Cena (EUR)")
        .reset_index(drop=True),
        use_container_width=True,
        height=300,
    )


else:
    st.title("Napoved cene vozila")
    st.markdown(
        "Vsi filtri so vezani na dejanske podatke v bazi. "
        "Vsaka kombinacija mora imeti vsaj **3 primere** za prikaz."
    )

    col1, col2 = st.columns(2)


    with col1:
        znamke = sorted(combos["brand"].unique())
        znamka = st.selectbox("1. Znamka", znamke)


    modeli_opcije = sorted(combos[combos["brand"] == znamka]["model"].unique())
    with col2:
        izbran_model = st.selectbox("2. Model", modeli_opcije)

    
    col3, col4 = st.columns(2)

    
    raw_bm = raw[(raw["brand"] == znamka) & (raw["model"] == izbran_model)]

    goriva_mozna = sorted(raw_bm["fuel"].dropna().unique())
    with col3:
        gorivo = st.selectbox("3. Gorivo", goriva_mozna)

    raw_bmf = raw_bm[raw_bm["fuel"] == gorivo]

    
    ccm_counts = raw_bmf["cubic_ccm"].dropna().value_counts()
    ccm_valid  = sorted(ccm_counts[ccm_counts >= 3].index)

    def ccm_label(ccm):
        liter = ccm / 1000
        return f"{liter:.1f} ({int(ccm)} ccm)"

    ccm_labels = {ccm_label(c): c for c in ccm_valid}

    with col4:
        if ccm_labels:
            izbran_motor_label = st.selectbox("4. Motor (prostornina)", list(ccm_labels.keys()))
            izbran_ccm = ccm_labels[izbran_motor_label]
        else:
            st.warning("Ni dovolj podatkov za to kombinacijo.")
            st.stop()

    
    moci_data  = raw_bmf[raw_bmf["cubic_ccm"] == izbran_ccm]["power_kw"].dropna()
    moci_counts = moci_data.value_counts()
    moci_valid  = sorted(moci_counts[moci_counts >= 3].index)
    moc_labels  = {f"{int(m)} kW": int(m) for m in moci_valid}

    col5, col6 = st.columns(2)
    with col5:
        if moc_labels:
            izbrana_moc_label = st.selectbox("5. Moč motorja", list(moc_labels.keys()))
            izbrana_moc = moc_labels[izbrana_moc_label]
        else:
            st.warning("Ni dovolj podatkov za moč tega motorja.")
            st.stop()

    
    n_vozil = int(moci_counts[izbrana_moc]) if izbrana_moc in moci_counts else 0
    st.caption(f"Vozil s to kombinacijo v bazi: **{n_vozil}**")

    
    menjalniki_mozni = sorted(
        raw_bm["transmission"].replace("nan", pd.NA).dropna().unique()
    )
    with col6:
        menjalnik = st.selectbox("6. Menjalnik", menjalniki_mozni if menjalniki_mozni else ["Automatic", "Manual gearbox"])

    col7, col8 = st.columns(2)
    with col7:
        stanje = st.selectbox("7. Stanje", ["Accident-free", "Used", "Damaged"])

    with col8:

        leta_mozna = sorted(
            raw_bm["year"].dropna().astype(int).unique()
        )
        leto = st.selectbox("8. Leto registracije", leta_mozna[::-1])


    km_data = raw_bm["mileage"].dropna()
    km_min  = max(0, int(km_data.quantile(0.05) // 5000 * 5000))
    km_max  = int(km_data.quantile(0.95) // 5000 * 5000 + 5000)
    km_def  = int(km_data.median() // 5000 * 5000)

    km = st.slider(
        f"9. Prevozeni km  (tipično {km_min:,} – {km_max:,} km za ta model)",
        min_value=km_min,
        max_value=km_max,
        value=km_def,
        step=5000,
    )

    lastniki_mozni = sorted(
        raw_bm["previous_owners"].dropna().astype(int).unique()
    )
    lastniki = st.selectbox("10. Število prejšnjih lastnikov", lastniki_mozni if lastniki_mozni else [1])

    st.divider()
    if st.button("Napovej ceno", type="primary"):
        input_df = pd.DataFrame([{
            "brand":           znamka,
            "model":           izbran_model,
            "fuel":            gorivo,
            "transmission":    menjalnik,
            "year":            float(leto),
            "mileage":         float(km),
            "power_kw":        float(izbrana_moc),
            "previous_owners": float(lastniki),
            "condition":       stanje,
        }])

        input_encoded = pd.get_dummies(input_df)
        for c in cols:
            if c not in input_encoded.columns:
                input_encoded[c] = 0
        input_encoded = input_encoded[cols]

        napoved = model.predict(input_encoded)[0]
        st.success(f"### Napovedana cena: **{napoved:,.0f} EUR**")
        st.caption(f"Model treniran na ~930 vozilih · MAE ≈ 1 525 EUR")


        st.subheader("Podobna vozila v podatkovni bazi")
        podobna = raw[
            (raw["brand"]  == znamka) &
            (raw["model"]  == izbran_model) &
            (raw["fuel"]   == gorivo) &
            (raw["year"]   == float(leto)) &
            (raw["mileage"].between(km * 0.6, km * 1.4))
        ][["brand", "model", "fuel", "year", "mileage", "power_kw", "price"]] \
            .rename(columns={
                "brand": "Znamka", "model": "Model", "fuel": "Gorivo",
                "year": "Leto", "mileage": "Km", "power_kw": "Moc (kW)", "price": "Cena (EUR)"
            }) \
            .sort_values("Cena (EUR)") \
            .reset_index(drop=True)

        if len(podobna):
            st.dataframe(podobna, use_container_width=True)
            avg = podobna["Cena (EUR)"].mean()
            st.caption(f"Povprecna cena podobnih vozil: **{avg:,.0f} EUR**")
        else:
            # Sprosti filter na +/- 2 leti
            podobna2 = raw[
                (raw["brand"]  == znamka) &
                (raw["model"]  == izbran_model) &
                (raw["mileage"].between(km * 0.5, km * 1.5))
            ][["brand", "model", "fuel", "year", "mileage", "power_kw", "price"]] \
                .rename(columns={
                    "brand": "Znamka", "model": "Model", "fuel": "Gorivo",
                    "year": "Leto", "mileage": "Km", "power_kw": "Moc (kW)", "price": "Cena (EUR)"
                }) \
                .sort_values("Cena (EUR)") \
                .reset_index(drop=True)
            if len(podobna2):
                st.info("Ni ujemanja za točno leto — prikazujem podobna vozila (vsa leta).")
                st.dataframe(podobna2, use_container_width=True)
            else:
                st.info("Ni podobnih vozil v bazi za ta filter.")