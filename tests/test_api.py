"""Tests for the ista VDM API client."""

from datetime import date
from typing import Any

import pytest

from ista_vdm_api import ConsumptionData, IstaVdmAPI, IstaVdmError

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
    def __init__(self, status: int, payload: Any) -> None:
        self.status = status
        self._payload = payload

    async def json(self) -> Any:
        return self._payload

    async def __aenter__(self) -> "_FakeResponse":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None


class _FakeSession:
    def __init__(self, responses: dict[str, _FakeResponse]) -> None:
        self._responses = responses
        self.requested: list[str] = []

    def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.requested.append(url)
        return self._responses[url]


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
