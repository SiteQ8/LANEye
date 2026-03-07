"""
LANEye - Main FastAPI Application
===================================
REST API + WebSocket server for real-time network monitoring.

Author: SiteQ8 (site@hotmail.com)
License: MIT
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional

import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from scanner import NetworkScanner
from database import Database
from notifications import NotificationManager
from exporters import ELKExporter, PrometheusExporter

logger = logging.getLogger("laneye")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f) or {}
    return {}

config = load_config()

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class HostResponse(BaseModel):
    ip: str
    mac: str
    vendor: str
    hostname: Optional[str] = None
    status: str = "online"
    method: str = "arp"
    last_seen: str = ""
    response_time_ms: float = 0.0
    first_seen: Optional[str] = None
    notes: Optional[str] = None

class ScanRequest(BaseModel):
    subnet: Optional[str] = None

class NotificationConfig(BaseModel):
    channel: str
    enabled: bool = True
    config: dict = {}

class StatsResponse(BaseModel):
    total_hosts: int = 0
    online_hosts: int = 0
    offline_hosts: int = 0
    last_scan: Optional[str] = None
    scan_count: int = 0
    uptime_seconds: float = 0

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

scanner = NetworkScanner(
    subnet=config.get("scanning", {}).get("subnet", "192.168.1.0/24"),
    interface=config.get("scanning", {}).get("interface", "eth0"),
    timeout=config.get("scanning", {}).get("timeout", 3),
)
db = Database(config.get("database", {}).get("path", "laneye.db"))
notifier = NotificationManager(config.get("notifications", {}))
elk_exporter = ELKExporter(config.get("elk", {}))
prom_exporter = PrometheusExporter()

connected_clients: List[WebSocket] = []
start_time = datetime.now(timezone.utc)
scan_task: Optional[asyncio.Task] = None

# ---------------------------------------------------------------------------
# Background scanner
# ---------------------------------------------------------------------------

async def background_scan_loop():
    interval = config.get("scanning", {}).get("interval", 60)
    while True:
        try:
            hosts = await scanner.scan_network()
            previous = await db.get_all_hosts()
            prev_ips = {h["ip"] for h in previous}

            new_hosts = [h for h in hosts if h["ip"] not in prev_ips]
            gone_hosts = [h for h in previous if h["ip"] not in {x["ip"] for x in hosts}]

            for host in hosts:
                await db.upsert_host(host)
            for host in gone_hosts:
                await db.update_host_status(host["ip"], "offline")

            if new_hosts:
                msg = f"🟢 {len(new_hosts)} new host(s) detected:\n"
                for h in new_hosts:
                    msg += f"  • {h['ip']} ({h['vendor']}) {h.get('hostname') or ''}\n"
                await notifier.broadcast(msg)

            if gone_hosts:
                msg = f"🔴 {len(gone_hosts)} host(s) went offline:\n"
                for h in gone_hosts:
                    msg += f"  • {h['ip']}\n"
                await notifier.broadcast(msg)

            # Export
            if config.get("elk", {}).get("enabled"):
                await elk_exporter.export(hosts)

            prom_exporter.update(hosts)

            # Push to WebSocket clients
            payload = {
                "type": "scan_complete",
                "hosts": hosts,
                "stats": {
                    "total": len(hosts),
                    "online": len([h for h in hosts if h["status"] == "online"]),
                    "new": len(new_hosts),
                    "offline": len(gone_hosts),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            for ws in connected_clients[:]:
                try:
                    await ws.send_json(payload)
                except Exception:
                    connected_clients.remove(ws)

        except Exception as e:
            logger.error(f"Background scan error: {e}")

        await asyncio.sleep(interval)

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scan_task
    await db.initialize()
    scan_task = asyncio.create_task(background_scan_loop())
    logger.info("LANEye started — background scanner active")
    yield
    if scan_task:
        scan_task.cancel()
    logger.info("LANEye shutting down")

app = FastAPI(
    title="LANEye",
    description="Lightweight Network IP Scanner with Web GUI",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend if available
if os.path.isdir("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html><head><title>LANEye</title></head>
    <body style="font-family:sans-serif;display:flex;align-items:center;
    justify-content:center;height:100vh;background:#0a0f1c;color:#00e5a0">
    <div style="text-align:center">
    <h1>🔍 LANEye v1.1.0</h1>
    <p>Network Scanner API is running</p>
    <p><a href="/docs" style="color:#00e5a0">API Documentation →</a></p>
    </div></body></html>
    """

@app.get("/api/hosts", response_model=List[HostResponse])
async def get_hosts(
    status: Optional[str] = Query(None, description="Filter: online|offline"),
    vendor: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("ip", description="Sort: ip|mac|vendor|last_seen"),
):
    hosts = await db.get_all_hosts()
    if status:
        hosts = [h for h in hosts if h.get("status") == status]
    if vendor:
        hosts = [h for h in hosts if vendor.lower() in h.get("vendor", "").lower()]
    return hosts

@app.get("/api/hosts/{ip}", response_model=HostResponse)
async def get_host(ip: str):
    host = await db.get_host(ip)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host

@app.post("/api/scan")
async def trigger_scan(req: ScanRequest = ScanRequest()):
    if scanner.scanning:
        raise HTTPException(status_code=409, detail="Scan already in progress")
    hosts = await scanner.scan_network(req.subnet)
    for host in hosts:
        await db.upsert_host(host)
    return {"status": "complete", "hosts_found": len(hosts), "hosts": hosts}

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    hosts = await db.get_all_hosts()
    online = [h for h in hosts if h.get("status") == "online"]
    return StatsResponse(
        total_hosts=len(hosts),
        online_hosts=len(online),
        offline_hosts=len(hosts) - len(online),
        last_scan=scanner.stats.get("last_scan"),
        scan_count=scanner.stats.get("scan_count", 0),
        uptime_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
    )

@app.get("/api/scanner/status")
async def scanner_status():
    return scanner.stats

@app.delete("/api/hosts/{ip}")
async def delete_host(ip: str):
    await db.delete_host(ip)
    return {"status": "deleted", "ip": ip}

@app.get("/metrics")
async def prometheus_metrics():
    return HTMLResponse(
        content=prom_exporter.generate(),
        media_type="text/plain",
    )

@app.get("/api/export/{format}")
async def export_data(format: str):
    hosts = await db.get_all_hosts()
    if format == "json":
        return JSONResponse(content=hosts)
    elif format == "csv":
        lines = ["ip,mac,vendor,hostname,status,last_seen"]
        for h in hosts:
            lines.append(
                f"{h['ip']},{h['mac']},{h['vendor']},"
                f"{h.get('hostname','')},{h['status']},{h['last_seen']}"
            )
        return HTMLResponse(content="\n".join(lines), media_type="text/csv")
    raise HTTPException(status_code=400, detail="Supported formats: json, csv")

# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    logger.info(f"WebSocket client connected ({len(connected_clients)} total)")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "scan":
                hosts = await scanner.scan_network()
                await websocket.send_json({"type": "scan_complete", "hosts": hosts})
            elif data == "stats":
                await websocket.send_json({"type": "stats", **scanner.stats})
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected ({len(connected_clients)} total)")

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.1.0",
        "uptime_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
    }
