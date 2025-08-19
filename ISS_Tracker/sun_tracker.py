import os
import requests as r
import datetime as dt
from zoneinfo import ZoneInfo


def _env_float(name: str) -> float:
    val = os.getenv(name)
    if val is None or val.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    try:
        return float(val)
    except ValueError:
        raise RuntimeError(f"Environment variable {name} must be a number (got '{val}')")

MY_LAT = _env_float("MY_LAT")
MY_LONG = _env_float("MY_LONG")

# Use explicit TZ if provided; fall back to Azure's WEBSITE_TIME_ZONE; else Phoenix
TZ_NAME = os.getenv("TZ") or os.getenv("WEBSITE_TIME_ZONE") or "America/Phoenix"
TZ = ZoneInfo(TZ_NAME)

ZERO_TIME = dt.time(0, 0)

# The sunrise-sunset api is default to the utc timezone. You need to go to the
# api docs to find the proper wording for your timezone.
def sunrise_sunset():
    """
    Returns (sunrise_local_time, sunset_local_time) as datetime.time objects
    in the configured timezone. Uses sunrise-sunset.org which returns UTC;
    we convert to local time.
    """
    params = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }
    try:
        resp = r.get("https://api.sunrise-sunset.org/json", params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()["results"]

        # Parse UTC timestamps and convert to local TZ
        sr_utc = dt.datetime.fromisoformat(data["sunrise"].replace("Z", "+00:00"))
        ss_utc = dt.datetime.fromisoformat(data["sunset"].replace("Z", "+00:00"))

        sr_local = sr_utc.astimezone(TZ).time()
        ss_local = ss_utc.astimezone(TZ).time()
        return sr_local, ss_local

    except r.Timeout:
        print("Error: sunrise/sunset request timed out.")
    except r.HTTPError as e:
        code = e.response.status_code if e.response is not None else "unknown"
        print(f"Error: sunrise/sunset HTTP {code}.")
    except r.ConnectionError as e:
        print(f"Error: connection error: {e}")
    except r.RequestException as e:
        print(f"Error: request failed: {e}")
    except Exception as e:
        print(f"Unknown exception: {e}")

    return ZERO_TIME, ZERO_TIME

def dark_check() -> bool:
    """
    True if it's currently dark (before sunrise OR after sunset) in the configured TZ.
    Returns False on API error.
    """
    sunrise_time, sunset_time = sunrise_sunset()
    now_time = dt.datetime.now(TZ).time()

    if sunrise_time == ZERO_TIME and sunset_time == ZERO_TIME:
        print(f"Now: {now_time.strftime('%H:%M')}  Sunrise: --:--  Sunset: --:--")
        return False

    if sunrise_time <= sunset_time:
        is_dark = (now_time < sunrise_time) or (now_time > sunset_time)
    else:
        is_dark = (sunset_time < now_time) and (now_time < sunrise_time)

    print(
        f"Now: {now_time.strftime('%H:%M')}  "
        f"Sunrise: {sunrise_time.strftime('%H:%M')}  "
        f"Sunset: {sunset_time.strftime('%H:%M')}  "
        f"Dark: {is_dark}"
    )
    return is_dark