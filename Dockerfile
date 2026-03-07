FROM python:3.12-slim

LABEL maintainer="SiteQ8 <site@hotmail.com>"
LABEL description="LANEye - Lightweight Network IP Scanner"
LABEL version="1.1.0"

WORKDIR /app

# Install network dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpcap-dev \
    tcpdump \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY config.yaml .
COPY frontend/ ./frontend/

RUN mkdir -p /data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
