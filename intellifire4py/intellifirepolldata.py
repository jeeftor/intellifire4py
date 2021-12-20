from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class IntellifirePollData(BaseModel):
    name: str
    serial: str
    temperature: int
    battery: int
    pilot: int
    light: int
    height: int = Field(alias="flameheight")
    fanspeed: int
    hot: int
    power: int
    thermostat: int
    setpoint: int
    timer: int
    timeremaining: int
    prepurge: int
    feature_light: int
    feature_thermostat: int
    power_vent: int
    feature_fan: int
    errors: List[int]
    fw_version: str
    fw_ver_str: str
    downtime: int
    uptime: int
    connection_quality: int
    ecm_latency: int
    ipv4_address: str
