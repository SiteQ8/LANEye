"""Network Scanner Module"""
import asyncio
from scapy.all import ARP, Ether, srp

class NetworkScanner:
    def __init__(self):
        self.scanning = False

    async def scan_network(self, subnet="192.168.1.0/24"):
        """Scan network for hosts"""
        hosts = []
        arp = ARP(pdst=subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        result = srp(packet, timeout=3, verbose=0)[0]

        for sent, received in result:
            hosts.append({
                'ip': received.psrc,
                'mac': received.hwsrc,
                'status': 'online'
            })

        return hosts
