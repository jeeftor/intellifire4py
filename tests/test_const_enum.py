"""Low-hanging fruit: Cover enums and constants in const.py."""
from intellifire4py import const

def test_enums_and_constants():
    # Cover version and user agent
    assert isinstance(const.PACKAGE_VERSION, str)
    assert const.USER_AGENT.startswith("intellifire4py/")

    # IntelliFireApiMode
    assert const.IntelliFireApiMode.LOCAL.value == "local"
    assert const.IntelliFireApiMode.CLOUD.value == "cloud"
    assert const.IntelliFireApiMode.NONE.value == "none"

    # IntelliFireCloudPollType
    assert const.IntelliFireCloudPollType.LONG.value == "long"
    assert const.IntelliFireCloudPollType.SHORT.value == "short"

    # IntelliFireErrorCode
    codes = [2, 130, 6, 4, 64, 129, 145, 132, 133, 134, 144, 3269, 642]
    for code in codes:
        assert const.IntelliFireErrorCode(code)
    # Enum names
    for name in dir(const.IntelliFireErrorCode):
        if not name.startswith("__"):
            getattr(const.IntelliFireErrorCode, name, None)
