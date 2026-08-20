FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY static ./static

ENV PUBLIC_DOMAIN=hermestudios.com
ENV LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
ENV HERMES_MAX_INFLIGHT=32
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
