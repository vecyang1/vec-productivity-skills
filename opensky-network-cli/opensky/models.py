"""
Data models for OpenSky Network telemetry and flight records.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class FlightState:
    icao24: str
    callsign: str
    origin_country: str
    time_position: Optional[int]
    last_contact: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    baro_altitude: Optional[float]  # meters
    on_ground: bool
    velocity: Optional[float]       # m/s
    true_track: Optional[float]     # degrees
    vertical_rate: Optional[float]  # m/s
    sensors: Optional[List[int]]
    geo_altitude: Optional[float]   # meters
    squawk: Optional[str]
    spi: bool
    position_source: int
    category: int = 0

    @classmethod
    def from_api_array(cls, arr: list) -> "FlightState":
        return cls(
            icao24=str(arr[0] or "").lower(),
            callsign=str(arr[1] or "").strip(),
            origin_country=str(arr[2] or ""),
            time_position=int(arr[3]) if arr[3] is not None else None,
            last_contact=int(arr[4]) if arr[4] is not None else None,
            longitude=float(arr[5]) if arr[5] is not None else None,
            latitude=float(arr[6]) if arr[6] is not None else None,
            baro_altitude=float(arr[7]) if arr[7] is not None else None,
            on_ground=bool(arr[8]) if arr[8] is not None else False,
            velocity=float(arr[9]) if arr[9] is not None else None,
            true_track=float(arr[10]) if arr[10] is not None else None,
            vertical_rate=float(arr[11]) if arr[11] is not None else None,
            sensors=arr[12] if len(arr) > 12 else None,
            geo_altitude=float(arr[13]) if len(arr) > 13 and arr[13] is not None else None,
            squawk=str(arr[14]) if len(arr) > 14 and arr[14] is not None else None,
            spi=bool(arr[15]) if len(arr) > 15 and arr[15] is not None else False,
            position_source=int(arr[16]) if len(arr) > 16 and arr[16] is not None else 0,
            category=int(arr[17]) if len(arr) > 17 and arr[17] is not None else 0,
        )

    @property
    def altitude_ft(self) -> Optional[float]:
        return round(self.baro_altitude * 3.28084, 1) if self.baro_altitude is not None else None

    @property
    def speed_kmh(self) -> Optional[float]:
        return round(self.velocity * 3.6, 1) if self.velocity is not None else None

    @property
    def speed_kts(self) -> Optional[float]:
        return round(self.velocity * 1.94384, 1) if self.velocity is not None else None

    @property
    def vertical_rate_fpm(self) -> Optional[float]:
        return round(self.vertical_rate * 196.85, 1) if self.vertical_rate is not None else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude_m": self.baro_altitude,
            "altitude_ft": self.altitude_ft,
            "velocity_ms": self.velocity,
            "speed_kmh": self.speed_kmh,
            "speed_kts": self.speed_kts,
            "heading_deg": self.true_track,
            "vertical_rate_fpm": self.vertical_rate_fpm,
            "on_ground": self.on_ground,
            "squawk": self.squawk,
            "last_contact": self.last_contact,
        }


@dataclass
class FlightRecord:
    icao24: str
    first_seen: int
    est_departure_airport: Optional[str]
    last_seen: int
    est_arrival_airport: Optional[str]
    callsign: Optional[str]
    est_departure_airport_horiz_distance: Optional[int] = None
    est_departure_airport_vert_distance: Optional[int] = None
    est_arrival_airport_horiz_distance: Optional[int] = None
    est_arrival_airport_vert_distance: Optional[int] = None
    departure_airport_candidates_count: int = 0
    arrival_airport_candidates_count: int = 0

    @classmethod
    def from_api_dict(cls, data: dict) -> "FlightRecord":
        return cls(
            icao24=str(data.get("icao24") or "").lower(),
            first_seen=int(data.get("firstSeen") or 0),
            est_departure_airport=data.get("estDepartureAirport"),
            last_seen=int(data.get("lastSeen") or 0),
            est_arrival_airport=data.get("estArrivalAirport"),
            callsign=str(data.get("callsign") or "").strip(),
            est_departure_airport_horiz_distance=data.get("estDepartureAirportHorizDistance"),
            est_departure_airport_vert_distance=data.get("estDepartureAirportVertDistance"),
            est_arrival_airport_horiz_distance=data.get("estArrivalAirportHorizDistance"),
            est_arrival_airport_vert_distance=data.get("estArrivalAirportVertDistance"),
            departure_airport_candidates_count=int(data.get("departureAirportCandidatesCount") or 0),
            arrival_airport_candidates_count=int(data.get("arrivalAirportCandidatesCount") or 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "departure_airport": self.est_departure_airport,
            "arrival_airport": self.est_arrival_airport,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }


@dataclass
class FlightTrack:
    icao24: str
    callsign: Optional[str]
    start_time: int
    end_time: int
    path: List[List[Any]]  # [[time, lat, lon, baro_alt, true_track, on_ground], ...]

    @classmethod
    def from_api_dict(cls, data: dict) -> "FlightTrack":
        return cls(
            icao24=str(data.get("icao24") or "").lower(),
            callsign=str(data.get("callsign") or "").strip(),
            start_time=int(data.get("startTime") or 0),
            end_time=int(data.get("endTime") or 0),
            path=data.get("path") or [],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "waypoint_count": len(self.path),
            "path": self.path,
        }


@dataclass
class RateLimitStatus:
    remaining_credits: Optional[int]
    daily_allowance: int
    retry_after_seconds: Optional[int]
    auth_mode: str  # "oauth2_client", "anonymous", or "env_credentials"
    token_valid_until: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "remaining_credits": self.remaining_credits,
            "daily_allowance": self.daily_allowance,
            "retry_after_seconds": self.retry_after_seconds,
            "auth_mode": self.auth_mode,
            "token_valid_until": self.token_valid_until,
        }
