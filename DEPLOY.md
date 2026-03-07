# Deployment Guide

## Quick Start (Docker)

```bash
git clone https://github.com/SiteQ8/LANEye.git
cd LANEye
docker-compose up -d
```

Access the web interface at **http://localhost:8000**

## With Monitoring Stack

```bash
# Includes Prometheus + Grafana
docker-compose --profile monitoring up -d
```

- **Grafana:** http://localhost:3001 (admin/admin)
- **Prometheus:** http://localhost:9090

## With ELK Stack

```bash
docker-compose --profile elk up -d
```

- **Kibana:** http://localhost:5601
- **Elasticsearch:** http://localhost:9200

## Manual Installation

```bash
# Prerequisites: Python 3.9+, libpcap
sudo apt install libpcap-dev

# Install
pip install -r requirements.txt

# Run (requires root for ARP scanning)
sudo uvicorn main:app --host 0.0.0.0 --port 8000
```

## Configuration

Edit `config.yaml` before starting — see comments inline for all options.

## Running as a Service (systemd)

```ini
[Unit]
Description=LANEye Network Scanner
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/laneye
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo cp laneye.service /etc/systemd/system/
sudo systemctl enable laneye
sudo systemctl start laneye
```
