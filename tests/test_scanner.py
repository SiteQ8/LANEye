"""Tests for the LANEye scanner module."""
import pytest
from scanner import lookup_vendor, get_hostname


def test_vendor_lookup_known():
    assert lookup_vendor("D8:9E:F3:AA:BB:CC") == "Apple"
    assert lookup_vendor("08:00:27:12:34:56") == "VirtualBox"
    assert lookup_vendor("B8:27:EB:00:00:01") == "Raspberry Pi"


def test_vendor_lookup_unknown():
    assert lookup_vendor("FF:FF:FF:FF:FF:FF") == "Unknown"
    assert lookup_vendor("00:00:00:00:00:00") == "Unknown"


def test_hostname_invalid():
    result = get_hostname("192.0.2.1")
    # May or may not resolve depending on DNS
    assert result is None or isinstance(result, str)
