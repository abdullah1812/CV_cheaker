FROM python:3.11.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Let Railway know what port to open (does not set the env var)
EXPOSE 5000

# Use entrypoint so $PORT is passed dynamically from Railway
CMD ["sh", "-c", "python app.py"]
