"""
LANEye - Network Scanner Module
================================
ARP and ICMP-based host discovery with vendor identification,
async scanning, and rate-limited probing.

Author: SiteQ8 (site@hotmail.com)
License: MIT
"""

import asyncio
import logging
import time
import socket
from datetime import datetime, timezone
from typing import List, Dict, Optional

from scapy.all import ARP, Ether, srp, IP, ICMP, sr1, conf

logger = logging.getLogger("laneye.scanner")

# Common OUI prefixes → vendor names
OUI_DATABASE: Dict[str, str] = {
    "00:50:56": "VMware", "00:0C:29": "VMware",
    "00:1A:A0": "Dell", "00:25:B5": "Dell",
    "D8:9E:F3": "Apple", "A4:83:E7": "Apple",
    "AC:DE:48": "Apple", "F0:18:98": "Apple",
    "B8:27:EB": "Raspberry Pi", "DC:A6:32": "Raspberry Pi",
    "00:15:5D": "Microsoft Hyper-V",
    "00:E0:4C": "Realtek", "52:54:00": "QEMU/KVM",
    "08:00:27": "VirtualBox",
    "00:1A:2B": "Cisco", "00:1B:54": "Cisco",
    "30:B5:C2": "TP-Link", "50:C7:BF": "TP-Link",
    "04:95:E6": "Google", "54:60:09": "Google",
    "18:D6:C7": "Ubiquiti", "24:A4:3C": "Ubiquiti",
    "94:18:82": "Synology", "00:11:32": "Synology",
    "3C:D9:2B": "HP", "00:1B:78": "HP",
    "20:CF:30": "ASUS", "2C:56:DC": "ASUS",
    "00:E0:FC": "Huawei", "E0:24:7F": "Huawei",
}


def lookup_vendor(mac: str) -> str:
    """Resolve OUI vendor from MAC address."""
    prefix = mac.upper()[:8]
    return OUI_DATABASE.get(prefix, "Unknown")


def get_hostname(ip: str) -> Optional[str]:
    """Reverse DNS lookup for hostname."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return None


class NetworkScanner:
    """
    Asynchronous network scanner using ARP and ICMP probes.

    Supports:
    - ARP-based Layer 2 host discovery
    - ICMP fallback for non-ARP reachable hosts
    - MAC vendor identification via OUI lookup
    - Hostname resolution (reverse DNS)
    - Configurable scan intervals and timeouts
    - Rate limiting to avoid triggering IDS/IPS
    """

    def __init__(
        self,
        subnet: str = "192.168.1.0/24",
        interface: str = "eth0",
        timeout: int = 3,
        retry: int = 1,
        rate_limit: float = 0.01,
    ):
        self.subnet = subnet
        self.interface = interface
        self.timeout = timeout
        self.retry = retry
        self.rate_limit = rate_limit
        self.scanning = False
        self._last_scan: Optional[datetime] = None
        self._scan_count: int = 0
        self._hosts_cache: List[Dict] = []

    async def arp_scan(self, subnet: Optional[str] = None) -> List[Dict]:
        """
        Perform ARP scan on the given subnet.
        Returns list of hosts with IP, MAC, vendor, hostname.
        """
        target = subnet or self.subnet
        logger.info(f"Starting ARP scan on {target} via {self.interface}")

        try:
            conf.verb = 0
            packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target)

            answered, _ = srp(
                packet,
                timeout=self.timeout,
                retry=self.retry,
                iface=self.interface,
                verbose=0,
            )

            hosts = []
            for sent, received in answered:
                mac = received.hwsrc.upper()
                ip = received.psrc
                vendor = lookup_vendor(mac)
                hostname = get_hostname(ip)

                hosts.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor,
                    "hostname": hostname,
                    "status": "online",
                    "method": "arp",
                    "last_seen": datetime.now(timezone.utc).isoformat(),
                    "response_time_ms": round(
                        (received.time - sent.sent_time) * 1000, 2
                    ),
                })

                if self.rate_limit > 0:
                    await asyncio.sleep(self.rate_limit)

            logger.info(f"ARP scan complete: {len(hosts)} hosts found")
            return hosts

        except PermissionError:
            logger.error("ARP scan requires root/admin privileges")
            raise
        except Exception as e:
            logger.error(f"ARP scan failed: {e}")
            return []

    async def icmp_scan(self, targets: List[str]) -> List[Dict]:
        """ICMP ping scan for hosts not reachable via ARP."""
        logger.info(f"Starting ICMP scan on {len(targets)} targets")
        hosts = []

        for target_ip in targets:
            try:
                start = time.time()
                reply = sr1(
                    IP(dst=target_ip) / ICMP(),
                    timeout=self.timeout,
                    verbose=0,
                )
                elapsed = (time.time() - start) * 1000

                if reply is not None:
                    hosts.append({
                        "ip": target_ip,
                        "mac": "N/A",
                        "vendor": "Unknown",
                        "hostname": get_hostname(target_ip),
                        "status": "online",
                        "method": "icmp",
                        "last_seen": datetime.now(timezone.utc).isoformat(),
                        "response_time_ms": round(elapsed, 2),
                    })

                if self.rate_limit > 0:
                    await asyncio.sleep(self.rate_limit)

            except Exception as e:
                logger.debug(f"ICMP scan failed for {target_ip}: {e}")

        logger.info(f"ICMP scan complete: {len(hosts)} hosts found")
        return hosts

    async def scan_network(self, subnet: Optional[str] = None) -> List[Dict]:
        """Full network scan combining ARP + ICMP."""
        self.scanning = True
        scan_start = time.time()

        try:
            hosts = await self.arp_scan(subnet)

            arp_ips = {h["ip"] for h in hosts}
            base = (subnet or self.subnet).split("/")[0].rsplit(".", 1)[0]
            gateway_candidates = [
                f"{base}.{s}" for s in ["1", "254"]
                if f"{base}.{s}" not in arp_ips
            ]

            if gateway_candidates:
                hosts.extend(await self.icmp_scan(gateway_candidates))

            hosts.sort(key=lambda h: tuple(int(p) for p in h["ip"].split(".")))

            self._hosts_cache = hosts
            self._last_scan = datetime.now(timezone.utc)
            self._scan_count += 1

            duration = round(time.time() - scan_start, 2)
            logger.info(
                f"Scan #{self._scan_count} done in {duration}s — "
                f"{len(hosts)} hosts"
            )
            return hosts

        finally:
            self.scanning = False

    @property
    def stats(self) -> Dict:
        return {
            "is_scanning": self.scanning,
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "scan_count": self._scan_count,
            "cached_hosts": len(self._hosts_cache),
            "subnet": self.subnet,
            "interface": self.interface,
        }
