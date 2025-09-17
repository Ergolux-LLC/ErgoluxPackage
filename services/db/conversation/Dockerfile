FROM python:3.11-slim

WORKDIR /app

# Install bash and netcat correctly
RUN apt-get update && apt-get install -y bash netcat-openbsd && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy in wait-for-db.sh
COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

CMD ["bash", "/app/wait-for-db.sh", "python", "${ENTRYPOINT}"]
