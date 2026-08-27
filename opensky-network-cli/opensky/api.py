"""
High-level OpenSky Network API client.
"""
import time
from typing import List, Optional, Tuple, Union

from .models import FlightRecord, FlightState, FlightTrack, RateLimitStatus
from .transport import OpenSkyTransport


class OpenSkyAPI:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: float = 12.0,
    ):
        self.transport = OpenSkyTransport(
            client_id=client_id,
            client_secret=client_secret,
            timeout=timeout,
        )

    def get_states(
        self,
        bbox: Optional[Union[Tuple[float, float, float, float], List[float]]] = None,
        icao24: Optional[Union[str, List[str]]] = None,
        unix_time: Optional[int] = None,
    ) -> List[FlightState]:
        """
        Retrieve live state vectors of aircraft.
        :param bbox: (min_lat, min_lon, max_lat, max_lon) or [min_lat, min_lon, max_lat, max_lon]
        :param icao24: Single 24-bit ICAO hex code or list of hex codes.
        :param unix_time: Unix timestamp in seconds (optional).
        """
        params = {}
        if bbox and len(bbox) == 4:
            params["lamin"] = bbox[0]
            params["lomin"] = bbox[1]
            params["lamax"] = bbox[2]
            params["lomax"] = bbox[3]

        if icao24:
            if isinstance(icao24, list):
                params["icao24"] = ",".join(i.lower().strip() for i in icao24)
            else:
                params["icao24"] = icao24.lower().strip()

        if unix_time:
            params["time"] = unix_time

        data, _ = self.transport.request("/states/all", params=params)
        raw_states = data.get("states") or []
        return [FlightState.from_api_array(s) for s in raw_states if s and len(s) >= 17]

    def get_flights_by_aircraft(
        self,
        icao24: str,
        begin: int,
        end: int,
    ) -> List[FlightRecord]:
        """
        Retrieve flights for a particular aircraft within a time interval.
        :param icao24: ICAO 24-bit transponder address in hex.
        :param begin: Start time in unix epoch seconds.
        :param end: End time in unix epoch seconds (interval must not exceed 30 days).
        """
        params = {
            "icao24": icao24.lower().strip(),
            "begin": begin,
            "end": end,
        }
        data, _ = self.transport.request("/flights/aircraft", params=params)
        if isinstance(data, list):
            return [FlightRecord.from_api_dict(item) for item in data]
        return []

    def get_arrivals_by_airport(
        self,
        airport_icao: str,
        begin: int,
        end: int,
    ) -> List[FlightRecord]:
        """
        Retrieve flights arriving at a given airport within a time interval (max 7 days).
        :param airport_icao: 4-letter ICAO airport code (e.g. 'VVNB', 'VVDN', 'ZGGG').
        """
        params = {
            "airport": airport_icao.upper().strip(),
            "begin": begin,
            "end": end,
        }
        data, _ = self.transport.request("/flights/arrival", params=params)
        if isinstance(data, list):
            return [FlightRecord.from_api_dict(item) for item in data]
        return []

    def get_departures_by_airport(
        self,
        airport_icao: str,
        begin: int,
        end: int,
    ) -> List[FlightRecord]:
        """
        Retrieve flights departing from a given airport within a time interval (max 7 days).
        :param airport_icao: 4-letter ICAO airport code (e.g. 'VVNB', 'VVDN', 'ZGGG').
        """
        params = {
            "airport": airport_icao.upper().strip(),
            "begin": begin,
            "end": end,
        }
        data, _ = self.transport.request("/flights/departure", params=params)
        if isinstance(data, list):
            return [FlightRecord.from_api_dict(item) for item in data]
        return []

    def get_track(
        self,
        icao24: str,
        unix_time: int = 0,
    ) -> Optional[FlightTrack]:
        """
        Retrieve flight trajectory for an aircraft at a given time point.
        """
        params = {
            "icao24": icao24.lower().strip(),
            "time": unix_time,
        }
        data, _ = self.transport.request("/tracks/all", params=params)
        if data and isinstance(data, dict) and "path" in data:
            return FlightTrack.from_api_dict(data)
        return None

    def get_rate_limit_status(self) -> RateLimitStatus:
        """
        Return the current rate limit and token status.
        """
        return self.transport.last_rate_limit

    def health_check(self) -> dict:
        """
        Validate connectivity, credential resolution, and token acquisition.
        """
        auth_mode = self.transport.auth_source
        token_valid = False
        token_error = None
        if self.transport.client_id:
            try:
                token = self.transport.get_valid_token()
                token_valid = bool(token)
            except Exception as e:
                token_error = str(e)

        return {
            "status": "healthy" if (token_valid or auth_mode == "anonymous") else "degraded",
            "auth_source": auth_mode,
            "client_id": self.transport.client_id[:8] + "..." if self.transport.client_id else None,
            "token_valid": token_valid,
            "token_error": token_error,
            "daily_allowance": self.transport.last_rate_limit.daily_allowance,
            "remaining_credits": self.transport.last_rate_limit.remaining_credits,
        }
