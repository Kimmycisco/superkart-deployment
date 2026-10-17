import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Create the Flask app
superkart_api = Flask("SuperKart Sales Predictor")

# Load the saved pipeline (preprocessing and model together)
model = joblib.load("superkart_model.joblib")

# Input columns the model expects
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area",
    "Product_MRP", "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API"


# Online inference: one JSON record in, one prediction out
@superkart_api.post("/v1/predict")
def predict_sales():
    data = request.get_json()
    sample = pd.DataFrame([data])[FEATURES]
    prediction = float(model.predict(sample)[0])
    return jsonify({"Predicted Sales": round(prediction, 2)})


# Batch inference: a CSV file in, one prediction per row out
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    file = request.files["file"]
    batch = pd.read_csv(file)[FEATURES]
    predictions = model.predict(batch)
    return jsonify({str(i): round(float(p), 2) for i, p in zip(batch.index, predictions)})


if __name__ == "__main__":
    superkart_api.run(debug=False)
