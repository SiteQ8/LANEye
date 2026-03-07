# LANEye Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│              (React GUI / WebSocket)                    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / WS
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌───────────┐  ┌──────────┐  ┌───────────────────┐    │
│  │  REST API  │  │WebSocket │  │ Background Scanner│    │
│  └─────┬─────┘  └────┬─────┘  └────────┬──────────┘    │
│        │              │                  │               │
│  ┌─────▼──────────────▼──────────────────▼───────┐      │
│  │              Core Scanner Engine              │      │
│  │         (ARP + ICMP + Vendor Lookup)          │      │
│  └─────────────────────┬─────────────────────────┘      │
│                        │                                │
│  ┌─────────┐  ┌───────▼────┐  ┌──────────────────┐     │
│  │SQLite DB│  │Notification│  │    Exporters      │     │
│  │         │  │  Manager   │  │ ELK/Prom/InfluxDB │     │
│  └─────────┘  └────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────┘

Components:
- Scanner:        ARP/ICMP network scanning (scapy)
- Backend:        FastAPI REST API + WebSocket
- Database:       Async SQLite with history tracking
- Notifications:  Telegram, Slack, Discord, Email, Webhooks
- Exporters:      Elasticsearch, Prometheus, InfluxDB
- Frontend:       React + Tailwind CSS (or GitHub Pages demo)
```

Author: **SiteQ8** (site@hotmail.com) · Website: [3li.info](https://3li.info)
