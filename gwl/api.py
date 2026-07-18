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

    def get_station(self, identifier):
        """Resolve a station to its record.

        Tries, in order: stationReference (e.g. "E14150"), wiskiID, and
        notation (the station's GUID). Many manual/dipped-only groundwater
        sites have no stationReference at all, only a wiskiID and notation,
        so a single lookup path isn't enough to cover every station.
        """
        for param in ("stationReference", "wiskiID"):
            data = self._get(f"{BASE_URL}/id/stations", {param: identifier})
            items = data.get("items", [])
            if items:
                return items[0]

        try:
            data = self._get(f"{BASE_URL}/id/stations/{identifier}")
        except requests.HTTPError:
            data = {"items": []}
        items = data.get("items", [])
        if items:
            return items[0]

        raise HydrologyAPIError(
            f"No station found for {identifier!r} (tried stationReference, wiskiID, notation)"
        )

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
