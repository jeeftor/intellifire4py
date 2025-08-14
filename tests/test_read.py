"""Test IntelliFireDataProvider and related read logic for intellifire4py."""

from datetime import datetime
from intellifire4py.read import IntelliFireDataProvider
from intellifire4py.model import IntelliFirePollData


class DummyProvider(IntelliFireDataProvider):
    """Dummy provider for testing."""

    @property
    def data(self):
        """Return dummy poll data."""
        return self._data

    @property
    def is_polling_in_background(self):
        """Return polling status."""
        return False

    async def start_background_polling(self, minimum_wait_in_seconds: int = 15) -> None:
        """Mock start background polling."""
        self._polling_started = True

    async def stop_background_polling(self) -> bool:
        """Mock stop background polling."""
        self._polling_started = False
        return True


def test_init_and_last_poll():
    """Test initialization and last_poll_utc property."""
    provider = DummyProvider()
    assert isinstance(provider._data, IntelliFirePollData)
    assert provider.last_poll_utc is None
    now = datetime.utcnow()
    provider._last_poll = now
    assert provider.last_poll_utc == now
    # data property returns the _data instance
    assert isinstance(provider.data, IntelliFirePollData)
