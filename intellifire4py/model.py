"""Model definitions."""
from __future__ import annotations

from http.cookies import SimpleCookie

try:
    from pydantic.v1 import Field, validator  # type: ignore # noqa F401 # pragma: no cover
    from pydantic.v1 import BaseModel  # type: ignore # pragma: no cover
except ImportError:
    from pydantic import Field  # type: ignore # pragma: no cover
    from pydantic import BaseModel  # type: ignore # pragma: no cover

from .const import IntelliFireErrorCode, IntelliFireApiMode
from aiohttp import CookieJar


class IntelliFirePollData(BaseModel):
    """Base model for IntelliFire status data."""

    battery: int = Field(default=0)
    brand: str = Field(default="unset")
    connection_quality: int = Field(default=0, alias="remote_connection_quality")
    downtime: int = Field(default=0, alias="remote_downtime")
    ecm_latency: int = Field(default=0)
    errors: list[int] = Field(default=[])
    fanspeed: int = Field(default=0)
    flameheight: int = Field(alias="height", default=0)
    fw_ver_str: str = Field(default="unset", alias="firmware_version_string")
    fw_version: str = Field(default="unset", alias="firmware_version")
    has_fan: bool = Field(alias="feature_fan", default=False)
    has_light: bool = Field(alias="feature_light", default=False)
    has_power_vent: bool = Field(alias="power_vent", default=False)
    has_thermostat: bool = Field(alias="feature_thermostat", default=False)
    ipv4_address: str = Field(default="127.0.0.1")
    is_hot: bool = Field(alias="hot", default=False)
    is_on: bool = Field(alias="power", default=False)
    light_level: int = Field(alias="light", default=0)
    name: str = Field(default="unset")  # Not available in local api
    pilot_on: bool = Field(alias="pilot", default=False)
    prepurge: int = Field(default=0)
    raw_thermostat_setpoint: int = Field(alias="setpoint", default=2200)
    serial: str = Field(default="unset")  # Not available in cloud api
    temperature_c: int = Field(alias="temperature", default=18)
    thermostat_on: bool = Field(alias="thermostat", default=False)
    timer_on: bool = Field(alias="timer", default=False)
    timeremaining_s: int = Field(alias="timeremaining", default=0)
    uptime: int = Field(default=0, alias="remote_uptime")

    class Config:
        """Set configuration values for pydantic."""

        # pydantic v1 version (i think)
        populate_by_name = True
        # Pydantic v2 version
        allow_population_by_field_name = True

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
    def error_codes(self) -> list[IntelliFireErrorCode]:
        """Error codes returned as IntelliFireErrroCodes."""
        return [IntelliFireErrorCode(i) for i in self.errors]

    @property
    def error_codes_string(self) -> str:
        """Assembled error codes into a formatted string."""
        return ", ".join([code.name for code in self.error_codes])

    @property
    def error_pilot_flame(self) -> bool:
        """Return whether PILOT_FLAME error is present."""
        return IntelliFireErrorCode.PILOT_FLAME in self.error_codes

    @property
    def error_flame(self) -> bool:
        """Return whether FLAME error is present."""
        return IntelliFireErrorCode.FLAME in self.error_codes

    @property
    def error_fan_delay(self) -> bool:
        """Return whether FAN_DELAY error is present."""
        return IntelliFireErrorCode.FAN_DELAY in self.error_codes

    @property
    def error_maintenance(self) -> bool:
        """Return whether MAINTENANCE error is present."""
        return IntelliFireErrorCode.MAINTENANCE in self.error_codes

    @property
    def error_disabled(self) -> bool:
        """Return whether DISABLED error is present."""
        return IntelliFireErrorCode.DISABLED in self.error_codes

    @property
    def error_fan(self) -> bool:
        """Return whether FAN error is present."""
        return IntelliFireErrorCode.FAN in self.error_codes

    @property
    def error_lights(self) -> bool:
        """Return whether LIGHTS error is present."""
        return IntelliFireErrorCode.LIGHTS in self.error_codes

    @property
    def error_accessory(self) -> bool:
        """Return whether ACCESSORY error is present."""
        return IntelliFireErrorCode.ACCESSORY in self.error_codes

    @property
    def error_soft_lock_out(self) -> bool:
        """Return whether SOFT_LOCK_OUT error is present."""
        return IntelliFireErrorCode.SOFT_LOCK_OUT in self.error_codes

    @property
    def error_ecm_offline(self) -> bool:
        """Return whether ECM_OFFLINE error is present."""
        return IntelliFireErrorCode.ECM_OFFLINE in self.error_codes

    @property
    def error_offline(self) -> bool:
        """Return whether OFFLINE error is present."""
        return IntelliFireErrorCode.OFFLINE in self.error_codes

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


class IntelliFireLocationDetails(BaseModel):
    """Define iftapi.net location details."""

    location_id: str
    location_name: str
    wifi_essid: str
    wifi_password: str
    postal_code: str
    user_class: int


class IntelliFireLocations(BaseModel):
    """Define base model for iftapi.net location."""

    locations: list[IntelliFireLocationDetails]
    email_notifications_enabled: int


class IntelliFireFireplaceCloud(BaseModel):
    """Define base model for individual iftapi.net fireplace."""

    serial: str
    brand: str
    name: str
    apikey: str
    power: str


class IntelliFireFireplaces(BaseModel):
    """Define iftapi.net fireplace list."""

    location_name: str
    fireplaces: list[IntelliFireFireplaceCloud]


class IntelliFireLocationWithFireplaces(BaseModel):
    """Combine location details with associated fireplaces."""

    location: IntelliFireLocationDetails
    fireplaces: list[IntelliFireFireplaceCloud] = []


class IntelliFireCookieData(BaseModel):
    """A data model to hold cookie data specific to IntelliFire system.

    This class is designed to store key cookie data required for user authentication and identification
    in IntelliFire systems. Since Pydantic does not natively handle `httpx.Cookies` objects, this model
    stores the essential cookie fields individually. It includes helper methods to construct and parse
    `httpx.Cookies` objects as needed, facilitating the handling of cookie data in a structured and
    Pydantic-compatible manner.

    Attributes:
        auth_cookie (str | None): The authentication cookie string. Default is None.
        user_id (str | None): The user ID cookie string. Default is None.
        web_client_id (str | None): The web client ID cookie string. Default is None.


    """

    # User authentication and identification information
    auth_cookie: str = "UNSET"
    user_id: str = "UNSET"
    web_client_id: str = "UNSET"

    def parse_cookie_jar(self, cookies: SimpleCookie) -> None:
        """Parses an `aiohttp.CookieJar` object to extract and store key cookie values.

        This method extracts 'user', 'auth_cookie', and 'web_client_id' values from the provided
        `aiohttp.CookieJar` object and stores them in the respective attributes of the class instance.

        Args:
            cookies (SimpleCookie): An `aiohttp.CookieJar` object containing the response cookies.
        """
        self.user_id = cookies.get("user", "UNSET").value  # type: ignore[union-attr]
        self.auth_cookie = cookies.get("auth_cookie", "UNSET").value  # type: ignore[union-attr]
        self.web_client_id = cookies.get("web_client_id", "UNSET").value  # type: ignore[union-attr]

    @property
    def cookie_jar(self) -> CookieJar:
        """Constructs an `aiohttp.CookieJar` object from stored cookie data.

        This method creates and returns an `aiohttp.CookieJar` object, populating it with
        the 'user', 'auth_cookie', and 'web_client_id' values stored in the class instance.

        Returns:
            CookieJar: An `aiohttp.CookieJar` object containing the user's authentication and
                       identification cookies.
        """

        cookie_jar = CookieJar()
        cookie_jar.update_cookies(
            {
                "user": self.user_id,
                "auth_cookie": self.auth_cookie,
                "web_client_id": self.web_client_id,
            }
        )
        return cookie_jar


class IntelliFireCommonFireplaceData(IntelliFireCookieData):
    """A single class that represents the required Cloud and Local Parameters for control."""

    ip_address: str = "UNSET"
    api_key: str = "UNSET"
    serial: str = "UNSET"

    # Existing modes should be stored in here i guess
    read_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL
    control_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL


class IntelliFireUserData(IntelliFireCookieData):
    """FirePlace data associated with a specific User on iftapi.net.

    This class stores a list of the users's fireplaces, their credentials, and the cookie information needed to access them
    """

    fireplaces: list[IntelliFireCommonFireplaceData] = []

    username: str | None = None
    password: str | None = None

    def get_data_for_serial(self, serial: str) -> IntelliFireCommonFireplaceData | None:
        """Retrieve fireplace data based on the provided serial number.

        This method uses a generator expression with `next` to find the first matching fireplace,
        which is more efficient than looping through all fireplaces.

        Args:
            serial (str): The serial number of the fireplace to search for.

        Returns:
            IntelliFireCommonFireplaceData | None: Fireplace data if found, None otherwise.
        """
        return next((fp for fp in self.fireplaces if fp.serial == serial), None)

    def get_data_for_ip(self, ip_address: str) -> IntelliFireCommonFireplaceData | None:
        """Retrieve fireplace data based on the provided ip address.

        This method uses a generator expression with `next` to find the first matching fireplace,
        which is more efficient than looping through all fireplaces.

        Args:
            ip_address (str): The serial number of the fireplace to search for.

        Returns:
            IntelliFireCommonFireplaceData | None: Fireplace data if found, None otherwise.
        """
        return next((fp for fp in self.fireplaces if fp.ip_address == ip_address), None)
