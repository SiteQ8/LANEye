"""Notification System"""
import aiohttp

class NotificationManager:
    def __init__(self):
        self.config = {}

    async def send(self, message):
        """Send notification"""
        print(f"Notification: {message}")

    async def send_telegram(self, message):
        """Send Telegram notification"""
        pass
