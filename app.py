import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Analiza vozil", layout="wide")

# ── Load data & model ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return joblib.load("data/cars_clean.pkl")

@st.cache_resource
def load_model():
    model   = joblib.load("data/model.pkl")
    columns = joblib.load("data/model_columns.pkl")
    return model, columns

df           = load_data()
model, cols  = load_model()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.title("Navigacija")
stran = st.sidebar.radio("Izberi razdelek:", ["📊 Analiza podatkov", "🔮 Napoved cene"])

# ═════════════════════════════════════════════════════════════════════════════
# 1. ANALIZA PODATKOV
# ═════════════════════════════════════════════════════════════════════════════
if stran == "📊 Analiza podatkov":

    st.title("📊 Interaktivna analiza vozil")

    # Filtri
    with st.expander("🔧 Filtri", expanded=True):
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


# ═════════════════════════════════════════════════════════════════════════════
# 2. NAPOVED CENE
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.title("🔮 Napoved cene vozila")
    st.markdown(
        "Vnesite lastnosti vozila in model bo napovedal trzno ceno na podlagi "
        "**RandomForest** modela treniranega na ~930 vozilih (MAE ~1525 EUR)."
    )

    col1, col2 = st.columns(2)

    with col1:
        znamka    = st.selectbox("Znamka",        sorted(df["brand"].unique()))
        gorivo    = st.selectbox("Vrsta goriva",  sorted(df["fuel"].unique()))
        menjalnik = st.selectbox("Menjalnik",     ["Automatic", "Manual gearbox"])
        stanje    = st.selectbox("Stanje",        ["Accident-free", "Used", "Damaged"])

    with col2:
        modeli_znamke = sorted(df[df["brand"] == znamka]["model"].unique())
        izbran_model  = st.selectbox("Model", modeli_znamke)
        leto          = st.slider("Leto registracije", 2005, 2024, 2018)
        km            = st.number_input("Prevozeni km", min_value=0, max_value=500000,
                                        value=80000, step=5000)
        moc_kw        = st.number_input("Moc motorja (kW)", min_value=40, max_value=400,
                                        value=85, step=5)
        lastniki      = st.number_input("Stevilo prejsnjih lastnikov", min_value=0,
                                        max_value=10, value=1)

    if st.button("Napovej ceno", type="primary"):
        input_df = pd.DataFrame([{
            "brand":           znamka,
            "model":           izbran_model,
            "fuel":            gorivo,
            "transmission":    menjalnik,
            "year":            float(leto),
            "mileage":         float(km),
            "power_kw":        float(moc_kw),
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

        # Podobna vozila
        st.subheader("Podobna vozila v podatkovni bazi")
        podobna = df[
            (df["brand"] == znamka) &
            (df["fuel"]  == gorivo) &
            (df["year"].between(leto - 2, leto + 2)) &
            (df["mileage"].between(km * 0.6, km * 1.4))
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
            st.info("Ni podobnih vozil v bazi za ta filter.")