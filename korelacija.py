import json
import re
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder


# ==========================================================
# CONFIG
# ==========================================================

DATA_FOLDER = Path("data/top5")


# ==========================================================
# HELPERS
# ==========================================================

def extract_num(x):

    if pd.isna(x):
        return None

    x = str(x)

    nums = re.findall(
        r"\d+",
        x.replace(".", "")
    )

    if nums:
        return int("".join(nums))

    return None


def clean_dataframe(df):

    CURRENT_YEAR = 2026

    df = df.copy()

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    for col in [

        "mileage",

        "power",

        "owners",

        "engine_size"

    ]:

        df[col] = (

            df[col]

            .apply(
                extract_num
            )

        )

    df["year"] = (

        df["registration"]

        .astype(
            str
        )

        .str.extract(
            r"(\d{4})"
        )

        .astype(
            float
        )

    )

    # ==================================
    # TIME FEATURES
    # ==================================

    df["age"] = (

        CURRENT_YEAR

        -

        df["year"]

    )

    df["age"] = (

        df["age"]

        .clip(
            lower=0
        )

    )

    # km na leto

    df["km_per_year"] = (

        df["mileage"]

        /

        (

            df["age"]

            + 1

        )

    )

    # moč glede na motor

    df["power_per_engine"] = (

        df["power"]

        /

        (

            df["engine_size"]

            + 1

        )

    )

    # oprema glede na starost

    df["features_per_year"] = (

        df["feature_count"]

        /

        (

            df["age"]

            + 1

        )

    )

    # lastniki glede na starost

    df["owners_per_year"] = (

        df["owners"]

        /

        (

            df["age"]

            + 1

        )

    )

    # moč ob upoštevanju starosti

    df["power_age"] = (

        df["power"]

        *

        (

            1

            /

            (

                df["age"]

                + 1

            )

        )

    )

    return df


def create_feature_importance(df, model_name):

    model_df = df.copy()

    for col in model_df.select_dtypes(
        include="object"
    ):

        model_df[col] = (
            LabelEncoder()
            .fit_transform(
                model_df[col]
                .astype(str)
            )
        )

    model_df = model_df.drop(
        columns=["registration"],
        errors="ignore"
    )

    model_df = model_df.dropna()

    if len(model_df) < 50:
        print(
            f"{model_name}: not enough rows"
        )
        return

    X = model_df.drop(
        columns=["price"]
    )

    y = model_df["price"]

    model = RandomForestRegressor(
        n_estimators=800,
        max_depth=18,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X,
        y
    )

    importance = (
        pd.Series(
            model.feature_importances_,
            index=X.columns
        )
        .sort_values()
    )

    plt.figure(
        figsize=(10, 6)
    )

    importance.plot(
        kind="barh"
    )

    plt.title(
        f"{model_name} — Feature Importance"
    )

    plt.tight_layout()

    plt.show()


def create_graphs(df, model_name):
    numeric = [
        "price",
        "mileage",
        "power",
        "engine_size",
        "year",
        "age",
        "km_per_year",
        "power_per_engine",
        "features_per_year",
        "owners_per_year",
        "power_age",
        "owners",
        "feature_count"
    ]

    # ----------------------
    # CORRELATION
    # ----------------------

    corr = (
        df[numeric]
        .corr(
            numeric_only=True
        )
    )

    plt.figure(
        figsize=(8, 6)
    )

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        center=0
    )

    plt.title(
        f"{model_name} Correlation"
    )

    plt.show()

    # ----------------------
    # MAIN PLOTS
    # ----------------------

    fig, ax = plt.subplots(
        2,
        2,
        figsize=(14, 10)
    )

    sns.scatterplot(
        data=df,
        x="mileage",
        y="price",
        ax=ax[0, 0]
    )

    ax[0, 0].set_title(
        "Mileage vs Price"
    )

    sns.scatterplot(
        data=df,
        x="year",
        y="price",
        ax=ax[0, 1]
    )

    ax[0, 1].set_title(
        "Year vs Price"
    )

    sns.regplot(
        data=df,
        x="power",
        y="price",
        ax=ax[1, 0]
    )

    ax[1, 0].set_title(
        "Engine Power vs Price"
    )

    sns.boxplot(
        data=df,
        x="transmission",
        y="price",
        ax=ax[1, 1]
    )

    ax[1, 1].set_title(
        "Transmission vs Price"
    )

    plt.tight_layout()

    plt.show()

    # ----------------------
    # ENGINE SIZE
    # ----------------------

    plt.figure(
        figsize=(8, 6)
    )

    sns.regplot(
        data=df,
        x="engine_size",
        y="price"
    )

    plt.title(
        f"{model_name} Engine Size"
    )

    plt.show()


# ==========================================================
# LOAD EACH MODEL SEPARATELY
# ==========================================================

datasets = {}

for file in DATA_FOLDER.glob(
    "*.json"
):

    model_name = file.stem

    print(
        "\nLoading:",
        model_name
    )

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        cars = json.load(f)

    rows = []

    for car in cars:

        attrs = (
            car.get(
                "attributes",
                {}
            )
        )

        rows.append({

            "price":
            car.get(
                "price.total.amount"
            ),

            "mileage":
            attrs.get(
                "Mileage"
            ),

            "power":
            attrs.get(
                "Power"
            ),

            "engine_size":
            attrs.get(
                "Cubic Capacity"
            ),

            "fuel":
            attrs.get(
                "Fuel"
            ),

            "transmission":
            attrs.get(
                "Transmission"
            ),

            "registration":
            attrs.get(
                "First Registration"
            ),

            "owners":
            attrs.get(
                "Number of Vehicle Owners"
            ),

            "feature_count":
            len(
                car.get(
                    "features",
                    []
                )
            )

        })

    df = pd.DataFrame(
        rows
    )

    df = clean_dataframe(
        df
    )

    datasets[
        model_name
    ] = df


# ==========================================================
# RUN PER MODEL
# ==========================================================

for model_name, df in datasets.items():

    print(
        "\n======================"
    )

    print(
        model_name.upper()
    )

    print(
        "Cars:",
        len(df)
    )

    print(
        "Avg price:",
        round(
            df["price"]
            .mean(),
            2
        )
    )

    create_graphs(
        df,
        model_name
    )

    create_feature_importance(
        df,
        model_name
    )


print(
    "\nDone."
)