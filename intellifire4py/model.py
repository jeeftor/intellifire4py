"""Model definitions."""
# pylint: disable=no-member
# pylint: disable=C0115
# pylint: disable=C0116
# pylint: disable=R0903
# pylint: disable=E0611
# flake8: noqa  D101
from typing import List

from pydantic import BaseModel, Field


class IntellifirePollData(BaseModel):
    name: str
    serial: str
    temperature_c: int = Field(alias="temperature")
    battery: int
    pilot_on: bool = Field(alias="pilot")
    light_level: int = Field(alias="light")
    flameheight: int = Field(alias="height")
    fanspeed: int
    is_hot: bool = Field(alias="hot")
    is_on: bool = Field(alias="power")
    thermostat_on: bool = Field(alias="thermostat")
    raw_thermostat_setpoint: int = Field(alias="setpoint")
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
    def thermostat_setpoint_c(self) -> float:
        return self.raw_thermostat_setpoint / 100

    @property
    def thermostat_setpoint_f(self) -> float:
        return (self.raw_thermostat_setpoint / 100 * 9 / 5) + 32


class UDPResponse(BaseModel):
    mac: str
    bssid: str
    channel: int
    ip: str
    ssid: str
    rssi: int
    remote_terminal_port: int
    time: int
    version: str
    uuid: str


class IntellifireLocationDetails(BaseModel):
    location_id: str
    location_name: str
    wifi_essid: str
    wifi_password: str
    postal_code: str
    user_class: int


class IntellifireLocations(BaseModel):
    locations: List[IntellifireLocationDetails]
    email_notifications_enabled: int


class IntellifireFireplace(BaseModel):
    serial: str
    brand: str
    name: str
    apikey: str
    power: str


class IntellifireFireplaces(BaseModel):
    location_name: str
    fireplaces: List[IntellifireFireplace]
