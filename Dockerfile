# Imagem Docker do backend job-sync (FastAPI).

FROM python:3.12-slim

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

COPY src/ ./src/
RUN mkdir -p /app/storage

ENV PYTHONPATH=src
ENV DATABASE_PATH=storage/job_sync.db
ENV PORT=8000
ENV HOST=0.0.0.0
ENV LOG_LEVEL=info

EXPOSE 8000

CMD ["uvicorn", "jobsync.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
