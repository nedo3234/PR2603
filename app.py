import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import json, glob
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import main as m



st.set_page_config(page_title="Analiza vozil", layout="wide")


def _read_csv(path):
    df = pd.read_csv(path, sep=";", encoding="latin-1",
                     quotechar='"', on_bad_lines="skip", low_memory=False)
    df.columns = df.columns.str.replace("ï»¿", "", regex=False).str.strip()
    return df

@st.cache_data
def load_register():
    a1 = _read_csv("data/Vozila1.csv")
    a2 = _read_csv("data/Vozila2.csv")
    a3 = _read_csv("data/Vozila3.csv")
    av = pd.concat([a1, a2, a3], ignore_index=True)
    av = av[av["J-Kategorija in vrsta vozila (opis)"] == "osebni avtomobil"]
    return av

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
    import pickle
    pipe = pickle.load(open("data/model2.pkl", "rb"))
    meta = pickle.load(open("data/model2_meta.pkl", "rb"))
    return pipe, meta

combos, raw  = load_combos(min_count=3)
model, cols  = load_model()


st.sidebar.title("Navigacija")
stran = st.sidebar.radio("Izberi razdelek:", ["Analiza podatkov", "Napoved cene"])


if stran == "Analiza podatkov":

    st.title("Interaktivna analiza slovenskega registra vozil")

    av = load_register()
    st.caption(f"Skupaj osebnih avtomobilov v registru: **{len(av):,}**".replace(",", "."))

    graf = st.selectbox("Izberi analizo:", [
        "Porazdelitev starosti vozil",
        "CO2 emisije glede na gorivo",
        "Masa vs moč vozila",
        "Poraba goriva glede na maso",
        "Top 10 občin po številu vozil",
        "Trend registracij: Bencin vs Diesel",
        "Top 10 znamk in modelov",
        "Trenutni trend goriv",
        "Rast EV po letih in regijah",
        "Korelacija med lastnostmi vozil",
        "CO2 glede na starost vozila",
        "Znamke po regijah (heatmap)",
    ])

    av_copy = av.copy()

    if graf == "Porazdelitev starosti vozil":
        fig = m.starost_vozila_graf(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "CO2 emisije glede na gorivo":
        fig = m.emisije_gorivo_graf(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "Masa vs moč vozila":
        fig1 = m.masa_moc_graf(av_copy)
        st.pyplot(fig1); plt.close(fig1)

    elif graf == "Poraba goriva glede na maso":
        fig = m.masa_poraba_graf(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "Top 10 občin po številu vozil":
        fig = m.naj_obcine_graf(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "Trend registracij: Bencin vs Diesel":
        fig = m.trend_registracij(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "Top 10 znamk in modelov":
        fig1, fig2 = m.naj_znamke_modeli(av_copy)
        st.pyplot(fig1); plt.close(fig1)
        st.pyplot(fig2); plt.close(fig2)

    elif graf == "Trenutni trend goriv":
        fig = m.trenutni_trend(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "Rast EV po letih in regijah":
        figs = m.trend_ev(av_copy)
        for f in figs:
            st.pyplot(f); plt.close(f)

    elif graf == "Korelacija med lastnostmi vozil":
        fig = m.korelacijski_graf(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "CO2 glede na starost vozila":
        fig = m.starost_co2(av_copy)
        st.pyplot(fig); plt.close(fig)

    elif graf == "Znamke po regijah (heatmap)":
        fig = m.trend_po_regijah(av_copy)
        st.pyplot(fig); plt.close(fig)


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
            "brand":         znamka,
            "model":         izbran_model,
            "fuel":          gorivo,
            "gear":          menjalnik,
            "condition":     stanje,
            "year":          float(leto),
            "km":            float(km),
            "power":         float(izbrana_moc),
            "engine":        float(izbran_ccm),
            "owners":        float(lastniki),
            "age":           float(2026 - leto),
            "feature_count": 0.0,
            "rating":        np.nan,
        }])

        napoved_log = model.predict(input_df)[0]
        napoved = float(np.expm1(napoved_log))
        st.success(f"### Napovedana cena: **{napoved:,.0f} EUR**")
        st.caption("StackingRegressor (ExtraTrees + GradientBoosting) · 1.124 vozil · 5-fold CV")


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
                .sort_values("Cena (EUR)")