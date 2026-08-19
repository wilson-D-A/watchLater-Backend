FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

WORKDIR /app/watchLater-api

ENV PORT=8080
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
ENV GOOGLE_APPLICATION_CREDENTIALS=/secrets/key.json

EXPOSE 8080

CMD ["sh", "-c", "uvicorn routes:app --host 0.0.0.0 --port ${PORT:-8080}"]