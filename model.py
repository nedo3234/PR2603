import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


def preprocess_data(data):

    with open(data, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data)



    df["price"] = df["price.total.amount"]

    df["brand"] = df["brand"]
    df["model"] = df["model"]


    df["fuel"] = df["attributes.Fuel"]
    df["transmission"] = df["attributes.Transmission"]
    df["year"] = df["attributes.First Registration"].str[-4:].astype(int)

    df["mileage"] = df["attributes.Mileage"].str.replace("km", "", regex=False).str.replace(",", "", regex=False).str.replace("\xa0", "", regex=False).astype(float)


    df["power_kw"] = df["attributes.Power"].str.extract(r"(\d+)").astype(float)

    df["previous_owners"] = df["attributes.Number of Vehicle Owners"].astype(float)
    df["condition"] = df["attributes.Vehicle condition"]

    return df


df = preprocess_data("data/top5/pezoji.json")
features = ["brand", "model", "fuel", "transmission", "year", "mileage", "power_kw", "previous_owners", "condition"]

target = "price"

X = pd.get_dummies(df[features])

y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
print(f"Mean Absolute Error: {mae:.2f}")

plt.figure(figsize=(8,8))

plt.scatter(y_test, predictions, alpha=0.5)

plt.xlabel("Dejanska cena")
plt.ylabel("Napovedana cena")

plt.title("Dejanska vs napovedana cena")

plt.show()