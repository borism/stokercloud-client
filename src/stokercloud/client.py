import json
import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from http.client import HTTPResponse
from urllib import request
from urllib.parse import urljoin
import logging
import time
from stokercloud.controller_data import ControllerData

logger = logging.getLogger(__name__)

# stokercloud.dk has been observed to accept a connection and then never
# reply; urlopen has no timeout by default, which hung every polling thread
# forever and starved HA's executor pool until nothing updated anymore.
REQUEST_TIMEOUT_SECONDS = 15

# getconsumption.php only accepts these window sizes per period.
# StokerCloud's epoch-ms timestamps are not UTC: they are Danish wall-clock
# time encoded as if it were UTC.
# ponytail: inferred from a winter (CET, UTC+1) observation only; summer
# (CEST, UTC+2) behaviour still needs verifying against real data.
STOKERCLOUD_TZ = ZoneInfo("Europe/Copenhagen")

CONSUMPTION_PERIODS = {"hours": 24, "days": 24, "months": 12, "years": 12}


class TokenInvalid(Exception):
    pass


class Client:
    BASE_URL = "http://www.stokercloud.dk/"

    def __init__(self, name: str, password: str = None, cache_time_seconds: int = 10,
                 chart_cache_time_seconds: int = 300):
        self.name = name
        self.password = password
        self.token = None
        self.state = None
        self.last_fetch = None
        self.cache_time_seconds = cache_time_seconds
        self.cached_chart = None
        self.last_chart_fetch = None
        self.chart_cache_time_seconds = chart_cache_time_seconds

    def refresh_token(self):
        with request.urlopen(
                urljoin(
                    self.BASE_URL,
                    'v2/dataout2/login.php?user=%s' % self.name
                ),
                timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            data = json.loads(response.read())
            self.token = data['token']  # actual token
            self.state = data['credentials']  # readonly

    def make_request(self, url, *args, **kwargs):
        try:
            if self.token is None:
                raise TokenInvalid()
            absolute_url = urljoin(
                self.BASE_URL,
                "%s%stoken=%s" % (url, '&' if '?' in url else '?', self.token)
            )
            logger.debug(absolute_url)
            with request.urlopen(absolute_url, timeout=REQUEST_TIMEOUT_SECONDS) as data:
                return json.load(data)
        except TokenInvalid:
            self.refresh_token()
            return self.make_request(url, *args, **kwargs)

    def update_controller_data(self):
        self.cached_data = self.make_request("v2/dataout2/controllerdata2.php")
        self.last_fetch = time.time()

    def controller_data(self):
        if not self.last_fetch or (time.time() - self.last_fetch) > self.cache_time_seconds:
            self.update_controller_data()
        return ControllerData(self.cached_data)

    def chart_values(self, hours: int = 1):
        """Latest value of every chart series, keyed by series name.

        Readings the controller publishes but controllerdata2 leaves out live
        here — notably drift_exttemp, the external temperature sensor, as
        opposed to the online weather lookup in the weatherdata block.

        This endpoint returns every series over the whole window (~65 kB for
        one hour, all 47 series) with no way to ask for one, so it is cached
        much longer than controller data. Raise chart_cache_time_seconds if
        the bandwidth matters more than freshness, or lower it if you are
        charting something that moves fast.
        """
        if not self.last_chart_fetch or (time.time() - self.last_chart_fetch) > self.chart_cache_time_seconds:
            self.cached_chart = self.make_request(
                "v2/dataout2/getchartv2.php?hours=%d" % hours
            )
            self.last_chart_fetch = time.time()
        return {
            series['name']: series['data'][-1][1]
            for series in self.cached_chart
            if series.get('name') and series.get('data')
        }

    def consumption_history(self, period: str = "hours"):
        """Pellet consumption history in kg, newest first.

        ``period`` is ``hours`` (last 24), ``days`` (last 24), ``months``
        (last 12) or ``years`` (last 12). Returns a list of
        ``(bucket start as aware UTC datetime, kg)``; the raw timestamps are
        Copenhagen wall-clock time (see ``STOKERCLOUD_TZ``) and are converted
        to real UTC. An empty or unexpected
        response, a missing ``graph_consume`` series and malformed points all
        give an empty list / are skipped rather than raising. Network errors
        still propagate from ``make_request``.

        Adapted from ``async_get_consumption`` in vurrut/stokercloud-client
        (MIT).
        """
        if period not in CONSUMPTION_PERIODS:
            raise ValueError("Invalid period: %s" % period)
        data = self.make_request(
            "v2/dataout2/getconsumption.php?%s=%d" % (period, CONSUMPTION_PERIODS[period])
        )
        if not isinstance(data, list):
            return []
        series = next(
            (s for s in data if isinstance(s, dict) and s.get("label") == "graph_consume"),
            None,
        )
        points = series.get("data") if series else None
        result = []
        for point in points if isinstance(points, list) else []:
            try:
                ts, kg = point
                kg = float(kg)
                if not math.isfinite(kg):
                    continue
                wall_clock = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                result.append((
                    wall_clock.replace(tzinfo=STOKERCLOUD_TZ).astimezone(timezone.utc),
                    kg,
                ))
            except (TypeError, ValueError, OverflowError, OSError):
                continue
        result.sort(key=lambda p: p[0], reverse=True)
        return result
