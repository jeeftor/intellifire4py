from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class IntellifirePollData(BaseModel):
    name: str
    serial: str
    temperature_c: int = Field(alias="temperature")
    battery: int
    pilot_on: bool = Field(alias="pilot")
    light_on: bool = Field(alias="light")
    flameheight: int = Field(alias="height")
    fanspeed: int
    is_hot: bool = Field(alias="hot")
    is_on: bool = Field(alias="power")
    thermostat_on: bool = Field(alias="thermostat")
    __thermostat_setpoint: int = Field(alias="setpoint")
    timer_on: bool = Field(alias="timer")
    timeremaining_s: int = Field(alias="timeremaining")
    prepurge: int
    has_light: bool = Field(alias="feature_light")
    has_thermostat: bool = Field(alias="feature_thermostat")
    has_power_vent: bool = Field(alias="power_vent")
    has_fan: bool = Field(alias="feature_fan")
    errors: List[int]
    fw_version: str
    fw_ver_str: str
    downtime: int
    uptime: int
    connection_quality: int
    ecm_latency: int
    ipv4_address: str

    @property
    def temperature_f(self) -> float:
        return (self.temperature_c * 9 / 5) + 32

    @property
    def thermostat_setpoint_c(self) -> int:
        return self.__thermostat_setpoint / 100

    @property
    def thermostat_setpoint_f(self) -> int:
        return (self.__thermostat_setpoint / 100 * 9 / 5) + 32

