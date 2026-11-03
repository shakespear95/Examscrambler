# Use a lightweight official Python runtime
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run database creation & seed on build
RUN python seed.py

# Expose port 8080 (standard Fly.io port)
EXPOSE 8080

# Run Gunicorn binding to 0.0.0.0:8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]