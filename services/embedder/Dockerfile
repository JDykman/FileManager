# services/embedder/Dockerfile

# --- Stage 1: Build the Python application ---
FROM python:3.12.4-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY services/embedder/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime Image ---
FROM python:3.12.4-slim-bullseye

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --no-create-home --ingroup appgroup appuser
USER appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY services/embedder/src ./src

CMD ["python", "src/main.py"]