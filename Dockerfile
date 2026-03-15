FROM python:3.11-slim

WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first (better caching)
COPY backend/requirements.txt /app/

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy backend code
COPY backend /app/backend

WORKDIR /app/backend

EXPOSE 8000

CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]