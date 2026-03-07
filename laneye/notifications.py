"""
LANEye - Notification System
==============================
Multi-channel alerting: Telegram, Slack, Discord, Email, Webhooks.

Author: SiteQ8 (site@hotmail.com)
License: MIT
"""

import logging
import smtplib
from email.mime.text import MIMEText
from typing import Dict, List, Optional

import aiohttp

logger = logging.getLogger("laneye.notifications")


class NotificationManager:
    """Send alerts through multiple channels."""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", False)
        self.channels: List[str] = self.config.get("channels", [])

    async def broadcast(self, message: str):
        """Send a message to all configured channels."""
        if not self.enabled:
            return
        for channel in self.channels:
            try:
                handler = getattr(self, f"send_{channel}", None)
                if handler:
                    await handler(message)
                else:
                    logger.warning(f"Unknown channel: {channel}")
            except Exception as e:
                logger.error(f"Notification failed [{channel}]: {e}")

    async def send_telegram(self, message: str):
        cfg = self.config.get("telegram", {})
        token = cfg.get("bot_token")
        chat_id = cfg.get("chat_id")
        if not token or not chat_id:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
            })
        logger.info("Telegram notification sent")

    async def send_slack(self, message: str):
        url = self.config.get("slack", {}).get("webhook_url")
        if not url:
            return
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"text": message})
        logger.info("Slack notification sent")

    async def send_discord(self, message: str):
        url = self.config.get("discord", {}).get("webhook_url")
        if not url:
            return
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"content": message})
        logger.info("Discord notification sent")

    async def send_webhook(self, message: str):
        url = self.config.get("webhook", {}).get("url")
        if not url:
            return
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={
                "source": "laneye",
                "message": message,
            })
        logger.info("Webhook notification sent")

    async def send_email(self, message: str):
        cfg = self.config.get("email", {})
        smtp_host = cfg.get("smtp_host")
        smtp_port = cfg.get("smtp_port", 587)
        username = cfg.get("username")
        password = cfg.get("password")
        to_addr = cfg.get("to")
        from_addr = cfg.get("from", username)

        if not all([smtp_host, username, password, to_addr]):
            return

        msg = MIMEText(message)
        msg["Subject"] = "🔍 LANEye Alert"
        msg["From"] = from_addr
        msg["To"] = to_addr

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.sendmail(from_addr, [to_addr], msg.as_string())
            logger.info("Email notification sent")
        except Exception as e:
            logger.error(f"Email send failed: {e}")
