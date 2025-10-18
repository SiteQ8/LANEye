# Deployment Guide

## Docker Compose

```bash
docker-compose up -d
```

## Manual

```bash
pip install -r requirements.txt
uvicorn laneye.main:app --host 0.0.0.0 --port 8000
```

Access: http://localhost:8000
