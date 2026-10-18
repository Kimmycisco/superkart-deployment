
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask
superkart_api = Flask(__name__)

# Load the saved preprocessing and prediction pipeline
MODEL_PATH = Path(__file__).resolve().parent / "superkart_model.joblib"
model = joblib.load(MODEL_PATH)

# Required input features
FEATURES = [
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

@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API"

@superkart_api.post("/v1/predict")
def predict_sales():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    missing = [col for col in FEATURES if col not in data]

    if missing:
        return jsonify({"error": "Missing features: " + ", ".join(missing)}), 400

    try:
        sample = pd.DataFrame([data])[FEATURES]
        prediction = float(model.predict(sample)[0])

        return jsonify({
            "Predicted Sales": round(prediction, 2)
        })

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    uploaded_file = request.files.get("file")

    if uploaded_file is None:
        return jsonify({"error": "A CSV file is required."}), 400

    try:
        batch_data = pd.read_csv(uploaded_file)

        if batch_data.empty:
            return jsonify({"error": "The CSV file is empty."}), 400

        missing = [
            col for col in FEATURES
            if col not in batch_data.columns
        ]

        if missing:
            return jsonify({
                "error": "Missing features: " + ", ".join(missing)
            }), 400

        predictions = model.predict(batch_data[FEATURES])

        results = {
            str(i): round(float(value), 2)
            for i, value in enumerate(predictions)
        }

        return jsonify(results)

    except (ValueError, TypeError, pd.errors.ParserError) as error:
        return jsonify({"error": str(error)}), 400

if __name__ == "__main__":
    superkart_api.run(
        host="0.0.0.0",
        port=7860,
        debug=False
    )
