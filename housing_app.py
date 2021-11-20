import json
import streamlit as st
import pandas as pd
import numpy as np
import pgeocode
from nearest_postal_code_algo import find_nearest_postal_code


st.write(
    """
# 🏠 Housing Price Prediction App


Investors can now predict housing price movement in Finland using artificial intelligence with this new real estate investing tool.

The aim of the tool is to work as a complement to traditional real estate investing which mainly relies on local knowledge and human-driven research.
Application uses big data based on historic data with machine-learning algorithms to forecast the future trend of property prices so you will be one step ahead in your investment decision.

Input your values and test now!

**Disclaimer: At the moment application predicts 2021 Q3 prices.**
"""
)

nomi = pgeocode.Nominatim("fi")

def get_predictions(postal_code, housing_type):
    # Encode categorical values to one hot encoding and postal code to geolocational data (latitude, longitude)
    housing_type_json = get_json_for_housing_type(housing_type)
    if postal_code in housing_type_json["pred"]:
        return housing_type_json["pred"][postal_code]
    else:
        nearest_postal_code = find_nearest_postal_code(postal_code, housing_type_json)
        st_disclaimer_nearest_postal_code(True, nearest_postal_code, postal_code)
        return housing_type_json["pred"][nearest_postal_code]


def get_json_for_housing_type(housing_type):
    json_dict = {
        "one-room": "one_room_predictions-Prophet.json",
        "two-room": "two_room_predictions-Prophet.json",
        "three or more room": "three_room_predictions-Prophet.json",
        "terrace house": "terraced_houses_predictions-Prophet.json",
    }
    json_file_path = "json_prediction/{}".format(json_dict[housing_type])

    with open(json_file_path, "r") as j:
        contents = json.loads(j.read())
    return contents


def user_input_features():
    # Streamlit interface's inputs to array for predictions
    postal_code = st.text_input("Postal code")
    housing_type = st.selectbox("Housing type", ("one-room", "two-room", "three or more room", "terrace house"))
    return postal_code, housing_type


def st_disclaimer_nearest_postal_code(found_nearest_postal_code=False, nearest_postal_code=None, postal_code=None):
    if found_nearest_postal_code:
        st.write("We didn't find a model for ***{}***. Therefore, we predict with the model which is nearest to this postal code: ***{}***.".format(postal_code, nearest_postal_code))

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


if __name__ == "__main__":
    try:
        postal_code, housing_type = user_input_features()
        if check_validity_of_postal_code(postal_code):
            pred = get_predictions(postal_code, housing_type)
            st.subheader("Results")
            st.write("Prediction price (EUR/m2) for 2021 Q2:")
            st.markdown("#### {:d}€ ####".format(int(pred)))

    except:
        st.stop()
