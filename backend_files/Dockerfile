FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the app, the model and the dependencies file into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# The API listens on port 7860
EXPOSE 7860

# Start the Flask app with gunicorn
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:7860", "app:superkart_api"]
