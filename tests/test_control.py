"""Control Logic Testing."""
from unittest.mock import patch

import pytest

from intellifire4py import IntellifireFireplace
from intellifire4py.control import IntellifireControl
from intellifire4py.exceptions import LoginException


@pytest.mark.asyncio  # type: ignore
async def test_login(mock_aioresponse) -> None:  # type: ignore
    """Test successful login."""
    control = IntellifireControl(fireplace_ip="192.168.1.1")

    login_url = f"{control.prefix}://iftapi.net/a//login"
    # location_url = f"{control.prefix}://iftapi.net/a/enumlocations"
    mock_aioresponse.post(login_url, status=204, headers={"Set-Cookie": "user=beef"})
    with patch(
        "intellifire4py.control.IntellifireControl.get_locations",
        return_value=[{"location_id": "mock_loc"}],
    ), patch(
        "intellifire4py.control.IntellifireControl.get_fireplaces",
        return_value=[
            IntellifireFireplace(
                serial="abcd1234",
                brand="Fakeroonie",
                name="tacoCooker",
                apikey="api1234",
                power="1",
            )
        ],
    ):
        await control.login(username="beef", password="taco")
    assert control.user == "beef"

@pytest.mark.asyncio  # type: ignore
async def test_bad_login(mock_aioresponse) -> None:  # type: ignore
    """Test a login error."""
    control = IntellifireControl(fireplace_ip="192.168.1.1")
    login_url = f"{control.prefix}://iftapi.net/a//login"
    mock_aioresponse.post(login_url, status=400, headers={"Set-Cookie": "user=beef"})

    with pytest.raises(LoginException):
        await control.login(username="beef", password="taco")
