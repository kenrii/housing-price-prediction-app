import json
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pgeocode
from nearest_postal_code_algo import find_nearest_postal_code

st.write(
    """
# 🏠 Housing Price Prediction App


Investors can now predict housing price movement in Finland using artificial intelligence with this new real estate investing tool.

The aim of the tool is to work as a complement to traditional real estate investing which mainly relies on local knowledge and human-driven research.
Application uses big data based on historic data with machine-learning algorithms to forecast the future trend of property prices so you will be one step ahead in your investment decision.

**Input your values and predict next four quarters!**

"""
)

nomi = pgeocode.Nominatim("fi")


def get_predictions_df(postal_code, housing_type):
    # Encode categorical values to one hot encoding and postal code to geolocational data (latitude, longitude)
    housing_type_json = get_json_for_housing_type(housing_type)
    housing_type_json_clustered = get_json_for_housing_type(housing_type, types="clustered")
    cluster_label, found_label = get_cluster_label(housing_type, postal_code)
    if postal_code in housing_type_json["pred_0"]:
        print("Found own model")
        return json_to_dataframe(housing_type_json, postal_code)
    elif found_label:
        return json_to_dataframe(housing_type_json_clustered, postal_code, types="clustered", label=cluster_label)
    else:
        nearest_postal_code = find_nearest_postal_code(postal_code, housing_type_json)
        st_disclaimer_nearest_postal_code(True, nearest_postal_code, postal_code)
        return json_to_dataframe(housing_type_json, nearest_postal_code)


def get_cluster_label(housing_type, postal_code):
    csv_dict = {
            "one-room": "cluster_labels/one_room_cluster_dictionary.csv",
            "two-room": "cluster_labels/two_room_cluster_dictionary.csv",
            "three or more room": "cluster_labels/two_room_cluster_dictionary.csv",
            "terrace house": "cluster_labels/two_room_cluster_dictionary.csv",
        }
    csv_file_path = "json_prediction/{}".format(csv_dict[housing_type])
    df = pd.read_csv(csv_file_path, dtype=str)
    if postal_code in list(df["Postal code"].values):
        print("Found label")
        label = df["label6"].values[df["Postal code"] == postal_code][0]
        return str(label), True
    else:
        print("Didn't find label")
        return None, False


def get_json_for_housing_type(housing_type, types="own"):
    if types == "own":
        json_dict = {
            "one-room": "emsembled_own/one_room_ensembled_forecast.json",
            "two-room": "emsembled_own/two_room_ensembled_forecast.json",
            "three or more room": "emsembled_own/three-more_room_ensembled_forecast.json",
            "terrace house": "emsembled_own/terrace_house_ensembled_forecast.json",
        }
    else:
        json_dict = {
            "one-room": "emsembled_clusters/one_room_ensemble_cluster_forecasts.json",
            "two-room": "emsembled_clusters/two_room_ensemble_cluster_forecasts.json",
            "three or more room": "emsembled_clusters/three-more_room_ensemble_cluster_forecasts.json",
            "terrace house": "emsembled_clusters/three-more_room_ensemble_cluster_forecasts.json",
        }
    json_file_path = "json_prediction/{}".format(json_dict[housing_type])

    with open(json_file_path, "r") as j:
        contents = json.loads(j.read())
    return contents


def json_to_dataframe(json_file, postal_code, types="own", label=None):
    future_dates = ["2021-07-01", "2021-10-01", "2022-01-01", "2022-04-01"]
    if types == "own":
        predictions = [float(json_file["pred_" + str(index)][postal_code]) for index in range(4)]
    else:
        predictions = [float(json_file["pred_" + str(index)][label]) for index in range(4)]
    df = pd.DataFrame({"date": future_dates, "price": predictions})
    df["date"] = pd.to_datetime(df["date"])
    return df


def user_input_features():
    # Streamlit interface's inputs to array for predictions
    postal_code = st.text_input("Postal code")
    housing_type = st.selectbox(
        "Housing type", ("one-room", "two-room", "three or more room", "terrace house")
    )
    return postal_code, housing_type


def st_disclaimer_nearest_postal_code(
    found_nearest_postal_code=False, nearest_postal_code=None, postal_code=None
):
    if found_nearest_postal_code:
        st.write(
            "We didn't find a model for ***{}***. Therefore, we predict with the model which is nearest to this postal code: ***{}***.".format(
                postal_code, nearest_postal_code
            )
        )


def check_validity_of_postal_code(postal_code):
    geolocation = nomi.query_postal_code([postal_code])
    latitude, longitude = (
        geolocation["latitude"].iloc[0],
        geolocation["longitude"].iloc[0],
    )
    if pd.isnull(latitude) or pd.isnull(longitude):
        st.error("Please input a valid Finnish postal code.")
        return False
    return True


def display_results_in_table(df):
    quarters_dict = {
        "2021-07-01": "Q3 2021",
        "2021-10-01": "Q4 2021",
        "2022-01-01": "Q1 2022",
        "2022-04-01": "Q2 2022",
    }
    for index, row in df.iterrows():
        st.write(
            "{}: **{:.2f}€**".format(
                quarters_dict[str(row["date"]).split()[0]], row["price"]
            )
        )


if __name__ == "__main__":
    postal_code, housing_type = user_input_features()
    if check_validity_of_postal_code(postal_code):
        st.subheader("Results")
        st.write(
            f"Prediction price (EUR/m2) for **{postal_code}** and **{housing_type}** for the next four quarters:\n"
        )
        df = get_predictions_df(postal_code, housing_type)
        display_results_in_table(df)
        st.subheader("Price development")
        fig = df.plot(y="price", x="date").get_figure()
        st.pyplot(fig)
        #st.stop()