FROM python:3.11.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=5000
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:$PORT", "app:app"]

