import decimal
from enum import Enum


class NotConnectedException(Exception):
    pass


class PowerState(Enum):
    ON = 1
    OFF = 0


class Unit(Enum):
    KWH = 'kwh'
    PERCENT = 'pct'
    DEGREE = 'deg'
    KILO_GRAM = 'kg'
    GRAM = 'g'


class State(Enum):
    POWER = 'state_5'
    HOT_WATER = 'state_7'
    IGNITION_1 = 'state_2'
    IGNITION_2 = 'state_4'
    FAULT_IGNITION = 'state_13'
    OFF = 'state_14'


STATE_BY_VALUE = {key.value: key for key in State}


class Value:
    def __init__(self, value, unit):
        self.value = decimal.Decimal(value)
        self.unit = unit

    def __eq__(self, other):
        if not isinstance(other, Value):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.value == other.value and self.unit == other.unit

    def __repr__(self):
        return "%s %s" % (self.value, self.unit)

def value_or_none(item, unit):
    """Build a Value, or None if StokerCloud isn't reporting this one.

    The API sends null for values the controller isn't currently producing
    (-wantedboilertemp has no setpoint while the boiler is idle), and omits
    entries entirely on some models. Absent is not zero, so report it as
    absent instead of raising from Decimal(None).
    """
    if item is None or item.get('value') is None:
        return None
    return Value(item['value'], unit)


def get_from_list_by_key(lst, key, value):
    for itm in lst:
        if itm.get(key) == value:
            return itm

class ControllerData:
    def __init__(self, data):
        if data['notconnected'] != 0:
            raise NotConnectedException("Furnace/boiler not connected to StokerCloud")
        self.data = data

    def get_sub_item(self, submenu, _id):
        return get_from_list_by_key(self.data[submenu], 'id', _id)

    @property
    def alarm(self):
        return {
            0: PowerState.OFF,
            1: PowerState.ON
        }.get(self.data['miscdata'].get('alarm'))

    @property
    def running(self):
        return {
            0: PowerState.OFF,
            1: PowerState.ON
        }.get(self.data['miscdata'].get('running'))

    @property
    def serial_number(self):
        return self.data['serial']

    @property
    def boiler_temperature_current(self):
        return value_or_none(self.get_sub_item('frontdata', 'boilertemp'), Unit.DEGREE)

    @property
    def boiler_temperature_requested(self):
        return value_or_none(self.get_sub_item('frontdata', '-wantedboilertemp'), Unit.DEGREE)

    @property
    def boiler_kwh(self):
        return value_or_none(self.get_sub_item('boilerdata', '5'), Unit.KWH)

    @property
    def state(self):
        return STATE_BY_VALUE.get(self.data['miscdata']['state']['value'])

    @property
    def hotwater_temperature_current(self):
        return value_or_none(self.get_sub_item('frontdata', 'dhw'), Unit.DEGREE)

    @property
    def hotwater_temperature_requested(self):
        return value_or_none(self.get_sub_item('frontdata', 'dhwwanted'), Unit.DEGREE)

    @property
    def consumption_total(self):
        return value_or_none(self.get_sub_item('hopperdata', '4'), Unit.KILO_GRAM)
    
    @property
    def consumption_day(self):
        return value_or_none(self.get_sub_item('hopperdata', '3'), Unit.KILO_GRAM)

    def get_output(self, image_hint, fallback_key):
        """State of a `leftoutput` entry, as PowerState, or None if unknown.

        Entries look like {'val': 'ON', 'unit': '', 'image': '1-dhw.png'}. The
        image name says what the output drives, so match on that and fall back
        to the fixed key. `val` can also be 'N/A' or 'disabled' (and the block
        or entry can be absent); all of those are unknown, not OFF.
        """
        outputs = self.data.get('leftoutput') or {}
        item = next(
            (v for v in outputs.values()
             if isinstance(v, dict) and image_hint in str(v.get('image') or '').lower()),
            outputs.get(fallback_key),
        )
        if not isinstance(item, dict):
            return None
        return {'ON': PowerState.ON, 'OFF': PowerState.OFF}.get(str(item.get('val')).upper())

    @property
    def dhw_valve(self):
        """Controller is driving the DHW diverter valve output."""
        return self.get_output('dhw', 'output-1')

    @property
    def circulation_pump(self):
        return self.get_output('pump', 'output-2')

    def get_weathercomp(self, key):
        """weathercomp entries are {'val': ..., 'unit': ...}, not the
        {'id': ..., 'value': ...} shape the other blocks use."""
        item = self.data.get('weathercomp', {}).get(key)
        if item is None or item.get('val') is None:
            return None
        # These arrive as JSON floats where other blocks send strings, and
        # Decimal(20.8) is 20.80000000000000071..., so go via str.
        return Value(str(item['val']), Unit.DEGREE)

    @property
    def zone1_temperature_current(self):
        """Zone 1 measured temperature ("Zone 1 T6" in the UI)."""
        return self.get_weathercomp('zone1-actual')

    @property
    def zone1_temperature_requested(self):
        """Zone 1 target flow temperature."""
        return self.get_weathercomp('zone1-wanted')

    @property
    def zone1_temperature_calculated(self):
        """Zone 1 weather-compensation reference.

        Tracks the external temperature sensor closely, so it appears to be
        the filtered outdoor value the compensation curve is evaluated at
        rather than a flow temperature.
        """
        return self.get_weathercomp('zone1-calc')

    @property
    def substate(self):
        """Finer-grained state than `state`, e.g. which ignition phase.

        Empty string when the controller isn't reporting one, normalised to
        None so callers don't have to special-case it.
        """
        return self.data['miscdata'].get('substate', {}).get('value') or None

    @property
    def substate_seconds(self):
        """Seconds spent in the current substate. Useful for spotting a
        controller stuck in one phase."""
        return self.data['miscdata'].get('substatesecs', {}).get('value')

    @property
    def oxygen(self):
        """Measured flue oxygen. Also in the chart data as drift_oxygen."""
        return value_or_none(self.get_sub_item('boilerdata', '12'), Unit.PERCENT)

    @property
    def oxygen_requested(self):
        return value_or_none(self.get_sub_item('frontdata', 'refoxygen'), Unit.PERCENT)

    @property
    def outside_temperature(self):
        """Outside temperature as StokerCloud reports it.

        Note this comes from the weather block, alongside city name, wind and
        humidity — it is an online lookup for the installation's location, not
        a sensor wired to the controller. The id is a JSON number here while
        its siblings are strings, so it is looked up as an int.
        """
        return value_or_none(self.get_sub_item('weatherdata', 1), Unit.DEGREE)
