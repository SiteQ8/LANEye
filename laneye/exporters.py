"""
LANEye - Data Exporters
========================
Export scan data to ELK Stack, Prometheus/Grafana, and InfluxDB.

Author: SiteQ8 (site@hotmail.com)
License: MIT
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp

logger = logging.getLogger("laneye.exporters")


class ELKExporter:
    """Export host data to Elasticsearch."""

    def __init__(self, config: Dict = None):
        config = config or {}
        self.url = config.get("elasticsearch_url", "http://localhost:9200")
        self.index = config.get("index_name", "laneye-hosts")
        self.enabled = config.get("enabled", False)

    async def export(self, hosts: List[Dict]):
        if not self.enabled:
            return

        try:
            async with aiohttp.ClientSession() as session:
                for host in hosts:
                    doc = {
                        **host,
                        "@timestamp": datetime.now(timezone.utc).isoformat(),
                        "source": "laneye",
                    }
                    await session.post(
                        f"{self.url}/{self.index}/_doc",
                        json=doc,
                        headers={"Content-Type": "application/json"},
                    )
            logger.info(f"Exported {len(hosts)} hosts to Elasticsearch")
        except Exception as e:
            logger.error(f"ELK export failed: {e}")

    async def health_check(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(f"{self.url}/_cluster/health")
                return resp.status == 200
        except Exception:
            return False


class PrometheusExporter:
    """Generate Prometheus-compatible metrics."""

    def __init__(self):
        self._total = 0
        self._online = 0
        self._offline = 0
        self._vendors: Dict[str, int] = {}
        self._scan_count = 0
        self._last_scan_duration = 0.0

    def update(self, hosts: List[Dict]):
        self._total = len(hosts)
        self._online = sum(1 for h in hosts if h.get("status") == "online")
        self._offline = self._total - self._online
        self._scan_count += 1

        self._vendors.clear()
        for h in hosts:
            v = h.get("vendor", "Unknown")
            self._vendors[v] = self._vendors.get(v, 0) + 1

    def generate(self) -> str:
        lines = [
            "# HELP laneye_hosts_total Total discovered hosts",
            "# TYPE laneye_hosts_total gauge",
            f"laneye_hosts_total {self._total}",
            "",
            "# HELP laneye_hosts_online Currently online hosts",
            "# TYPE laneye_hosts_online gauge",
            f"laneye_hosts_online {self._online}",
            "",
            "# HELP laneye_hosts_offline Currently offline hosts",
            "# TYPE laneye_hosts_offline gauge",
            f"laneye_hosts_offline {self._offline}",
            "",
            "# HELP laneye_scans_total Total scans performed",
            "# TYPE laneye_scans_total counter",
            f"laneye_scans_total {self._scan_count}",
            "",
            "# HELP laneye_hosts_by_vendor Hosts grouped by vendor",
            "# TYPE laneye_hosts_by_vendor gauge",
        ]
        for vendor, count in self._vendors.items():
            safe = vendor.replace('"', '\\"')
            lines.append(f'laneye_hosts_by_vendor{{vendor="{safe}"}} {count}')

        return "\n".join(lines) + "\n"


class InfluxDBExporter:
    """Export to InfluxDB (line protocol)."""

    def __init__(self, config: Dict = None):
        config = config or {}
        self.url = config.get("url", "http://localhost:8086")
        self.bucket = config.get("bucket", "laneye")
        self.org = config.get("org", "")
        self.token = config.get("token", "")
        self.enabled = config.get("enabled", False)

    async def export(self, hosts: List[Dict]):
        if not self.enabled:
            return

        lines = []
        for h in hosts:
            vendor = h.get("vendor", "Unknown").replace(" ", "\\ ")
            status = 1 if h.get("status") == "online" else 0
            rt = h.get("response_time_ms", 0)
            lines.append(
                f"laneye_host,ip={h['ip']},mac={h['mac']},vendor={vendor} "
                f"status={status},response_time={rt}"
            )

        payload = "\n".join(lines)

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.url}/api/v2/write?bucket={self.bucket}&org={self.org}",
                    data=payload,
                    headers={
                        "Authorization": f"Token {self.token}",
                        "Content-Type": "text/plain",
                    },
                )
            logger.info(f"Exported {len(hosts)} hosts to InfluxDB")
        except Exception as e:
            logger.error(f"InfluxDB export failed: {e}")
