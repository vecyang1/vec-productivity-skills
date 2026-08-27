#!/usr/bin/env python3
"""
OpenSky Network CLI - Real-time Air Traffic Radar & Flight Tracking
"""
import argparse
import csv
import io
import json
import sys
import time
from datetime import datetime, timezone
from typing import List

from opensky.api import OpenSkyAPI
from opensky.models import FlightRecord, FlightState, FlightTrack


def _parse_time(time_str: str) -> int:
    """Parse date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) or unix integer."""
    time_str = time_str.strip()
    if time_str.isdigit():
        return int(time_str)
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(time_str, fmt).replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except ValueError:
            continue
    raise ValueError(f"Invalid time format '{time_str}'. Use 'YYYY-MM-DD' or unix timestamp.")


def _format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Render a clean text table with aligned columns."""
    if not rows:
        return "(No records found)"
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    row_lines = [
        " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(r))
        for r in rows
    ]
    return f"{header_line}\n{sep_line}\n" + "\n".join(row_lines)


def cmd_auth_check(api: OpenSkyAPI, args: argparse.Namespace):
    """Run credential check, OAuth2 token validity, and quota status."""
    print("Checking OpenSky Network API authentication and connectivity...")
    hc = api.health_check()
    rl = api.get_rate_limit_status()

    output = {
        "status": hc["status"],
        "auth_source": hc["auth_source"],
        "client_id_preview": hc["client_id"],
        "token_valid": hc["token_valid"],
        "daily_allowance_credits": rl.daily_allowance,
        "remaining_credits": rl.remaining_credits,
        "token_error": hc["token_error"],
    }

    if args.format == "json":
        print(json.dumps(output, indent=2))
        return

    print("\n--- OpenSky API Status ---")
    print(f"Health Status      : {'✅ ' + hc['status'].upper() if hc['status'] == 'healthy' else '⚠️ ' + hc['status'].upper()}")
    print(f"Auth Source        : {hc['auth_source']}")
    print(f"Client ID          : {hc['client_id'] or 'None (Anonymous)'}")
    print(f"Token Verification : {'✅ Verified Active' if hc['token_valid'] else ('⚠️ Skipped (Anonymous)' if hc['auth_source'] == 'anonymous' else '❌ Failed: ' + str(hc['token_error']))}")
    print(f"Daily Allowance    : {rl.daily_allowance:,} credits/day")
    print(f"Live Remaining     : {str(rl.remaining_credits) + ' credits' if rl.remaining_credits is not None else 'Available upon first data request'}")
    print("--------------------------\n")


def cmd_radar(api: OpenSkyAPI, args: argparse.Namespace):
    """Query live aircraft state vectors with filters and bounding box."""
    bbox = None
    if args.bbox and len(args.bbox) == 4:
        bbox = [float(x) for x in args.bbox]

    icao_filter = [i.strip() for i in args.icao24.split(",")] if args.icao24 else None

    states = api.get_states(bbox=bbox, icao24=icao_filter)

    # Post-filtering by callsign or country if specified
    if args.callsign:
        target_cs = args.callsign.upper().strip()
        states = [s for s in states if target_cs in s.callsign.upper()]
    if args.country:
        target_co = args.country.lower().strip()
        states = [s for s in states if target_co in s.origin_country.lower()]

    if args.limit and args.limit > 0:
        states = states[: args.limit]

    rl = api.get_rate_limit_status()

    if args.format == "json":
        data = {
            "count": len(states),
            "remaining_credits": rl.remaining_credits,
            "states": [s.to_dict() for s in states],
        }
        print(json.dumps(data, indent=2))
        return

    if args.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ICAO24", "Callsign", "Country", "Lat", "Lon", "Alt_m", "Speed_kmh", "Heading_deg", "VerticalRate_fpm", "OnGround"])
        for s in states:
            writer.writerow([
                s.icao24, s.callsign, s.origin_country, s.latitude, s.longitude,
                s.baro_altitude, s.speed_kmh, s.true_track, s.vertical_rate_fpm, s.on_ground
            ])
        print(output.getvalue().strip())
        return

    # Table format
    headers = ["ICAO24", "Callsign", "Country", "Lat/Lon", "Altitude", "Speed", "Heading", "V/S", "Status"]
    rows = []
    for s in states:
        pos_str = f"{s.latitude:.3f}, {s.longitude:.3f}" if s.latitude is not None and s.longitude is not None else "N/A"
        alt_str = f"{int(s.altitude_ft)}ft" if s.altitude_ft is not None else (f"{int(s.baro_altitude)}m" if s.baro_altitude else "0")
        speed_str = f"{int(s.speed_kmh)} km/h" if s.speed_kmh is not None else "0"
        head_str = f"{int(s.true_track)}°" if s.true_track is not None else "-"
        vs_str = f"{int(s.vertical_rate_fpm)} fpm" if s.vertical_rate_fpm is not None else "-"
        status_str = "Ground" if s.on_ground else "Airborne"
        rows.append([s.icao24, s.callsign or "-", s.origin_country[:15], pos_str, alt_str, speed_str, head_str, vs_str, status_str])

    print(f"\n--- OpenSky Radar Live Telemetry ({len(states)} Aircraft) ---")
    print(_format_table(headers, rows))
    if rl.remaining_credits is not None:
        print(f"\n[Quota] Remaining Daily Credits: {rl.remaining_credits:,}")
    print()


def cmd_flights(api: OpenSkyAPI, args: argparse.Namespace):
    """Query airport arrivals/departures or aircraft flights."""
    now = int(time.time())
    begin = _parse_time(args.begin) if args.begin else (now - 86400)
    end = _parse_time(args.end) if args.end else now

    if args.airport:
        if args.type == "departure":
            records = api.get_departures_by_airport(args.airport, begin, end)
        else:
            records = api.get_arrivals_by_airport(args.airport, begin, end)
    elif args.icao24:
        records = api.get_flights_by_aircraft(args.icao24, begin, end)
    else:
        sys.stderr.write("Error: Either --airport (e.g. VVNB) or --icao24 must be specified.\n")
        sys.exit(1)

    if args.limit and args.limit > 0:
        records = records[: args.limit]

    rl = api.get_rate_limit_status()

    if args.format == "json":
        print(json.dumps({
            "count": len(records),
            "remaining_credits": rl.remaining_credits,
            "flights": [r.to_dict() for r in records],
        }, indent=2))
        return

    headers = ["ICAO24", "Callsign", "Departure", "Arrival", "First Seen (UTC)", "Last Seen (UTC)"]
    rows = []
    for r in records:
        t_first = datetime.fromtimestamp(r.first_seen, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if r.first_seen else "-"
        t_last = datetime.fromtimestamp(r.last_seen, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if r.last_seen else "-"
        rows.append([r.icao24, r.callsign or "-", r.est_departure_airport or "-", r.est_arrival_airport or "-", t_first, t_last])

    print(f"\n--- OpenSky Flight Records ({len(records)} Flights) ---")
    print(_format_table(headers, rows))
    if rl.remaining_credits is not None:
        print(f"\n[Quota] Remaining Daily Credits: {rl.remaining_credits:,}")
    print()


def cmd_track(api: OpenSkyAPI, args: argparse.Namespace):
    """Retrieve aircraft trajectory waypoints."""
    if not args.icao24:
        sys.stderr.write("Error: --icao24 is required for trajectory lookup.\n")
        sys.exit(1)

    t_val = _parse_time(args.time) if args.time else 0
    track = api.get_track(args.icao24, unix_time=t_val)

    if not track or not track.path:
        print(f"No trajectory track found for aircraft {args.icao24}.")
        return

    if args.format == "json":
        print(json.dumps(track.to_dict(), indent=2))
        return

    headers = ["Time (UTC)", "Lat", "Lon", "Alt (m)", "Heading", "On Ground"]
    rows = []
    for pt in track.path[:args.limit or 50]:
        t_str = datetime.fromtimestamp(pt[0], tz=timezone.utc).strftime("%H:%M:%S") if len(pt) > 0 and pt[0] else "-"
        lat_str = f"{pt[1]:.4f}" if len(pt) > 1 and pt[1] is not None else "-"
        lon_str = f"{pt[2]:.4f}" if len(pt) > 2 and pt[2] is not None else "-"
        alt_str = f"{int(pt[3])}" if len(pt) > 3 and pt[3] is not None else "-"
        head_str = f"{int(pt[4])}°" if len(pt) > 4 and pt[4] is not None else "-"
        ground_str = "Yes" if len(pt) > 5 and pt[5] else "No"
        rows.append([t_str, lat_str, lon_str, alt_str, head_str, ground_str])

    print(f"\n--- Aircraft Trajectory Track [{track.icao24} | Callsign: {track.callsign or '-'}] ({len(track.path)} Waypoints) ---")
    print(_format_table(headers, rows))
    print()


def main():
    # Common format argument
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format (default: table)")
    parent_parser.add_argument("--client-id", help="OpenSky API Client ID (defaults to 1Password / env)")
    parent_parser.add_argument("--client-secret", help="OpenSky API Client Secret (defaults to 1Password / env)")

    parser = argparse.ArgumentParser(
        description="OpenSky Network CLI - Real-time Air Traffic Radar & Flight Tracking",
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # auth-check / quota
    p_auth = subparsers.add_parser("auth-check", aliases=["quota"], parents=[parent_parser], help="Check credential status, OAuth2 token validity, and rate limit credits")
    p_auth.set_defaults(func=cmd_auth_check)

    # radar / states
    p_radar = subparsers.add_parser("radar", aliases=["states"], parents=[parent_parser], help="Live aircraft radar telemetry and positions")
    p_radar.add_argument("--bbox", nargs=4, type=float, metavar=("MIN_LAT", "MIN_LON", "MAX_LAT", "MAX_LON"), help="Bounding box filter (e.g. 21.0 105.0 22.5 106.5)")
    p_radar.add_argument("--callsign", help="Filter by airline callsign substring (e.g. HVN, CCA, AFR)")
    p_radar.add_argument("--country", help="Filter by origin country (e.g. Vietnam, China, United States)")
    p_radar.add_argument("--icao24", help="Filter by 24-bit ICAO transponder hex (comma-separated)")
    p_radar.add_argument("--limit", type=int, default=25, help="Maximum number of rows to return (default: 25)")
    p_radar.set_defaults(func=cmd_radar)

    # flights
    p_flights = subparsers.add_parser("flights", parents=[parent_parser], help="Historical or active airport flights")
    p_flights.add_argument("--airport", help="4-letter ICAO airport code (e.g. VVNB, VVDN, ZGGG)")
    p_flights.add_argument("--type", choices=["arrival", "departure"], default="arrival", help="Arrivals or departures (default: arrival)")
    p_flights.add_argument("--icao24", help="Filter by aircraft 24-bit ICAO address")
    p_flights.add_argument("--begin", help="Start time (YYYY-MM-DD or unix timestamp)")
    p_flights.add_argument("--end", help="End time (YYYY-MM-DD or unix timestamp)")
    p_flights.add_argument("--limit", type=int, default=20, help="Maximum number of records to return (default: 20)")
    p_flights.set_defaults(func=cmd_flights)

    # track
    p_track = subparsers.add_parser("track", parents=[parent_parser], help="Aircraft trajectory track history")
    p_track.add_argument("--icao24", required=True, help="24-bit ICAO address of the aircraft")
    p_track.add_argument("--time", help="Unix timestamp or YYYY-MM-DD for trajectory point")
    p_track.add_argument("--limit", type=int, default=40, help="Max waypoints to display")
    p_track.set_defaults(func=cmd_track)

    args = parser.parse_args()

    api = OpenSkyAPI(
        client_id=args.client_id,
        client_secret=getattr(args, "client_secret", None),
    )

    try:
        args.func(api, args)
    except Exception as e:
        sys.stderr.write(f"\n[ERROR] {e}\n\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
