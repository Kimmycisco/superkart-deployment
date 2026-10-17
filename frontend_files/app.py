import os
import requests
import pandas as pd
import streamlit as st

# Address of the Flask backend (the container name on the Docker network)
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales of a product in a store.")

# Single prediction
st.subheader("Single prediction")

col1, col2 = st.columns(2)
with col1:
    weight = st.number_input("Product weight", 4.0, 22.0, 12.65, step=0.01)
    sugar = st.selectbox("Product sugar content", ["Low Sugar", "Regular", "No Sugar"])
    area = st.number_input(
        "Product allocated area", 0.004, 0.3, 0.056, step=0.001, format="%.3f"
    )
    mrp = st.number_input("Product MRP", 31.0, 266.0, 147.0, step=0.01)
    id_char = st.selectbox("Product ID prefix", ["FD", "NC", "DR"])
with col2:
    category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])
    size = st.selectbox("Store size", ["Small", "Medium", "High"])
    city = st.selectbox("Store city type", ["Tier 1", "Tier 2", "Tier 3"])
    store_type = st.selectbox(
        "Store type",
        ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"],
    )
    age = st.number_input("Store age (years)", 1, 60, 16, step=1)

ERROR_UNREACHABLE = "Could not reach the prediction API."

if st.button("Predict sales"):
    payload = {
        "Product_Weight": weight,
        "Product_Sugar_Content": sugar,
        "Product_Allocated_Area": area,
        "Product_MRP": mrp,
        "Store_Size": size,
        "Store_Location_City_Type": city,
        "Store_Type": store_type,
        "Product_Id_char": id_char,
        "Store_Age_Years": int(age),
        "Product_Type_Category": category,
    }
    try:
        url = BACKEND_URL + "/v1/predict"
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            value = response.json()["Predicted Sales"]
            st.success(f"Predicted sales: {value:,.2f}")
        else:
            st.error(f"The API returned an error: {response.status_code}")
    except requests.exceptions.RequestException:
        st.error(ERROR_UNREACHABLE)

# Batch prediction
st.subheader("Batch prediction")
st.write("Upload a CSV file with the same 10 input columns.")
uploaded = st.file_uploader("CSV file", type="csv")

if uploaded is not None and st.button("Predict for the file"):
    try:
        url = BACKEND_URL + "/v1/predictbatch"
        files = {"file": ("batch.csv", uploaded.getvalue())}
        response = requests.post(url, files=files, timeout=60)
        if response.status_code == 200:
            rows = list(response.json().items())
            results = pd.DataFrame(rows, columns=["Row", "Predicted Sales"])
            st.dataframe(results)
        else:
            st.error(f"The API returned an error: {response.status_code}")
    except requests.exceptions.RequestException:
        st.error(ERROR_UNREACHABLE)
