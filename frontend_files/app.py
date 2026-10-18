
import os
import io

import pandas as pd
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SuperKart Sales Forecast",
    page_icon="🛒",
    layout="wide"
)

# Configurable Flask backend address
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:7860"
).rstrip("/")

REQUIRED_FEATURES = [
    "Product_Weight",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Age_Years",
    "Product_Sugar_Content",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Product_Type_Category"
]

st.title("SuperKart Sales Forecast")

st.write(
    "Predict product-level sales revenue using "
    "the trained Random Forest regression model."
)

# -------------------------------
# Single Prediction
# -------------------------------

st.header("Single prediction")

with st.form("single_prediction_form"):

    left, right = st.columns(2)

    with left:
        product_weight = st.number_input(
            "Product weight",
            min_value=0.0,
            value=12.66,
            format="%.2f"
        )

        sugar_content = st.selectbox(
            "Product sugar content",
            ["Low Sugar", "Regular", "No Sugar"]
        )

        allocated_area = st.number_input(
            "Product allocated area",
            min_value=0.0,
            max_value=1.0,
            value=0.027,
            format="%.3f"
        )

        product_mrp = st.number_input(
            "Product MRP",
            min_value=0.0,
            value=117.08,
            format="%.2f"
        )

        product_prefix = st.selectbox(
            "Product ID prefix",
            ["FD", "NC", "DR"]
        )

    with right:
        product_category = st.selectbox(
            "Product type category",
            ["Perishables", "Non Perishables"]
        )

        store_size = st.selectbox(
            "Store size",
            ["Small", "Medium", "High"],
            index=1
        )

        city_type = st.selectbox(
            "Store city type",
            ["Tier 1", "Tier 2", "Tier 3"],
            index=1
        )

        store_type = st.selectbox(
            "Store type",
            [
                "Departmental Store",
                "Supermarket Type1",
                "Supermarket Type2",
                "Food Mart"
            ],
            index=2
        )

        store_age = st.number_input(
            "Store age (years)",
            min_value=0,
            value=16,
            step=1
        )

    predict_single = st.form_submit_button(
        "Predict sales"
    )

if predict_single:

    payload = {
        "Product_Weight": float(product_weight),
        "Product_Allocated_Area": float(allocated_area),
        "Product_MRP": float(product_mrp),
        "Store_Age_Years": int(store_age),
        "Product_Sugar_Content": sugar_content,
        "Store_Size": store_size,
        "Store_Location_City_Type": city_type,
        "Store_Type": store_type,
        "Product_Id_char": product_prefix,
        "Product_Type_Category": product_category
    }

    try:
        response = requests.post(
            BACKEND_URL + "/v1/predict",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            prediction = response.json()["Predicted Sales"]

            st.success(
                f"Predicted sales: {prediction:,.2f}"
            )

        else:
            try:
                message = response.json().get(
                    "error",
                    "Prediction request failed."
                )
            except ValueError:
                message = response.text

            st.error(
                f"API error ({response.status_code}): "
                f"{message}"
            )

    except requests.exceptions.RequestException as error:
        st.error(
            "Could not connect to the Flask prediction API. "
            "Verify that the backend is running and "
            "BACKEND_URL is configured correctly."
        )


# -------------------------------
# Batch Prediction
# -------------------------------

st.header("Batch prediction")

st.write(
    "Upload a CSV file containing the 10 required "
    "model input columns."
)

with st.form("batch_prediction_form"):

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    predict_batch = st.form_submit_button(
        "Predict for the file"
    )

if predict_batch:

    if uploaded_file is None:
        st.warning("Please upload a CSV file.")

    else:
        try:
            file_bytes = uploaded_file.getvalue()

            batch_df = pd.read_csv(
                io.BytesIO(file_bytes)
            )

            if batch_df.empty:
                st.error("The uploaded CSV file is empty.")

            else:
                missing_columns = [
                    column
                    for column in REQUIRED_FEATURES
                    if column not in batch_df.columns
                ]

                if missing_columns:
                    st.error(
                        "Missing required columns: "
                        + ", ".join(missing_columns)
                    )

                else:
                    response = requests.post(
                        BACKEND_URL + "/v1/predictbatch",
                        files={
                            "file": (
                                uploaded_file.name,
                                file_bytes,
                                "text/csv"
                            )
                        },
                        timeout=60
                    )

                    if response.status_code == 200:

                        predictions = response.json()

                        results = pd.DataFrame(
                            [
                                {
                                    "Row": int(row),
                                    "Predicted Sales": value
                                }
                                for row, value in predictions.items()
                            ]
                        ).sort_values("Row")

                        results = results.reset_index(drop=True)

                        st.success(
                            f"Successfully predicted "
                            f"{len(results)} records."
                        )

                        st.dataframe(
                            results,
                            use_container_width=True,
                            hide_index=True
                        )

                        csv_output = results.to_csv(
                            index=False
                        ).encode("utf-8")

                        st.download_button(
                            "Download predictions",
                            data=csv_output,
                            file_name="superkart_predictions.csv",
                            mime="text/csv"
                        )

                    else:
                        try:
                            message = response.json().get(
                                "error",
                                "Batch prediction failed."
                            )
                        except ValueError:
                            message = response.text

                        st.error(
                            f"API error ({response.status_code}): "
                            f"{message}"
                        )

        except requests.exceptions.RequestException:
            st.error(
                "Could not connect to the Flask prediction API. "
                "Verify that the backend is running."
            )

        except (ValueError, pd.errors.ParserError) as error:
            st.error(
                f"Unable to process the CSV file: {error}"
            )
