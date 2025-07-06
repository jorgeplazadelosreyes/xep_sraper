FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && \
  apt-get install -y wget gnupg libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 curl && \
  rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium --with-deps

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
