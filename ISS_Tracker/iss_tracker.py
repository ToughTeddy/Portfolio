import os
import requests as r

def _env_float(name: str) -> float:
    val = os.getenv(name)
    if val is None or val.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    try:
        return float(val)
    except ValueError:
        raise RuntimeError(f"{name} must be a number (got '{val}')")

# Required coords (strings in env; parsed to float)
MY_LAT  = _env_float("MY_LAT")
MY_LONG = _env_float("MY_LONG")
PROX_DEG = float(os.getenv("PROX_DEG", "45"))

def iss_position():
    """Return (lat, lon) of the ISS as floats, or (0.0, 0.0) on error."""
    try:
        resp = r.get("http://api.open-notify.org/iss-now.json", timeout=20)
        resp.raise_for_status()
        data = resp.json()

        lat = float(data["iss_position"]["latitude"])
        lon = float(data["iss_position"]["longitude"])
        return lat, lon

    except r.Timeout:
        print("Error: ISS API request timed out.")
    except r.HTTPError as e:
        code = e.response.status_code if e.response is not None else "unknown"
        print(f"Error: ISS API HTTP {code}.")
    except r.ConnectionError as e:
        print(f"Error: connection error: {e}")
    except r.RequestException as e:
        print(f"Error: request failed: {e}")
    except Exception as e:
        print(f"Unknown exception: {e}")

    return 0.0, 0.0

def iss_close_check() -> bool:
    """
    True if ISS is within a ±PROX_DEG degree box around (MY_LAT, MY_LONG).
    """
    iss_lat, iss_lon = iss_position()
    if iss_lat == 0.0 and iss_lon == 0.0:
        return False

    lat_ok = (MY_LAT - PROX_DEG) <= iss_lat <= (MY_LAT + PROX_DEG)
    lon_ok = (MY_LONG - PROX_DEG) <= iss_lon <= (MY_LONG + PROX_DEG)
    return lat_ok and lon_ok