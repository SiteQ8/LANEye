FROM python:3.11-slim

LABEL maintainer="SiteQ8 <site@hotmail.com>"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY laneye/ ./laneye/
COPY config.yaml .

RUN mkdir -p /data

EXPOSE 8000

CMD ["uvicorn", "laneye.main:app", "--host", "0.0.0.0", "--port", "8000"]
