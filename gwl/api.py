"""Thin client for the Environment Agency Hydrology API.

Docs: https://environment.data.gov.uk/hydrology/doc/reference
No API key is required. Data is published under the Open Government
Licence v3.0 - see the README for the required attribution.
"""

import requests

BASE_URL = "https://environment.data.gov.uk/hydrology"
DEFAULT_TIMEOUT = 60


class HydrologyAPIError(RuntimeError):
    """Raised when the Hydrology API returns an unexpected or empty response."""


def measure_notation(measure_id):
    """Return the bare measure notation, accepting either a notation or a full @id URL."""
    return measure_id.rstrip("/").split("/")[-1]


class HydrologyClient:
    """Small wrapper around the three Hydrology API endpoints this package needs."""

    def __init__(self, session=None, timeout=DEFAULT_TIMEOUT):
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, url, params=None):
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_station(self, station_reference):
        """Resolve a station reference (e.g. "E14150") to its station record."""
        data = self._get(f"{BASE_URL}/id/stations", {"stationReference": station_reference})
        items = data.get("items", [])
        if not items:
            raise HydrologyAPIError(f"No station found for stationReference={station_reference!r}")
        return items[0]

    def get_measures(self, station_notation, observed_property="groundwaterLevel"):
        """List the measures (e.g. logged/dipped series) for a station's observed property."""
        url = f"{BASE_URL}/id/stations/{station_notation}/measures"
        data = self._get(url, {"observedProperty": observed_property})
        return data.get("items", [])

    def get_readings(self, measure_id, latest=False, mineq_date=None, max_date=None,
                      limit=None, time=None):
        """Fetch readings for a measure, accepting either a notation or a full @id URL."""
        notation = measure_notation(measure_id)
        url = f"{BASE_URL}/id/measures/{notation}/readings"
        params = {}
        if latest:
            params["latest"] = ""
        if mineq_date:
            params["mineq-date"] = mineq_date
        if max_date:
            params["max-date"] = max_date
        if limit:
            params["_limit"] = limit
        if time:
            params["time"] = time
        data = self._get(url, params)
        return data.get("items", [])
