"""Low-hanging fruit: Cover IntelliFireDataProvider in read.py."""
import pytest
from intellifire4py.read import IntelliFireDataProvider
from intellifire4py.model import IntelliFirePollData
from datetime import datetime

class DummyProvider(IntelliFireDataProvider):
    @property
    def data(self):
        return self._data
    @property
    def is_polling_in_background(self):
        return False
    async def start_background_polling(self, minimum_wait_in_seconds: int = 15) -> None:
        self._polling_started = True
    async def stop_background_polling(self) -> bool:
        self._polling_started = False
        return True

def test_init_and_last_poll():
    provider = DummyProvider()
    assert isinstance(provider._data, IntelliFirePollData)
    assert provider.last_poll_utc is None
    now = datetime.utcnow()
    provider._last_poll = now
    assert provider.last_poll_utc == now
    # data property returns the _data instance
    assert isinstance(provider.data, IntelliFirePollData)
