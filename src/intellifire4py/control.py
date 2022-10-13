"""IntelliFire Control Logic."""
from __future__ import annotations

from enum import Enum


class IntelliFireSendMode(Enum):
    """Command send mode config."""

    LOCAL = "local"
    CLOUD = "cloud"
