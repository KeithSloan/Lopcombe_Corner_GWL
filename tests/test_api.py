"""Tests that HydrologyClient correctly parses sample API responses."""

import unittest
from unittest.mock import MagicMock

from gwl import api

SAMPLE_READINGS_RESPONSE = {
    "meta": {"limit": 100000},
    "items": [
        {
            "measure": {"@id": "http://environment.data.gov.uk/hydrology/id/measures/abc-gw-logged-i-subdaily-mAOD-qualified"},
            "date": "2026-07-01",
            "dateTime": "2026-07-01T09:00:00",
            "value": 79.649,
            "quality": "Unchecked",
        },
        {
            "measure": {"@id": "http://environment.data.gov.uk/hydrology/id/measures/abc-gw-logged-i-subdaily-mAOD-qualified"},
            "date": "2026-07-02",
            "dateTime": "2026-07-02T09:00:00",
            "value": 79.618,
            "quality": "Unchecked",
        },
    ],
}

SAMPLE_STATION_RESPONSE = {
    "meta": {"limit": 100},
    "items": [
        {
            "@id": "http://environment.data.gov.uk/hydrology/id/stations/c962ac5b-0532-4220-ac82-160104126de1",
            "label": "Lopcombe Corner",
            "notation": "c962ac5b-0532-4220-ac82-160104126de1",
            "stationReference": "E14150",
        }
    ],
}

SAMPLE_DIPPED_ONLY_STATION_RESPONSE = {
    "meta": {"limit": 100},
    "items": [
        {
            "@id": "http://environment.data.gov.uk/hydrology/id/stations/06f4a7b9-0e81-4d98-abef-ca4818d1cf65",
            "label": "Nelson Arms Winterslow",
            "notation": "06f4a7b9-0e81-4d98-abef-ca4818d1cf65",
            "wiskiID": "141811463",
        }
    ],
}

EMPTY_RESPONSE = {"meta": {}, "items": []}


def _make_client_with_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    session = MagicMock()
    session.get.return_value = response
    return api.HydrologyClient(session=session), session


class GetReadingsTests(unittest.TestCase):
    def test_parses_items_from_response(self):
        client, _session = _make_client_with_response(SAMPLE_READINGS_RESPONSE)
        readings = client.get_readings("abc-gw-logged-i-subdaily-mAOD-qualified", time="09:00:00")
        self.assertEqual(len(readings), 2)
        self.assertEqual(readings[0]["value"], 79.649)
        self.assertEqual(readings[1]["date"], "2026-07-02")

    def test_accepts_full_id_url_and_builds_expected_query_params(self):
        client, session = _make_client_with_response(SAMPLE_READINGS_RESPONSE)
        client.get_readings(
            "http://environment.data.gov.uk/hydrology/id/measures/abc-gw-logged-i-subdaily-mAOD-qualified",
            mineq_date="2026-07-01", max_date="2026-07-02", time="09:00:00", limit=5,
        )
        called_args, called_kwargs = session.get.call_args
        self.assertTrue(called_args[0].endswith("/id/measures/abc-gw-logged-i-subdaily-mAOD-qualified/readings"))
        self.assertEqual(called_kwargs["params"], {
            "mineq-date": "2026-07-01",
            "max-date": "2026-07-02",
            "_limit": 5,
            "time": "09:00:00",
        })

    def test_latest_flag_sends_bare_latest_param(self):
        client, session = _make_client_with_response(SAMPLE_READINGS_RESPONSE)
        client.get_readings("abc-gw-logged-i-subdaily-mAOD-qualified", latest=True)
        _called_args, called_kwargs = session.get.call_args
        self.assertEqual(called_kwargs["params"], {"latest": ""})

    def test_empty_response_returns_empty_list(self):
        client, _session = _make_client_with_response({"meta": {}, "items": []})
        readings = client.get_readings("abc-gw-dipped-i-mAOD-qualified")
        self.assertEqual(readings, [])


class GetStationTests(unittest.TestCase):
    def test_parses_station_from_response(self):
        client, _session = _make_client_with_response(SAMPLE_STATION_RESPONSE)
        station = client.get_station("E14150")
        self.assertEqual(station["notation"], "c962ac5b-0532-4220-ac82-160104126de1")
        self.assertEqual(station["label"], "Lopcombe Corner")

    def test_raises_when_no_station_found(self):
        client, _session = _make_client_with_response({"meta": {}, "items": []})
        with self.assertRaises(api.HydrologyAPIError):
            client.get_station("E00000")

    def test_falls_back_to_wiskiid_when_no_stationreference_match(self):
        # Dipped-only sites (e.g. Nelson Arms Winterslow) have no stationReference,
        # only a wiskiID and notation - stationReference lookup misses, wiskiID hits.
        response_empty = MagicMock()
        response_empty.json.return_value = EMPTY_RESPONSE
        response_empty.raise_for_status.return_value = None
        response_hit = MagicMock()
        response_hit.json.return_value = SAMPLE_DIPPED_ONLY_STATION_RESPONSE
        response_hit.raise_for_status.return_value = None

        session = MagicMock()
        session.get.side_effect = [response_empty, response_hit]
        client = api.HydrologyClient(session=session)

        station = client.get_station("141811463")
        self.assertEqual(station["label"], "Nelson Arms Winterslow")
        first_call_params = session.get.call_args_list[0].kwargs["params"]
        second_call_params = session.get.call_args_list[1].kwargs["params"]
        self.assertEqual(first_call_params, {"stationReference": "141811463"})
        self.assertEqual(second_call_params, {"wiskiID": "141811463"})

    def test_falls_back_to_notation_path_when_no_param_match(self):
        response_empty = MagicMock()
        response_empty.json.return_value = EMPTY_RESPONSE
        response_empty.raise_for_status.return_value = None
        response_hit = MagicMock()
        response_hit.json.return_value = SAMPLE_DIPPED_ONLY_STATION_RESPONSE
        response_hit.raise_for_status.return_value = None

        session = MagicMock()
        session.get.side_effect = [response_empty, response_empty, response_hit]
        client = api.HydrologyClient(session=session)

        station = client.get_station("06f4a7b9-0e81-4d98-abef-ca4818d1cf65")
        self.assertEqual(station["label"], "Nelson Arms Winterslow")
        third_call_args = session.get.call_args_list[2]
        self.assertTrue(
            third_call_args.args[0].endswith("/id/stations/06f4a7b9-0e81-4d98-abef-ca4818d1cf65")
        )


if __name__ == "__main__":
    unittest.main()
