
FROM python:3.11-slim

# Set directory for the app in the container
WORKDIR /app

# Set environment variables for the app
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Copy requirements file first for better caching of dependencies
COPY requirements.txt .

# Install Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code into the container
COPY . .

# Create directory for SQLite database if it doesn't exist
RUN mkdir -p /app/data

# Expose port 5000 for the Flask application to listen on
EXPOSE 5000

# Run the Flask application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

