FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-lock.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir pytest pytest-cov structlog python-json-logger ruff

COPY . .

CMD ["pytest", "--cov=."]
