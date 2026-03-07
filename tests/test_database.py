"""Tests for the database module."""
import pytest
import pytest_asyncio
import asyncio
import os
from database import Database


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.initialize()
    return database


@pytest.mark.asyncio
async def test_initialize(db):
    hosts = await db.get_all_hosts()
    assert hosts == []


@pytest.mark.asyncio
async def test_upsert_and_retrieve(db):
    host = {
        "ip": "192.168.1.10",
        "mac": "AA:BB:CC:DD:EE:FF",
        "vendor": "TestVendor",
        "hostname": "test-host",
        "status": "online",
        "method": "arp",
        "response_time_ms": 1.5,
    }
    await db.upsert_host(host)
    hosts = await db.get_all_hosts()
    assert len(hosts) == 1
    assert hosts[0]["ip"] == "192.168.1.10"
    assert hosts[0]["vendor"] == "TestVendor"


@pytest.mark.asyncio
async def test_delete_host(db):
    host = {
        "ip": "192.168.1.20",
        "mac": "11:22:33:44:55:66",
        "vendor": "Unknown",
        "status": "online",
    }
    await db.upsert_host(host)
    await db.delete_host("192.168.1.20")
    result = await db.get_host("192.168.1.20")
    assert result is None
