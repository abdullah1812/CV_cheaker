# Use an official Python runtime as the base image
FROM python:3.11.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    which gunicorn  # Debug: Check if gunicorn is in PATH

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=5000  # Default to 5000 if not set by Railway

# Run gunicorn with proper port handling
CMD ["sh", "-c", "gunicorn --workers=4 --bind=0.0.0.0:${PORT:-5000} app:app"]
