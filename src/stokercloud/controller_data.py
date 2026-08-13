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

    @property
    def outside_temperature(self):
        """Outside temperature as StokerCloud reports it.

        Note this comes from the weather block, alongside city name, wind and
        humidity — it is an online lookup for the installation's location, not
        a sensor wired to the controller. The id is a JSON number here while
        its siblings are strings, so it is looked up as an int.
        """
        return value_or_none(self.get_sub_item('weatherdata', 1), Unit.DEGREE)
