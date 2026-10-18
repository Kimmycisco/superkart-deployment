FROM python:3.11-slim

WORKDIR /app

# Install required Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application and trained model
COPY app.py superkart_model.joblib ./

# Expose the backend API port
EXPOSE 7860

# Start the Flask application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "app:superkart_api"]
