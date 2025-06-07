# Use an official Python runtime as the base image
FROM python:3.11.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=5000

# Run gunicorn (ensure it's in PATH)
CMD ["sh", "-c", "gunicorn --workers=4 --bind=0.0.0.0:$PORT app:app"]
