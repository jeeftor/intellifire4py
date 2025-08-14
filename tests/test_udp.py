"""Test UDP discovery and protocol for intellifire4py."""

import asyncio
import json
import pytest
from unittest import mock
from intellifire4py.udp import (
    IFTDiscoveryReaderProtocol,
    IFTDiscoverySenderProtocol,
    UDPFireplaceFinder,
)


@pytest.mark.asyncio
async def test_ift_discovery_reader_protocol_adds_ip():
    """Test that IFTDiscoveryReaderProtocol adds discovered IPs."""
    ip_set = set()
    protocol = IFTDiscoveryReaderProtocol(timeout=5, ip_set=ip_set)
    # Simulate receiving a valid datagram
    data = json.dumps({"ip": "192.168.1.100"}).encode()  # NOSONAR
    addr = ("192.168.1.100", 55555)  # NOSONAR
    protocol.datagram_received(data, addr)
    assert "192.168.1.100" in ip_set  # NOSONAR


def test_ift_discovery_reader_protocol_connection_methods():
    """Test connection_made and connection_lost methods for reader protocol."""
    ip_set = set()
    protocol = IFTDiscoveryReaderProtocol(timeout=5, ip_set=ip_set)
    transport = mock.Mock()
    protocol.connection_made(transport)
    protocol.connection_lost(None)  # Should not raise


def test_ift_discovery_sender_protocol_sends_message():
    """Test that IFTDiscoverySenderProtocol sends a message."""
    message = "test message"
    on_con_lost = mock.Mock()
    protocol = IFTDiscoverySenderProtocol(message, on_con_lost)
    transport = mock.Mock()
    sock = mock.Mock()
    transport.get_extra_info.return_value = sock
    protocol.connection_made(transport)
    # Ensure sendto was called with the correct arguments
    transport.sendto.assert_called_with(message.encode(), ("255.255.255.255", 3785))


def test_ift_discovery_sender_protocol_error_and_close():
    """Test error and close handling for sender protocol."""
    protocol = IFTDiscoverySenderProtocol("msg", None)
    protocol.transport = mock.Mock()
    # Should log a warning but not raise
    protocol.error_received(Exception("err"))
    protocol.connection_lost(None)


@pytest.mark.asyncio
async def test_udp_fireplace_finder_ips_and_init():
    """Test UDPFireplaceFinder initialization and IPs property."""
    finder = UDPFireplaceFinder(timeout_in_seconds=1)
    assert finder.ips == []
    finder.ip_set.add("1.2.3.4")  # NOSONAR
    assert finder.ips == ["1.2.3.4"]  # NOSONAR


@pytest.mark.asyncio
async def test_udp_fireplace_finder_send_discovery_packet(monkeypatch):
    """Test sending of UDP discovery packet."""
    finder = UDPFireplaceFinder(timeout_in_seconds=1)
    loop = mock.Mock()
    monkeypatch.setattr(finder, "loop", loop)
    loop.create_datagram_endpoint = mock.AsyncMock(
        return_value=(mock.Mock(), mock.Mock())
    )
    fut = asyncio.Future()
    fut.set_result(True)
    loop.create_future = mock.Mock(return_value=fut)
    await finder.send_discovery_packet()
    loop.create_datagram_endpoint.assert_called()


@pytest.mark.asyncio
async def test_udp_fireplace_finder_search_fireplace(monkeypatch):
    """Test searching for fireplace via UDPFireplaceFinder."""
    finder = UDPFireplaceFinder(timeout_in_seconds=1)
    # Patch send_discovery_packet and start_discovery_reader
    monkeypatch.setattr(finder, "send_discovery_packet", mock.AsyncMock())
    monkeypatch.setattr(finder, "start_discovery_reader", mock.AsyncMock())
    result = await finder.search_fireplace(timeout=1)
    assert isinstance(result, list)
