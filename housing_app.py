import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pgeocode


st.write(
"""
# 🏠 Housing Price Prediction App


Investors can now predict housing price movement in Finland using artificial intelligence with this new real estate investing tool.

The aim of the tool is to work as a complement to traditional real estate investing which mainly relies on local knowledge and human-driven research.
Application uses big data based on historic data with machine-learning algorithms to forecast the future trend of property prices so you will be one step ahead in your investment decision.

Input your values and test now!

**Disclaimer: At the moment application predicts 2021 Q2 prices for testing purposes.**
"""
)

nomi = pgeocode.Nominatim("fi")


def preprocess_input(postal_code, housing_type):
    # Encode categorical values to one hot encoding and postal code to geolocational data (latitude, longitude)

    quarter = "2021-01-04"
    geolocation = nomi.query_postal_code([postal_code])
    latitude, longitude = (
        geolocation["latitude"].iloc[0],
        geolocation["longitude"].iloc[0],
    )
    if pd.isnull(latitude) or pd.isnull(longitude):
        st.error("Application did not find geolocation for this postal code")
    else:
        cat = np.array([housing_type, quarter]).reshape(1, -1)
        load_encoder = joblib.load("onehot_encoder.pkl")
        features = load_encoder.transform(cat).toarray()
        features = np.append(features, [longitude, latitude]).reshape(1, -1)
        return features


def user_input_features():
    # Streamlit interface's inputs to array for predictions
    postal_code = st.text_input("Postal code")
    housing_type = st.selectbox(
        "Housing type", ("one-room", "two-room", "three or more room", "terrace house")
    )
    return preprocess_input(postal_code, housing_type)


try:
    input_data = user_input_features()
    load_regr = joblib.load("housing_regr.pkl")
    pred = load_regr.predict(input_data)
    st.subheader("Results")
    st.write("Prediction price (EUR/m2) for 2021 Q2: ***${:d}***".format(int(pred)))
except:
    st.stop()
