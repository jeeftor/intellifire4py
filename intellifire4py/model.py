"""Model definitions."""
from pydantic import BaseModel, Field

from intellifire4py.const import IntellifireErrorCode


class IntellifirePollData(BaseModel):
    """Base model for Intellifire status data."""

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
    errors: list[int]
    fw_version: str
    fw_ver_str: str
    downtime: int
    uptime: int
    connection_quality: int
    ecm_latency: int
    ipv4_address: str

    @property
    def temperature_f(self) -> float:
        """Return temperature in fahrenheit."""
        return (self.temperature_c * 9 / 5) + 32

    @property
    def thermostat_setpoint_c(self) -> float:
        """Thermostat set point in celsius."""
        return self.raw_thermostat_setpoint / 100

    @property
    def thermostat_setpoint_f(self) -> float:
        """Thermostat setpoint in fahrenheit."""
        return (self.raw_thermostat_setpoint / 100 * 9 / 5) + 32

    @property
    def error_codes(self) -> list[IntellifireErrorCode]:
        """Error codes returned as IntellifireErrroCodes."""
        return [IntellifireErrorCode(i) for i in self.errors]

    @property
    def error_codes_string(self) -> str:
        """Assembled error codes into a formatted string."""
        return ", ".join([code.name for code in self.error_codes])

    @property
    def error_pilot_flame(self) -> bool:
        """Return whether PILOT_FLAME error is present."""
        return IntellifireErrorCode.PILOT_FLAME in self.error_codes

    @property
    def error_flame(self) -> bool:
        """Return whether FLAME error is present."""
        return IntellifireErrorCode.FLAME in self.error_codes

    @property
    def error_fan_delay(self) -> bool:
        """Return whether FAN_DELAY error is present."""
        return IntellifireErrorCode.FAN_DELAY in self.error_codes

    @property
    def error_maintenance(self) -> bool:
        """Return whether MAINTENANCE error is present."""
        return IntellifireErrorCode.MAINTENANCE in self.error_codes

    @property
    def error_disabled(self) -> bool:
        """Return whether DISABLED error is present."""
        return IntellifireErrorCode.DISABLED in self.error_codes

    @property
    def error_fan(self) -> bool:
        """Return whether FAN error is present."""
        return IntellifireErrorCode.FAN in self.error_codes

    @property
    def error_lights(self) -> bool:
        """Return whether LIGHTS error is present."""
        return IntellifireErrorCode.LIGHTS in self.error_codes

    @property
    def error_accessory(self) -> bool:
        """Return whether ACCESSORY error is present."""
        return IntellifireErrorCode.ACCESSORY in self.error_codes

    @property
    def error_soft_lock_out(self) -> bool:
        """Return whether SOFT_LOCK_OUT error is present."""
        return IntellifireErrorCode.SOFT_LOCK_OUT in self.error_codes

    @property
    def error_ecm_offline(self) -> bool:
        """Return whether ECM_OFFLINE error is present."""
        return IntellifireErrorCode.ECM_OFFLINE in self.error_codes

    @property
    def error_offline(self) -> bool:
        """Return whether OFFLINE error is present."""
        return IntellifireErrorCode.OFFLINE in self.error_codes

    @property
    def has_errors(self) -> bool:
        """If there is any errors this will be true."""
        return len(self.error_codes) > 0


class UDPResponse(BaseModel):
    """Define response from UDP discovery."""

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
    """Define iftapi.net location details."""

    location_id: str
    location_name: str
    wifi_essid: str
    wifi_password: str
    postal_code: str
    user_class: int


class IntellifireLocations(BaseModel):
    """Define base model for iftapi.net location."""

    locations: list[IntellifireLocationDetails]
    email_notifications_enabled: int


class IntellifireFireplace(BaseModel):
    """Define base model for individual iftapi.net fireplace."""

    serial: str
    brand: str
    name: str
    apikey: str
    power: str


class IntellifireFireplaces(BaseModel):
    """Define iftapi.net fireplace list."""

    location_name: str
    fireplaces: list[IntellifireFireplace]
