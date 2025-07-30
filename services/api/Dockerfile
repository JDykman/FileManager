# services/api/Dockerfile

# --- Stage 1: Build the Python application (Install dependencies) ---
FROM python:3.12.4-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# The COPY paths are relative to the build context.
# Assuming you run 'docker build .' from the FileManager/ root.
COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime Image ---
FROM python:3.12.4-slim-bookworm
WORKDIR /app

RUN addgroup --system appgroup && adduser --system --no-create-home --ingroup appgroup appuser
USER appuser

# COPY THE LIBRARIES
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# ALSO COPY THE EXECUTABLES (like uvicorn, gunicorn, etc.)
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your application source code
# This will put services/api/src (from host) into /app/src (in container)
COPY services/api/src ./src

EXPOSE 8000

# This CMD is correct, assuming the above fix is in place.
CMD ["uvicorn", "src.process_file:app", "--host", "0.0.0.0", "--port", "8000"]