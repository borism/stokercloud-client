import json
import pytest

from stokercloud.controller_data import ControllerData, PowerState, NotConnectedException, Unit, Value, State


def test_controller_data():
    test_data = """
    {
        "weatherdata": [
            {
                "id": "weather-city",
                "value": "Sample Kommune",
                "unit": "",
                "name": "",
                "selection": ""
            },
            {
                "id": 1,
                "value": "0.8",
                "unit": "LNG_DEGREE",
                "name": "lng_weather_1",
                "selection": ""
            },
            {
                "id": "2",
                "value": "1.96",
                "unit": "LNG_METERSEC",
                "name": "lng_weather_2",
                "selection": "weather1"
            },
            {
                "id": "3",
                "value": "E",
                "unit": "",
                "name": "lng_weather_3",
                "selection": "weather2"
            },
            {
                "id": "9",
                "value": "100",
                "unit": "LNG_PERCENT",
                "name": "lng_weather_9",
                "selection": "weather3"
            }
        ],
        "boilerdata": [
            {
                "id": "3",
                "value": 0,
                "unit": "LNG_DEGREE",
                "name": "lng_boil_3",
                "selection": "boiler1"
            },
            {
                "id": "5",
                "value": "3.8",
                "unit": "LNG_KW",
                "name": "lng_boil_5",
                "selection": "boiler2"
            },
            {
                "id": "4",
                "value": "14",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_4",
                "selection": "boiler3"
            },
            {
                "id": "6",
                "value": "100",
                "unit": "",
                "name": "lng_boil_6",
                "selection": "boiler4"
            },
            {
                "id": "12",
                "value": "17.6",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_12",
                "selection": "boiler5"
            },
            {
                "id": "14",
                "value": "100",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_14",
                "selection": "boiler6"
            },
            {
                "id": "15",
                "value": "100",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_15",
                "selection": "boiler7"
            },
            {
                "id": "16",
                "value": "100",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_16",
                "selection": "boiler8"
            },
            {
                "id": "9",
                "value": "99.8",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_9",
                "selection": "boiler9"
            }
        ],
        "hopperdata": [
            {
                "id": "2",
                "value": "1300",
                "unit": "LNG_GRAM",
                "name": "lng_hopper_2",
                "selection": "hopper1"
            },
            {
                "id": "3",
                "value": "27.7",
                "unit": "LNG_KG",
                "name": "lng_hopper_3",
                "selection": "hopper2"
            },
            {
                "id": "4",
                "value": "1499",
                "unit": "LNG_KG",
                "name": "lng_hopper_4",
                "selection": "hopper3"
            },
            {
                "id": "7",
                "value": "3.0",
                "unit": "LNG_KW",
                "name": "lng_hopper_7",
                "selection": "hopper4"
            },
            {
                "id": "8",
                "value": "20",
                "unit": "LNG_KW",
                "name": "lng_hopper_8",
                "selection": "hopper5"
            }
        ],
        "dhwdata": [
            {
                "id": "3",
                "value": "6",
                "unit": "LNG_DEGREE",
                "name": "lng_dhw_3",
                "selection": "dhw1"
            },
            {
                "id": "4",
                "value": "N/A",
                "unit": "LNG_PERCENT",
                "name": "lng_dhw_4",
                "selection": "dhw2"
            }
        ],
        "frontdata": [
            {
                "id": "hoppercontent",
                "value": "-1493",
                "unit": "LNG_KG",
                "name": "lng_hopper_1",
                "selection": ""
            },
            {
                "id": "boilertemp",
                "value": "59.9",
                "unit": "LNG_DEGREE",
                "name": "lng_boil_1",
                "selection": ""
            },
            {
                "id": "-wantedboilertemp",
                "value": "62.0",
                "unit": "LNG_DEGREE",
                "name": "lng_boil_2",
                "selection": ""
            },
            {
                "id": "dhw",
                "value": 54.9,
                "unit": "LNG_DEGREE",
                "name": "lng_dhw_1",
                "selection": ""
            },
            {
                "id": "dhwwanted",
                "value": "57",
                "unit": "LNG_DEGREE",
                "name": "lng_dhw_2",
                "selection": ""
            },
            {
                "id": "refoxygen",
                "value": "20.9",
                "unit": "LNG_PERCENT",
                "name": "lng_boil_13",
                "selection": ""
            },
            {
                "id": "refair",
                "value": "0",
                "unit": "LNG_M3HOUR",
                "name": "lng_boil_13",
                "selection": ""
            }
        ],
        "miscdata": {
            "state": {
                "id": "state",
                "value": "state_5",
                "unit": "LNG_KW",
                "name": "",
                "selection": ""
            },
            "clock": {
                "id": "clock",
                "value": "22:30",
                "unit": "",
                "name": "",
                "selection": ""
            },
            "substate": {
                "id": "substate",
                "value": "",
                "unit": "",
                "name": "",
                "selection": ""
            },
            "substatesecs": {
                "id": "substatesecs",
                "value": 0,
                "unit": "",
                "name": "",
                "selection": ""
            },
            "alarm": 0,
            "running": 1,
            "output": 3.8,
            "outputpct": "14",
            "hopper.distance_max": "50",
            "vacuum.min_distance": null,
            "vacuum.max_distance": null,
            "vacuum.output_auger": "0",
            "backpressure": null,
            "hopperdistance": 999
        },
        "leftoutput": {
            "output-1": {
                "val": "OFF",
                "unit": "",
                "image": "1-dhw.png"
            },
            "output-2": {
                "val": "disabled",
                "unit": "",
                "image": "2-pump.png"
            },
            "output-3": {
                "val": "disabled",
                "unit": "",
                "image": "3-weathervalve.png"
            },
            "output-4": {
                "val": "disabled",
                "unit": "",
                "image": "4-weatherpump.png"
            },
            "output-5": {
                "val": "disabled",
                "unit": "%",
                "image": "5-exhaustfan.png"
            },
            "output-6": {
                "val": "disabled",
                "unit": "LNG_KG",
                "image": "6-ashauger.png"
            },
            "output-7": {
                "val": "disabled",
                "unit": "",
                "image": "7-compressor.png"
            },
            "output-8": {
                "val": "disabled",
                "unit": "%",
                "image": "8-weathervalve2.png"
            },
            "output-9": {
                "val": "disabled",
                "unit": "",
                "image": "9-weatherpump2.png"
            }
        },
        "rightoutput": {
            "sunoutput-1": {
                "val": "disabled",
                "unit": "",
                "image": "output-sun-pump.png"
            },
            "sunoutput-2": {
                "val": "disabled",
                "unit": "",
                "image": "output-sun-valve.png"
            }
        },
        "infomessages": [],
        "model": "1",
        "weathercomp": {
            "zone1active": 0,
            "zone2active": 0,
            "zone1-wanted": {
                "val": 0,
                "unit": "LNG_DEGREE"
            },
            "zone1-actual": {
                "val": 999.9,
                "unit": "LNG_DEGREE"
            },
            "zone1-valve": {
                "val": "0",
                "unit": "LNG_PERCENT"
            },
            "zone1-actualref": {
                "val": "0.8",
                "unit": "LNG_DEGREE"
            },
            "zone1-calc": {
                "val": 0.3,
                "unit": "LNG_DEGREE"
            },
            "zone2-wanted": {
                "val": "0.0",
                "unit": "LNG_DEGREE"
            },
            "zone2-actual": {
                "val": "999.9",
                "unit": "LNG_DEGREE"
            },
            "zone2-valve": {
                "val": "0",
                "unit": "LNG_PERCENT"
            },
            "zone2-actualref": {
                "val": "0.8",
                "unit": "LNG_DEGREE"
            },
            "zone2-calc": {
                "val": "0.3",
                "unit": "LNG_DEGREE"
            }
        },
        "notconnected": 0,
        "newuser": 0,
        "serial": "12345",
        "metrics": "EUR"
    }
    """
    cd = ControllerData(json.loads(test_data))

    assert cd.running == PowerState.ON
    assert cd.alarm == PowerState.OFF
    assert cd.serial_number == "12345"
    assert cd.boiler_kwh == Value("3.8", Unit.KWH)
    assert cd.boiler_temperature_current == Value("59.9", Unit.DEGREE)
    assert cd.boiler_temperature_requested == Value("62.0", Unit.DEGREE)
    assert cd.state == State.POWER
    assert cd.consumption_total == Value("1499", Unit.KILO_GRAM)
    assert cd.outside_temperature == Value("0.8", Unit.DEGREE)
    assert cd.oxygen == Value("17.6", Unit.PERCENT)
    assert cd.oxygen_requested == Value("20.9", Unit.PERCENT)
    assert cd.consumption_day == Value("27.7", Unit.KILO_GRAM)
    # JSON floats here, so this also pins the str() conversion: a bare
    # Decimal(0.3) would be 0.2999999999999999888977697537...
    assert cd.zone1_temperature_current == Value("999.9", Unit.DEGREE)
    assert cd.zone1_temperature_calculated == Value("0.3", Unit.DEGREE)
    assert cd.substate is None  # empty string in the payload
    assert cd.substate_seconds == 0


def test_controller_data_connected():
    test_data = '{"notconnected": 1}'
    with pytest.raises(NotConnectedException):
        ControllerData(json.loads(test_data))

def test_null_and_missing_values():
    """StokerCloud sends null for values the controller isn't producing."""
    test_data = """
    {
        "frontdata": [
            {"id": "boilertemp", "value": "18.6", "unit": "LNG_DEGREE"},
            {"id": "-wantedboilertemp", "value": null, "unit": "LNG_DEGREE"}
        ],
        "hopperdata": [],
        "weatherdata": [],
        "miscdata": {"state": {"value": "state_9"}, "alarm": 0, "running": 0},
        "notconnected": 0,
        "serial": "12345"
    }
    """
    cd = ControllerData(json.loads(test_data))

    # present value still parses
    assert cd.boiler_temperature_current == Value("18.6", Unit.DEGREE)
    # null value reads as absent instead of raising TypeError from Decimal(None)
    assert cd.boiler_temperature_requested is None
    # entry missing from the payload entirely is absent too
    assert cd.consumption_total is None
    # unknown state code is absent rather than a KeyError
    assert cd.state is None
    # whole weatherdata block missing from the payload
    assert cd.outside_temperature is None
    # no weathercomp block at all
    assert cd.zone1_temperature_current is None


def test_chart_values_takes_latest_point():
    """Series are returned as [[timestamp, value], ...], newest last."""
    from stokercloud.client import Client
    import time

    client = Client("someuser")
    client.cached_chart = [
        {"name": "drift_exttemp", "data": [[1786664029000, 12.1], [1786671168000, 13.7]]},
        {"name": "drift_kedel_temp", "data": [[1786671168000, 18.7]]},
        {"name": "drift_empty", "data": []},
        {"data": [[1786671168000, 1]]},  # no name
    ]
    client.last_chart_fetch = time.time()  # inside the cache window, so no request

    values = client.chart_values()
    assert values == {"drift_exttemp": 13.7, "drift_kedel_temp": 18.7}


def _consumption_client(monkeypatch, payload, urls=None):
    """Client whose HTTP layer returns ``payload`` (JSON-encoded) for every request."""
    import io
    from stokercloud import client as client_module

    def fake_urlopen(url, timeout=None):
        if urls is not None:
            urls.append(url)
        return io.BytesIO(json.dumps(payload).encode())

    monkeypatch.setattr(client_module.request, "urlopen", fake_urlopen)
    client = client_module.Client("example_user")
    client.token = "tok"
    return client


def test_consumption_history_normal(monkeypatch):
    from datetime import datetime, timezone

    urls = []
    payload = [
        {"label": "other_series", "data": [[1700000000000, 99]]},
        {"label": "graph_consume", "data": [
            [1700000000000, 0.5],
            [1700003600000, "1.25"],  # numeric strings are accepted
            [1700007200000, 0],
        ]},
    ]
    client = _consumption_client(monkeypatch, payload, urls)

    result = client.consumption_history("hours")

    assert result == [
        (datetime.fromtimestamp(1700007200, tz=timezone.utc), 0.0),
        (datetime.fromtimestamp(1700003600, tz=timezone.utc), 1.25),
        (datetime.fromtimestamp(1700000000, tz=timezone.utc), 0.5),
    ]
    assert urls == [client.BASE_URL + "v2/dataout2/getconsumption.php?hours=24&token=tok"]


def test_consumption_history_period_counts(monkeypatch):
    urls = []
    client = _consumption_client(monkeypatch, [], urls)
    for period in ("hours", "days", "months", "years"):
        client.consumption_history(period)
    assert [u.split("?")[1].split("&")[0] for u in urls] == [
        "hours=24", "days=24", "months=12", "years=12",
    ]
    with pytest.raises(ValueError):
        client.consumption_history("weeks")


@pytest.mark.parametrize("payload", [{}, [], None, "oops", [{"label": "graph_consume"}],
                                     [{"label": "graph_consume", "data": None}],
                                     [{"label": "graph_consume", "data": []}]])
def test_consumption_history_empty(monkeypatch, payload):
    assert _consumption_client(monkeypatch, payload).consumption_history() == []


def test_consumption_history_missing_label(monkeypatch):
    payload = [{"label": "something_else", "data": [[1700000000000, 1.0]]}, "junk", 3]
    assert _consumption_client(monkeypatch, payload).consumption_history() == []


def test_consumption_history_malformed_points(monkeypatch):
    from datetime import datetime, timezone

    payload = [{"label": "graph_consume", "data": [
        [1700000000000, 2.0],      # good
        [1700003600000],           # too short
        [1700007200000, 1, 2],     # too long
        [1700010800000, None],     # null value
        [1700014400000, "abc"],    # non-numeric value
        [1700018000000, "nan"],    # not finite
        ["bad", 1.0],              # non-numeric timestamp
        None,
        "x",
        [1e30, 1.0],               # timestamp out of range
    ]}]
    result = _consumption_client(monkeypatch, payload).consumption_history()
    assert result == [(datetime.fromtimestamp(1700000000, tz=timezone.utc), 2.0)]
