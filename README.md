# 🔍 LANEye - Lightweight Network IP Scanner

[![GitHub stars](https://img.shields.io/github/stars/SiteQ8/laneye?style=social)](https://github.com/SiteQ8/laneye/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**LANEye** is a lightweight, powerful, and reliable network IP scanner with a modern web GUI. Designed for system administrators, security professionals, and network enthusiasts who need real-time visibility into their network infrastructure.

🌐 **[Live Demo](https://siteq8.github.io/laneye/dashboard.html)** | 📚 **[Documentation](https://siteq8.github.io/laneye/)** | 🐛 **[Report Bug](https://github.com/SiteQ8/laneye/issues)**

## ✨ Features

### 🚀 Core Features
- **Real-time Network Discovery**: Automatic ARP and ICMP-based host detection
- **Host Inventory Management**: Persistent database of all discovered devices with MAC, IP, vendor info
- **Online/Offline Monitoring**: Continuous monitoring with historical status tracking
- **Beautiful Web GUI**: Modern, responsive React interface with Tailwind CSS
- **Smart Notifications**: Multi-channel alerts (Telegram, Email, Slack, Discord, Webhooks)

### 📊 Integrations
- **ELK Stack**: Export scan data to Elasticsearch for advanced analytics
- **Grafana/Prometheus**: Built-in metrics endpoint for beautiful dashboards
- **InfluxDB Support**: Time-series data export for long-term analysis
- **Webhook Integration**: Custom integrations with your existing tools

### 🔐 Security & Reliability
- Docker-first deployment for isolation and portability
- SQLite/PostgreSQL database support
- WebSocket real-time updates
- RESTful API for automation
- Comprehensive logging

## 📸 Screenshots

### Dashboard
![Dashboard](https://siteq8.github.io/laneye/dashboard.html)

### Host Inventory
Beautiful, searchable table of all network devices with real-time status updates.

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/SiteQ8/laneye.git
cd laneye

# Start LANEye with Docker Compose
docker-compose up -d

# Access the web interface
open http://localhost:8000
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure settings
cp config.yaml.example config.yaml
nano config.yaml

# Start the backend
uvicorn laneye.main:app --host 0.0.0.0 --port 8000

# Start the frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## 📋 Requirements

- Python 3.8+
- Docker & Docker Compose (optional but recommended)
- Network interface with packet capture capabilities
- Root/Administrator privileges for network scanning

## ⚙️ Configuration

Edit `config.yaml` to customize LANEye:

```yaml
# Network Scanning
scanning:
  interface: eth0
  subnet: 192.168.1.0/24
  interval: 60  # seconds

# Notifications
notifications:
  enabled: true
  channels:
    - telegram
    - webhook
  telegram:
    bot_token: YOUR_BOT_TOKEN
    chat_id: YOUR_CHAT_ID

# ELK Integration
elk:
  enabled: true
  elasticsearch_url: http://localhost:9200
  index_name: laneye-hosts
```

## 📊 Grafana Dashboard

LANEye exposes Prometheus metrics at `/metrics`:

- `laneye_hosts_total` - Total discovered hosts
- `laneye_hosts_online` - Online hosts count
- `laneye_hosts_offline` - Offline hosts count

Import our [Grafana dashboard template](docs/grafana-dashboard.json) for instant visualization.

## 🔔 Notification Channels

LANEye supports multiple notification methods:

### Telegram
```yaml
telegram:
  bot_token: YOUR_BOT_TOKEN
  chat_id: YOUR_CHAT_ID
```

### Webhook
```yaml
webhook:
  url: https://your-webhook-url.com/alert
```

### Email (SMTP)
```yaml
email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  username: your-email@gmail.com
  password: your-app-password
  recipients:
    - admin@example.com
```

## 🛠️ API Documentation

### Get All Hosts
```bash
GET /api/hosts
```

### Trigger Manual Scan
```bash
POST /api/scan
Content-Type: application/json

{
  "interface": "eth0",
  "subnet": "192.168.1.0/24"
}
```

### Export to ELK
```bash
POST /api/export/elk
```

### Prometheus Metrics
```bash
GET /metrics
```

Full API documentation: [API Docs](https://siteq8.github.io/laneye/api-docs.html)

## 🐳 Docker Deployment

### Standalone Container
```bash
docker run -d \
  --name laneye \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  -v $(pwd)/data:/data \
  -e INTERFACE=eth0 \
  siteq8/laneye:latest
```

### With Full ELK Stack
See [docker-compose.yml](docker-compose.yml) for complete deployment with Elasticsearch, Kibana, Grafana, and Prometheus.

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/WebSocket
┌──────▼──────┐
│  React GUI  │
└──────┬──────┘
       │ REST API
┌──────▼──────┐      ┌──────────────┐
│   FastAPI   │◄────►│   Database   │
│   Backend   │      │ (SQLite/PG)  │
└──────┬──────┘      └──────────────┘
       │
       ├──────► Network Scanner (ARP/ICMP)
       │
       ├──────► Notification System
       │
       └──────► Exporters (ELK/Grafana)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Changelog

### v1.0.0 (2025-10-18)
- Initial release
- Network scanning with ARP/ICMP
- Web GUI dashboard
- Host inventory management
- Multi-channel notifications
- ELK and Grafana integration
- Docker support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**SiteQ8**
- Email: site@hotmail.com
- Website: [3li.info](https://3li.info)
- GitHub: [@SiteQ8](https://github.com/SiteQ8)

## 🙏 Acknowledgments

- Inspired by [WatchYourLAN](https://github.com/aceberg/WatchYourLAN)
- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://reactjs.org/), and [Scapy](https://scapy.net/)
- Chart.js for beautiful visualizations
- Tailwind CSS for modern UI

## 🔗 Related Projects

- [PhishGuard](https://github.com/SiteQ8/phishguard) - Phishing detection tool
- [CBK-Scanner](https://github.com/SiteQ8/cbk-scanner) - CBK compliance scanner
- [M365-Defender-Queries](https://github.com/SiteQ8/m365-defender-queries) - M365 hunting queries

## ⭐ Star History

If you find LANEye useful, please consider giving it a star!

---

**Made with ❤️ in Kuwait**
