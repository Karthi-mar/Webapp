FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces (Docker Space type) expects the container to listen on
# port 7860 -- app.py's app.run() is already configured to bind to it.
EXPOSE 7860

CMD ["python", "app.py"]
