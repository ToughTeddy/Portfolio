import requests as r
import my_info as me


def iss_position():
    try:
        response = r.get(url="http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
        data = response.json()

        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])

        return iss_latitude, iss_longitude

    except r.Timeout:
        print("Error: ISS API request timed out.")
        return 0.0, 0.0

    except r.HTTPError as e:
        code = e.response.status_code if e.response is not None else "unknown"
        print(f"Error: ISS API HTTP {code}.")
        return 0.0, 0.0

    except r.ConnectionError as e:
        print(f"Error: connection error: {e}")
        return 0.0, 0.0

    except r.RequestException as e:
        print(f"Error: request failed: {e}")
        return 0.0, 0.0

    except Exception as e:
        print(f"Unknown exception: {e}")
        return 0.0, 0.0

# print(iss_position())

def iss_close_check():
    check = False

    iss_lat, iss_long = iss_position()

    if iss_lat != 0 and iss_long != 0:
        if (me.MY_LAT - 5 <= iss_lat <= me.MY_LAT + 5
                and me.MY_LONG - 5 <= iss_long <= me.MY_LONG + 5):
            check = True

    return check

# print(iss_close_check())