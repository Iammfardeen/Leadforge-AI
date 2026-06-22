# LeadForge AI — Backend (FastAPI)
FROM python:3.11-slim

WORKDIR /app

# System deps needed by weasyprint (PDF rendering) and playwright (screenshots)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright's browser binary — needed once the screenshot feature is wired up
RUN playwright install --with-deps chromium || true

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
