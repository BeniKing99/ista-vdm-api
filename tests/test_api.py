"""Tests for the ista VDM API client."""

from datetime import date
from typing import Any

import aiohttp
import pytest

from ista_vdm_api import (
    ConsumptionData,
    IstaVdmAPI,
    IstaVdmAuthError,
    IstaVdmConnectionError,
    IstaVdmError,
)
from ista_vdm_api.api import LOGIN_URL, TOKEN_URL

HEATING_AND_COLD_WATER_CSV = '''Adresse:;Adresse;
LiegenschaftsNr:;123456789;
Nutzer:;"=""User""";
Nutzernummer:;"=""0005""";
ObjektNr Kunde:;"=""""";
Nutzfläche:;79,09;m²
;;
Verbauch;;
;Wärme in;kWh
"=""Dezember 2025""";392,1;kWh
"=""Jänner 2026""";1.204,5;kWh
"=""Februar 2026""";300;kWh
;;
;;
;Kaltwasser in;m³
"=""Dezember 2025""";1,5;m³
"=""Jänner 2026""";2;m³
"=""Februar 2026""";3,25;m³
'''

HEATING_AND_HOT_WATER_CSV = '''Nutzfläche:;56,9;m²
;;
Verbauch;;
;Wärme in;kWh
"=""November 2025""";327,8;kWh
"=""Dezember 2025""";392,1;kWh
;;
;Warmwasser in;m³
"=""November 2025""";0,29;m³
"=""Dezember 2025""";0,26;m³
'''

ALL_SECTIONS_CSV = ''';Wärme in;kWh
"=""März 2026""";10;kWh
;Warmwasser in;m³
"=""März 2026""";0,5;m³
;Kaltwasser in;m³
"=""März 2026""";1,5;m³
;Strom in;kWh
"=""März 2026""";999;kWh
'''


def _by_month(records: list[ConsumptionData]) -> dict[tuple[int, int], ConsumptionData]:
    return {(r.period_start.year, r.period_start.month): r for r in records}


def test_parse_cold_water_does_not_overwrite_heating() -> None:
    """Cold water rows must land in their own field, not in heating."""
    api = IstaVdmAPI("user@example.com", "secret")
    records = _by_month(api._parse_csv(HEATING_AND_COLD_WATER_CSV))

    assert len(records) == 3
    assert records[(2025, 12)].heating_consumption == 392.1
    assert records[(2026, 1)].heating_consumption == 1204.5
    assert records[(2026, 2)].heating_consumption == 300

    assert records[(2025, 12)].cold_water_consumption == 1.5
    assert records[(2026, 1)].cold_water_consumption == 2
    assert records[(2026, 2)].cold_water_consumption == 3.25

    assert all(r.hot_water_consumption is None for r in records.values())


def test_parse_hot_water() -> None:
    """Existing heating + hot water exports keep parsing as before."""
    api = IstaVdmAPI("user@example.com", "secret")
    records = _by_month(api._parse_csv(HEATING_AND_HOT_WATER_CSV))

    assert records[(2025, 11)].heating_consumption == 327.8
    assert records[(2025, 11)].hot_water_consumption == 0.29
    assert records[(2025, 12)].hot_water_consumption == 0.26
    assert records[(2025, 12)].cold_water_consumption is None
    assert records[(2025, 12)].period_end == date(2025, 12, 31)


def test_parse_all_sections_and_ignore_unknown() -> None:
    """All known sections are parsed; rows of unknown sections are ignored."""
    api = IstaVdmAPI("user@example.com", "secret")
    records = api._parse_csv(ALL_SECTIONS_CSV)

    assert len(records) == 1
    record = records[0]
    assert record.heating_consumption == 10
    assert record.hot_water_consumption == 0.5
    assert record.cold_water_consumption == 1.5


def test_consumption_data_cold_water_defaults() -> None:
    """Cold water fields are optional so existing callers keep working."""
    record = ConsumptionData(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 1, 31),
        heating_consumption=1.0,
        heating_cost=None,
        hot_water_consumption=None,
        hot_water_cost=None,
    )
    assert record.cold_water_consumption is None
    assert record.cold_water_cost is None


class _FakeResponse:
    def __init__(
        self,
        status: int,
        payload: Any = None,
        text: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self._payload = payload
        self._text = text
        self.headers = headers or {}

    async def json(self) -> Any:
        return self._payload

    async def text(self) -> str:
        return self._text

    async def __aenter__(self) -> "_FakeResponse":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


class _FakeSession:
    def __init__(self, responses: dict[str, Any]) -> None:
        # A value is a response, an exception to raise, or a list of them in order
        self._responses = responses
        self.requested: list[str] = []

    def _respond(self, url: str) -> _FakeResponse:
        self.requested.append(url)
        response = self._responses[url]
        if isinstance(response, list):
            response = response.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._respond(url)

    def post(self, url: str, **kwargs: Any) -> _FakeResponse:
        return self._respond(url)


LOGIN_FORM_URL = "https://login.ista.com/realms/vdm/login-actions/authenticate"
LOGIN_PAGE = (
    f'<form id="kc-form-login" action="{LOGIN_FORM_URL}">'
    '<input name="username"><input name="password"></form>'
)
WRONG_PASSWORD_PAGE = '<span id="input-error">Invalid username or password.</span>'


def _login_session(overrides: dict[str, Any]) -> _FakeSession:
    """Return a fake session for a successful login, with single steps overridden."""
    responses: dict[str, Any] = {
        LOGIN_URL: _FakeResponse(200, text=LOGIN_PAGE),
        LOGIN_FORM_URL: _FakeResponse(
            302, headers={"Location": "https://ista-vdm.at/login-redirect?code=abc"}
        ),
        TOKEN_URL: _FakeResponse(200, {"access_token": "token", "expires_in": 300}),
        "https://ista-vdm.at/api/flats": _FakeResponse(200, FLATS_RESPONSE),
    }
    responses.update(overrides)
    return _FakeSession(responses)


FLATS_RESPONSE = {
    "data": [
        {"id": 111, "userId": 42, "street": "Teststraße", "housenumber": "1", "door": "4"},
        {"id": 222, "userId": 42, "street": "Teststraße", "housenumber": "1", "door": "5"},
    ]
}


@pytest.mark.asyncio
async def test_all_flats_are_discovered() -> None:
    """Every flat of the account is kept; the first one stays the default."""
    session = _FakeSession({"https://ista-vdm.at/api/flats": _FakeResponse(200, FLATS_RESPONSE)})
    api = IstaVdmAPI("user@example.com", "secret", session=session)  # type: ignore[arg-type]
    api._access_token = "token"

    await api._get_user_info()

    assert api.flat_id == "111"
    assert api.flat_ids == ["111", "222"]
    assert api.user_id == "42"

    api._token_expires = None  # token counts as valid
    flats = await api.get_flats()
    assert [flat["id"] for flat in flats] == ["111", "222"]
    assert flats[1]["door"] == "5"


@pytest.mark.asyncio
async def test_get_flat_info_for_specific_flat() -> None:
    """get_flat_info queries the requested flat, defaulting to the first one."""
    session = _FakeSession(
        {
            "https://ista-vdm.at/api/flats/111": _FakeResponse(
                200, {"data": {"id": 111, "door": "4"}}
            ),
            "https://ista-vdm.at/api/flats/222": _FakeResponse(
                200, {"data": {"id": 222, "door": "5"}}
            ),
        }
    )
    api = IstaVdmAPI("user@example.com", "secret", session=session)  # type: ignore[arg-type]
    api._access_token = "token"
    api._flat_id = "111"

    default_flat = await api.get_flat_info()
    second_flat = await api.get_flat_info("222")

    assert default_flat is not None and default_flat["door"] == "4"
    assert second_flat is not None and second_flat == {**second_flat, "id": "222", "door": "5"}
    assert session.requested == [
        "https://ista-vdm.at/api/flats/111",
        "https://ista-vdm.at/api/flats/222",
    ]


@pytest.mark.asyncio
async def test_no_flats_raises() -> None:
    """An account without flats is reported as an error."""
    session = _FakeSession({"https://ista-vdm.at/api/flats": _FakeResponse(200, {"data": []})})
    api = IstaVdmAPI("user@example.com", "secret", session=session)  # type: ignore[arg-type]
    api._access_token = "token"

    with pytest.raises(IstaVdmError):
        await api._get_user_info()


def _api(session: _FakeSession) -> IstaVdmAPI:
    return IstaVdmAPI("user@example.com", "secret", session=session)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    """The full login flow stores the token and discovers the flats."""
    api = _api(_login_session({}))

    assert await api.authenticate() is True
    assert api.is_authenticated
    assert api.flat_ids == ["111", "222"]


@pytest.mark.asyncio
async def test_authenticate_wrong_password_is_auth_error() -> None:
    """A rejected password is the only case that asks for new credentials."""
    api = _api(_login_session({LOGIN_FORM_URL: _FakeResponse(200, text=WRONG_PASSWORD_PAGE)}))

    with pytest.raises(IstaVdmAuthError, match="Invalid username or password"):
        await api.authenticate()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("url", "response"),
    [
        (LOGIN_URL, aiohttp.ClientConnectionError("Connection refused")),
        (LOGIN_URL, TimeoutError()),
        (LOGIN_URL, _FakeResponse(503)),
        (LOGIN_FORM_URL, _FakeResponse(502)),
        (TOKEN_URL, _FakeResponse(500)),
        ("https://ista-vdm.at/api/flats", _FakeResponse(503)),
    ],
)
async def test_authenticate_outage_is_connection_error(
    url: str, response: _FakeResponse | Exception
) -> None:
    """Network errors and server errors of the portal are temporary, not auth errors."""
    api = _api(_login_session({url: response}))

    with pytest.raises(IstaVdmConnectionError) as exc_info:
        await api.authenticate()
    assert not isinstance(exc_info.value, IstaVdmAuthError)


@pytest.mark.asyncio
async def test_authenticate_changed_login_page_is_not_auth_error() -> None:
    """A login page without the form is a portal change, not a wrong password."""
    api = _api(_login_session({LOGIN_URL: _FakeResponse(200, text="<html>Maintenance</html>")}))

    with pytest.raises(IstaVdmError) as exc_info:
        await api.authenticate()
    assert not isinstance(exc_info.value, (IstaVdmAuthError, IstaVdmConnectionError))


@pytest.mark.asyncio
async def test_consumption_server_error_is_connection_error() -> None:
    """A server error while fetching consumption data is a connection error."""
    session = _FakeSession({"https://ista-vdm.at/api/flats/111": _FakeResponse(503)})
    api = _api(session)
    api._access_token = "token"
    api._flat_id = "111"

    with pytest.raises(IstaVdmConnectionError):
        await api.get_consumption_data()


@pytest.mark.asyncio
async def test_expired_session_token_logs_in_again() -> None:
    """An expired session token (401) is renewed with the stored credentials."""
    session = _login_session(
        {
            "https://ista-vdm.at/api/flats/111": [
                _FakeResponse(401),
                _FakeResponse(200, {"data": {"id": 111, "door": "4"}}),
            ]
        }
    )
    api = _api(session)
    api._access_token = "expired"
    api._flat_id = "111"

    flat = await api.get_flat_info()

    assert flat is not None and flat["door"] == "4"
    assert session.requested.count(LOGIN_URL) == 1
    assert api._access_token == "token"


@pytest.mark.asyncio
async def test_expired_session_token_with_changed_password_is_auth_error() -> None:
    """If the new login is rejected too, the auth error reaches the caller."""
    session = _login_session(
        {
            "https://ista-vdm.at/api/flats/111": _FakeResponse(401),
            LOGIN_FORM_URL: _FakeResponse(200, text=WRONG_PASSWORD_PAGE),
        }
    )
    api = _api(session)
    api._access_token = "expired"
    api._flat_id = "111"

    with pytest.raises(IstaVdmAuthError, match="Invalid username or password"):
        await api.get_consumption_data()
    assert session.requested.count(LOGIN_URL) == 1
