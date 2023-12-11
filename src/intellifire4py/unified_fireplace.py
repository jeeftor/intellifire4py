"""Unified Fireplace Object encapsulating both Local and Cloud."""
from __future__ import annotations

import asyncio
import logging

from httpx import ConnectError

from intellifire4py import IntelliFireAPILocal, IntelliFireAPICloud
from intellifire4py.const import IntelliFireApiMode
from intellifire4py.control import IntelliFireController
from intellifire4py.model import (
    IntelliFireCommonFireplaceData,
    IntelliFirePollData,
    IntelliFireUserData,
)
from rich import inspect

from intellifire4py.read import IntelliFireDataProvider

from typing import cast
from typing import Any
from collections.abc import Coroutine


class UnifiedFireplace:
    """Unified Fireplace Object encapsulating both Local and Cloud control and data access.

    This class acts as a wrapper around both local and cloud interfaces for an IntelliFire fireplace,
    providing unified access to control and read data irrespective of the underlying connection mode.
    It abstracts the complexity of handling two different APIs and offers a simple interface for
    controlling and monitoring the fireplace.
    """

    log: logging.Logger = logging.getLogger(__name__)
    _control_mode: IntelliFireApiMode
    _read_mode: IntelliFireApiMode
    # Data of importance
    _fireplace_data: IntelliFireCommonFireplaceData

    # API Variables
    _local_api: IntelliFireAPILocal
    _cloud_api: IntelliFireAPICloud

    cloud_connectivity: bool | None = None
    local_connectivity: bool | None = None

    def __init__(
        self,
        fireplace_data: IntelliFireCommonFireplaceData,
        read_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        control_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        use_http: bool = False,
        verify_ssl: bool = True,
    ):
        """Initializes a new instance of the UnifiedFireplace class, configuring it for both local and cloud interactions with an IntelliFire fireplace.

        This constructor sets up the UnifiedFireplace object with essential data and configurations required for interfacing with an IntelliFire fireplace system. It establishes the modes for reading data and controlling the fireplace, and it initializes the local and cloud API interfaces using the provided fireplace data.

        Args:
            fireplace_data (IntelliFireCommonFireplaceData): Essential data for interacting with the fireplace, including details like serial number, IP address, user ID, API key, and cookies.
            read_mode (IntelliFireApiMode, optional): Specifies the mode for reading data (LOCAL for local network, CLOUD for cloud). Defaults to LOCAL.
            control_mode (IntelliFireApiMode, optional): Determines how the fireplace is controlled (LOCAL for local network, CLOUD for cloud). Defaults to LOCAL.
            use_http (bool, optional): Indicates whether to use HTTP (True) or HTTPS (False) for communication. Defaults to False (HTTPS).
            verify_ssl (bool, optional): Toggles SSL certificate verification. Defaults to True (verification enabled).

        The constructor prepares two API interfaces:
            - _local_api (IntelliFireAPILocal): Configured for direct local network communication, using the IP address, user ID, and API key from the fireplace_data.
            - _cloud_api (IntelliFireAPICloud): Set up for cloud-based interactions, using the serial number and cookies from the fireplace_data.

        These interfaces enable the UnifiedFireplace class to seamlessly manage and interact with IntelliFire fireplaces, simplifying the complexity of handling different APIs and connection modes.
        """
        self._control_mode = control_mode
        self._read_mode = read_mode

        self._fireplace_data = fireplace_data

        self._verify_ssl = verify_ssl
        self._use_http = use_http

        self._local_api: IntelliFireAPILocal = IntelliFireAPILocal(
            fireplace_ip=self.ip_address, user_id=self.user_id, api_key=self.api_key
        )

        self._cloud_api = IntelliFireAPICloud(
            serial=self.serial,
            cookies=self._fireplace_data.cookies,
            verify_ssl=verify_ssl,
            use_http=use_http,
        )

    async def perform_cloud_poll(self) -> None:
        """Perform a Cloud Poll - this should be used to validate the stored credentials."""
        await self._cloud_api.poll()

    async def perform_local_poll(self) -> None:
        """Perform a local Poll - used to test local connectivity."""
        await self._local_api.poll()

    @property
    def dump_user_data_json(self) -> str:
        """Dump the internal _fireplace_data object to a JSON String."""
        return self._fireplace_data.model_dump_json()

    @property
    def ip_address(self) -> str:
        """Retrieves the IP address associated with the fireplace.

        This property returns the IP address stored in the '_fireplace_data' attribute
        of the class instance. The IP address is used for Local control.

        Returns:
            str: The IP address of the fireplace.
        """
        return self._fireplace_data.ip_address

    @property
    def api_key(self) -> str:
        """Retrieves the API key from the fireplace data.

        This property is used to access the 'api_key' stored in the '_fireplace_data'
        attribute. The API key is typically used for authentication when making
        API calls related to the fireplace system.

        Returns:
            str: The API key for the fireplace.
        """
        return self._fireplace_data.api_key

    @property
    def serial(self) -> str:
        """Retrieves the serial number of the fireplace.

        This property returns the serial number associated with the fireplace.
        The serial number is stored in the '_fireplace_data' attribute of the class instance.

        Returns:
            str: The serial number of the fireplace.
        """
        return self._fireplace_data.serial

    @property
    def user_id(self) -> str:
        """Retrieves the user ID from the fireplace data cookie.

        This property accesses the 'user_id' stored within the cookie attribute
        of the '_fireplace_data'. It's useful for identifying the user associated
        with the current fireplace instance.

        Returns:
        str: The user ID extracted from the fireplace data cookie.
        """
        return self._fireplace_data.user_id

    @property
    def auth_cookie(self) -> str:
        """Retrieves the authentication cookie from the fireplace data.

        This property is used to obtain the 'auth_cookie' from the cookie attribute
        of the '_fireplace_data'. It is typically used for authentication purposes.

        Returns:
            str: The authentication cookie value.
        """
        return self._fireplace_data.auth_cookie

    @property
    def web_client_id(self) -> str:
        """Retrieves the web client ID from the fireplace data cookie.

        This property fetches the 'web_client_id' from the cookie attribute
        of the '_fireplace_data'. The web client ID can be used for tracking or
        identification purposes in web-related operations.

        Returns:
            str: The web client ID extracted from the fireplace data cookie.
        """
        return self._fireplace_data.web_client_id

    @property
    def read_api(self) -> IntelliFireDataProvider:
        """Returns the appropriate read API based on the current read mode.

        This method chooses between the local or cloud API for reading the fireplace,
        depending on the value of '_read_mode'. This abstraction allows for seamless switching
        between local and cloud control without affecting the rest of the codebase.
        """

        # Due to how python handles inheritance we probably need to cast the stuff
        # in order to suppress errors that may/may-not actually exist at all
        # This could however break stuff I think

        api = (
            self._local_api
            if self._read_mode == IntelliFireApiMode.LOCAL
            else self._cloud_api
        )

        return cast(IntelliFireDataProvider, api)

    @property
    def control_api(self) -> IntelliFireController:
        """Returns the appropriate control API based on the current control mode.

        This method chooses between the local or cloud API for controlling the fireplace,
        depending on the value of '_control_mode'. This abstraction allows for seamless switching
        between local and cloud control without affecting the rest of the codebase.
        """
        return (
            self._local_api
            if self._control_mode == IntelliFireApiMode.LOCAL
            else self._cloud_api
        )

    @property
    def read_mode(self) -> IntelliFireApiMode:
        """Returns the current read mode of the fireplace instance.

        This property provides access to the current mode used for reading data from the fireplace,
        which can be either local or cloud mode. It enables external entities to query the current
        read mode configuration of the fireplace.
        """
        return self._read_mode

    async def set_read_mode(self, mode: IntelliFireApiMode) -> None:
        """Sets the read mode of the fireplace instance.

        This method allows dynamically changing the read mode between local and cloud.
        It also handles the necessary setup or teardown operations needed when switching
        between these modes.
        """
        self.log.debug("Changing READ mode: %s=>%s", self._read_mode.name, mode.name)
        if self._read_mode == mode:
            self.log.info("Not updating mode -- it was the same")
            return

        try:
            await self._switch_read_mode(mode)
        except Exception as e:
            self.log.error(f"Error switching read mode: {e}")

    async def _switch_read_mode(self, mode: IntelliFireApiMode) -> None:
        """Internal helper method to switch the read mode.

        This method performs the actual switching of read modes. It stops background polling
        on the current API, updates the data, and then starts polling on the new API based on the
        selected mode. It's designed to be an internal method, not exposed externally.
        """
        if mode == IntelliFireApiMode.LOCAL:
            await self._cloud_api.stop_background_polling()
            self._local_api.overwrite_data(self._cloud_api.data)
            await self._local_api.start_background_polling()
        else:
            await self._local_api.stop_background_polling()
            self._cloud_api.overwrite_data(self._local_api.data)
            await self._cloud_api.start_background_polling()
        self._read_mode = mode
        self._fireplace_data.read_mode = mode

    @property
    def control_mode(self) -> IntelliFireApiMode:
        """Reads the current control mode of the fireplace instance.

        This property provides access to the current mode used for controlling the fireplace,
        allowing external entities to understand how the fireplace is currently being controlled
        (locally or through the cloud).
        """
        return self._control_mode

    async def set_control_mode(self, mode: IntelliFireApiMode) -> None:
        """Sets the control mode of the fireplace instance.

        This method allows dynamically changing the control mode between local and cloud.
        It updates the '_control_mode' property to reflect the new mode.
        """
        self.log.debug(
            "Changing CONTROL mode: %s=>%s", self._control_mode.name, mode.name
        )
        self._control_mode = mode
        self._fireplace_data.control_mode = mode

    @property
    def _cloud_data(self) -> IntelliFirePollData:
        """Provides access to the cloud data associated with the fireplace.

        This internal property encapsulates access to data retrieved from the cloud API,
        presenting a unified view of the cloud data to the rest of the class.
        """
        return self._cloud_api.data

    @property
    def _local_data(self) -> IntelliFirePollData:
        """Provides access to the local data associated with the fireplace.

        This internal property encapsulates access to data retrieved from the local API,
        presenting a unified view of the local data to the rest of the class.
        """
        return self._local_api.data

    @property
    def data(self) -> IntelliFirePollData:
        """Retrieves the IntelliFirePoll data based on the current read mode.

        This property dynamically returns the IntelliFirePoll data,
        choosing between local or cloud-based data depending on the current
        setting of the 'read_mode' attribute.

        If the 'read_mode' is set to 'IntelliFireApiMode.LOCAL', it fetches
        the data from '_local_data', which is assumed to be the locally stored
        IntelliFire data. This might be preferred when the fireplace is
        accessible within a local network or for privacy reasons.

        On the other hand, if 'read_mode' is set to any other value,
        the method defaults to returning data from '_cloud_data'. This implies
        that the data is fetched from a cloud service, which could be the
        case when remote access or additional cloud-based services are involved.

        Returns:
            IntelliFirePollData: The current IntelliFire poll data,
            either from local storage or cloud, based on the read mode.
        """
        if self.read_mode == IntelliFireApiMode.LOCAL:
            return self._local_data
        else:
            return self._cloud_data

    @classmethod
    async def create_async_instance(
        cls,
        fireplace_data: IntelliFireCommonFireplaceData,
        read_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        control_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        use_http: bool = False,
        verify_ssl: bool = True,
    ) -> UnifiedFireplace:
        """Asynchronously creates an instance of the class with specified fireplace data and operating modes.

        This class method facilitates the asynchronous instantiation of the class, initializing it
        with given fireplace data, read mode, and control mode. It also ensures that the instance
        is properly set up with the specified read mode before it's returned for use.

        Args:
            fireplace_data (IntelliFireCommonFireplaceData): Data related to the fireplace, necessary
                for initializing the instance. This includes details like IP address, serial number,
                user ID, API key, etc.
            read_mode (IntelliFireApiMode, optional): The mode of reading data from the fireplace, either
                local or cloud. Defaults to IntelliFireApiMode.LOCAL.
            control_mode (IntelliFireApiMode, optional): The mode of controlling the fireplace, either
                local or cloud. Defaults to IntelliFireApiMode.LOCAL.
            use_http (bool, optional): Indicates whether to use HTTP (True) or HTTPS (False) for communication.
            verify_ssl (bool, optional): Toggles SSL certificate verification.

        Returns:
            [cls]: An initialized instance of the class with the specified configuration.
        """
        instance = cls(
            fireplace_data,
            read_mode,
            control_mode,
            verify_ssl=verify_ssl,
            use_http=use_http,
        )
        await instance._switch_read_mode(instance._read_mode)
        return instance

    @classmethod
    async def build_fireplace_from_common_data(
        cls,
        common_data: IntelliFireCommonFireplaceData,
        use_http: bool = False,
        verify_ssl: bool = True,
    ) -> UnifiedFireplace:
        """Asynchronously constructs a UnifiedFireplace instance from a given IntelliFireCommonFireplaceData object, including network security settings.

        This method serves as a factory for creating UnifiedFireplace instances. It takes a pre-defined IntelliFireCommonFireplaceData object and uses it to instantiate a new UnifiedFireplace object, including SSL and HTTP configuration.

        Args:
            common_data (IntelliFireCommonFireplaceData): An object containing essential fireplace data.
            use_http (bool, optional): Indicates whether to use HTTP or HTTPS for communication.
            verify_ssl (bool, optional): Determines whether SSL certificate verification is enabled.

        Returns:
            UnifiedFireplace: A fully initialized instance of UnifiedFireplace.
        """
        return await cls.create_async_instance(common_data)

    @classmethod
    async def build_fireplaces_from_user_data(
        cls,
        user_data: IntelliFireUserData,
        read_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        control_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        use_http: bool = False,
        verify_ssl: bool = True,
    ) -> list[UnifiedFireplace]:
        """Builds a list of UnifiedFireplace instances from IntelliFireUserData.

        This method takes user data, which includes a list of fireplace data,
        and creates a UnifiedFireplace instance for each item in the list.

        Args:
            user_data (IntelliFireUserData): User data containing a list of fireplace data.
            read_mode (IntelliFireApiMode, optional): The mode of reading data from the fireplace, either
                local or cloud. Defaults to IntelliFireApiMode.LOCAL.
            control_mode (IntelliFireApiMode, optional): The mode of controlling the fireplace, either
                local or cloud. Defaults to IntelliFireApiMode.LOCAL.
            use_http (bool, optional): Indicates whether to use HTTP or HTTPS for communication.
            verify_ssl (bool, optional): Determines whether SSL certificate verification is enabled.


        Returns:
            list[UnifiedFireplace]: A list of UnifiedFireplace instances.
        """

        tasks = [
            cls.create_async_instance(
                fp,
                read_mode=read_mode,
                control_mode=control_mode,
            )
            for fp in user_data.fireplaces
        ]
        return await asyncio.gather(*tasks)

    @classmethod
    async def build_fireplace_direct(
        cls,
        ip_address: str,
        api_key: str,
        serial: str,
        auth_cookie: str,
        user_id: str,
        web_client_id: str,
        read_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        control_mode: IntelliFireApiMode = IntelliFireApiMode.LOCAL,
        use_http: bool = False,
        verify_ssl: bool = True,
    ) -> UnifiedFireplace:
        """Asynchronously constructs a UnifiedFireplace instance with direct input parameters.

        This class method allows for creating a UnifiedFireplace instance by directly providing
        the individual components of the fireplace data such as IP address, API key, serial number,
        authentication cookie, user ID, and web client ID. It's useful when the data components
        are available separately and need to be compiled into a common fireplace data structure
        before instantiating the UnifiedFireplace object.

        Args:
            ip_address (str): The IP address of the IntelliFire fireplace.
            api_key (str): The API key for accessing the fireplace's functionalities.
            serial (str): The serial number of the fireplace.
            auth_cookie (str): The authentication cookie for accessing the fireplace's functionalities.
            user_id (str): The user ID associated with the fireplace.
            web_client_id (str): The web client ID for accessing the fireplace's functionalities.
            read_mode (IntelliFireApiMode, optional): The mode of reading data from the fireplace, either
                local or cloud. Defaults to IntelliFireApiMode.LOCAL.
            control_mode (IntelliFireApiMode, optional): The mode of controlling the fireplace, either
                local or cloud. Defaults to IntelliFireApiMode.LOCAL.
            use_http (bool, optional): Indicates whether to use HTTP or HTTPS for communication.
            verify_ssl (bool, optional): Determines whether SSL certificate verification is enabled.


        Returns:
            UnifiedFireplace: An instance of the UnifiedFireplace class initialized with the provided data.
        """

        common_fireplace = IntelliFireCommonFireplaceData(
            ip_address=ip_address,
            api_key=api_key,
            serial=serial,
            auth_cookie=auth_cookie,
            user_id=user_id,
            web_client_id=web_client_id,
            read_mode=read_mode,
            control_mode=control_mode,
        )

        return await cls.create_async_instance(common_fireplace)

    @classmethod
    async def build_fireplace_from_common(
        cls,
        common_fireplace: IntelliFireCommonFireplaceData,
        use_http: bool = False,
        verify_ssl: bool = True,
    ) -> UnifiedFireplace:
        """Asynchronously creates a UnifiedFireplace instance from a common fireplace data structure.

        This class method is intended to simplify the instantiation of a UnifiedFireplace object
        when all the necessary data is already encapsulated in an IntelliFireCommonFireplaceData object.
        It serves as a convenient way to create a UnifiedFireplace instance without the need to
        individually pass all the data components.

        Args:
            common_fireplace (IntelliFireCommonFireplaceData): A pre-constructed common fireplace data
            object containing all necessary details for the fireplace.
            use_http (bool, optional): Indicates whether to use HTTP or HTTPS for communication.
            verify_ssl (bool, optional): Determines whether SSL certificate verification is enabled.

        Returns:
            UnifiedFireplace: An instance of the UnifiedFireplace class initialized with the given common fireplace data.
        """
        return await cls.create_async_instance(
            common_fireplace, use_http=use_http, verify_ssl=verify_ssl
        )

    def debug(self) -> None:
        """Utility method to output detailed debugging information.

        This method leverages the 'rich' library to print an inspection of the current
        class instance, including its methods and properties. It is especially useful
        for debugging purposes to understand the state of an object in a rich, readable format.
        """
        inspect(self, methods=True, help=True)

    async def async_validate_connectivity(
        self, timeout: int = 600
    ) -> tuple[bool, bool]:
        """Asynchronously validate connectivity for both local and cloud services.

        This function checks the connectivity status for local and cloud services
        by awaiting on two asynchronous tasks. Each task has a specified timeout,
        after which it is considered unsuccessful.

        Parameters:
        timeout (int): The maximum time in seconds to wait for each connectivity check.

        Returns:
        tuple[bool, bool]: A tuple containing two boolean values. The first boolean
                           indicates the success of the local connectivity check,
                           and the second indicates the success of the cloud connectivity check.
        """

        async def with_timeout(coroutine: Coroutine[Any, Any, Any]) -> bool:
            """Helper function to run a coroutine with a timeout.

            If the coroutine does not complete within the specified timeout,
            or if a ConnectError is raised, it returns False. Otherwise, it returns True.

            Parameters:
            coroutine: The coroutine to be executed with a timeout.

            Returns:
            bool: True if the coroutine completes successfully within the timeout, False otherwise.
            """
            try:
                await asyncio.wait_for(coroutine, timeout)
                return True
            except asyncio.TimeoutError:
                return False
            except ConnectError:
                return False

        # Initiate asynchronous connectivity checks for local and cloud.
        local_future = with_timeout(self.perform_local_poll())
        cloud_future = with_timeout(self.perform_cloud_poll())

        # Await the completion of both connectivity checks.
        local_success, cloud_success = await asyncio.gather(local_future, cloud_future)

        # Update instance variables with the results of the connectivity checks.
        self.cloud_connectivity = cloud_success
        self.local_connectivity = local_success

        # Return the results of the connectivity checks.
        return local_success, cloud_success
