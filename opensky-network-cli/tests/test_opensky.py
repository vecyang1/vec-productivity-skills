"""
Deterministic, offline unit tests for OpenSky Network Python client and models.
Requires 0 live network access.
"""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure module is discoverable from any CWD
_SKILL_DIR = str(Path(__file__).resolve().parent.parent)
if _SKILL_DIR not in sys.path:
    sys.path.insert(0, _SKILL_DIR)

from opensky.models import FlightRecord, FlightState, FlightTrack, RateLimitStatus
from opensky.resolver import resolve_credentials
from opensky.transport import OpenSkyTransport
from opensky.api import OpenSkyAPI


class TestOpenSkyModels(unittest.TestCase):
    def test_flight_state_parsing_and_conversions(self):
        raw_state = [
            "885142",        # 0: icao24
            "HVN123  ",      # 1: callsign
            "Vietnam",       # 2: origin_country
            1724740000,      # 3: time_position
            1724740005,      # 4: last_contact
            105.80,          # 5: longitude
            21.22,           # 6: latitude
            10000.0,         # 7: baro_altitude (m)
            False,           # 8: on_ground
            250.0,           # 9: velocity (m/s)
            180.5,           # 10: true_track (deg)
            -5.0,            # 11: vertical_rate (m/s)
            None,            # 12: sensors
            10100.0,         # 13: geo_altitude
            "7401",          # 14: squawk
            False,           # 15: spi
            0,               # 16: position_source
            1,               # 17: category
        ]

        state = FlightState.from_api_array(raw_state)
        self.assertEqual(state.icao24, "885142")
        self.assertEqual(state.callsign, "HVN123")
        self.assertEqual(state.origin_country, "Vietnam")
        self.assertFalse(state.on_ground)

        # Conversions
        self.assertAlmostEqual(state.altitude_ft, 32808.4, places=1)
        self.assertAlmostEqual(state.speed_kmh, 900.0, places=1)
        self.assertAlmostEqual(state.speed_kts, 486.0, places=1)
        self.assertAlmostEqual(state.vertical_rate_fpm, -984.2, places=1)

        d = state.to_dict()
        self.assertEqual(d["icao24"], "885142")
        self.assertEqual(d["callsign"], "HVN123")
        self.assertEqual(d["speed_kmh"], 900.0)

    def test_flight_record_parsing(self):
        raw_flight = {
            "icao24": "885142",
            "firstSeen": 1724740000,
            "estDepartureAirport": "VVNB",
            "lastSeen": 1724747200,
            "estArrivalAirport": "VVTS",
            "callsign": "HVN123",
        }
        rec = FlightRecord.from_api_dict(raw_flight)
        self.assertEqual(rec.icao24, "885142")
        self.assertEqual(rec.est_departure_airport, "VVNB")
        self.assertEqual(rec.est_arrival_airport, "VVTS")
        self.assertEqual(rec.callsign, "HVN123")

    def test_flight_track_parsing(self):
        raw_track = {
            "icao24": "885142",
            "callsign": "HVN123",
            "startTime": 1724740000,
            "endTime": 1724747200,
            "path": [
                [1724740000, 21.22, 105.80, 1000.0, 180.0, False],
                [1724740100, 21.10, 105.82, 3000.0, 180.0, False],
            ]
        }
        track = FlightTrack.from_api_dict(raw_track)
        self.assertEqual(track.icao24, "885142")
        self.assertEqual(len(track.path), 2)
        d = track.to_dict()
        self.assertEqual(d["waypoint_count"], 2)


class TestOpenSkyResolverAndTransport(unittest.TestCase):
    def test_explicit_credentials_resolution(self):
        cid, csec, src = resolve_credentials(
            custom_client_id="my_id",
            custom_client_secret="my_secret",
        )
        self.assertEqual(cid, "my_id")
        self.assertEqual(csec, "my_secret")
        self.assertEqual(src, "explicit_arguments")

    @patch("opensky.resolver._read_from_1password")
    def test_1password_resolver(self, mock_1p):
        mock_1p.side_effect = lambda ref: "mock_cid" if "username" in ref else "mock_secret"
        with patch.dict("os.environ", {}, clear=True):
            cid, csec, src = resolve_credentials()
            self.assertEqual(cid, "mock_cid")
            self.assertEqual(csec, "mock_secret")
            self.assertEqual(src, "1password_vault")

    @patch("urllib.request.urlopen")
    def test_transport_request_and_quota_header_parsing(self, mock_urlopen):
        # Mock HTTP response
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "time": 1724740000,
            "states": [
                ["885142", "HVN123", "Vietnam", 1724740000, 1724740005, 105.8, 21.2, 10000.0, False, 250.0, 180.0, 0.0, None, 10000.0, "7401", False, 0, 0]
            ]
        }).encode("utf-8")
        mock_resp.headers = {
            "X-Rate-Limit-Remaining": "3980",
            "X-Rate-Limit-Retry-After-Seconds": "0",
        }
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        api = OpenSkyAPI(client_id="test_id", client_secret="test_secret")
        # Bypass get_valid_token for offline test
        with patch.object(api.transport, "get_valid_token", return_value="fake_bearer_token"):
            states = api.get_states(bbox=[21.0, 105.0, 22.0, 106.0])
            self.assertEqual(len(states), 1)
            self.assertEqual(states[0].callsign, "HVN123")
            
            rl = api.get_rate_limit_status()
            self.assertEqual(rl.remaining_credits, 3980)


if __name__ == "__main__":
    unittest.main()
