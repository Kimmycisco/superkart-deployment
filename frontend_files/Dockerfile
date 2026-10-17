FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the app and the dependencies file into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit listens on port 8501
EXPOSE 8501

# Start the Streamlit app, reachable from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
