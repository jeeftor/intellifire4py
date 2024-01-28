"""IntelliFire abstract read class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from .model import IntelliFirePollData


class IntelliFireDataProvider(ABC):
    """Abstract base class to provide read logic."""

    def __init__(self) -> None:
        """Define simple initializer."""
        self._data = IntelliFirePollData()
        self._last_poll: datetime | None = None
        pass

    @property
    def last_poll(self) -> datetime | None:
        """Return the last poll time."""
        return self._last_poll

    @property
    @abstractmethod
    def data(self) -> IntelliFirePollData:
        """Return data to the user."""
        return IntelliFirePollData()

    @property
    @abstractmethod
    def is_polling_in_background(self) -> bool:
        """Return whether api is polling."""
        return False

    @abstractmethod
    async def start_background_polling(self, minimum_wait_in_seconds: int = 15) -> None:
        """Abstract start polling."""
        pass

    @abstractmethod
    async def stop_background_polling(self) -> bool:
        """Abstract stop polling."""
        return False

    def overwrite_data(self, new_data: IntelliFirePollData) -> None:
        """Overwrite existing poll data."""
        self._data = new_data
