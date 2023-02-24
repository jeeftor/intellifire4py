"""IntelliFire abstract read class."""
from __future__ import annotations

from abc import ABC, abstractmethod

from intellifire4py.model import IntelliFirePollData


class IntelliFireDataProvider(ABC):
    """Abstract base class to provide read logic."""

    @property
    @abstractmethod
    def data(self) -> IntelliFirePollData:
        """Return data to the user."""
        return IntelliFirePollData()
