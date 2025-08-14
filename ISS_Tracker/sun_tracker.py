import requests as r
import my_info as me
import datetime as dt


# The sunrise-sunset api is default to the utc timezone. You need to go to the
# api docs to find the proper wording for your timezone.
def sunrise_sunset():
    parameters = {
        "lat": me.MY_LAT,
        "lng": me.MY_LONG,
        "formatted": 0,
        "tzid": "America/Phoenix" # Change to your timezone.
    }
    try:
        sun = r.get("https://api.sunrise-sunset.org/json", params=parameters)
        sun.raise_for_status()
        sun_data = sun.json()

        sunrise_iso = sun_data["results"]["sunrise"]
        sunset_iso = sun_data["results"]["sunset"]

        sunrise_hour, sunrise_minute = map(int, sunrise_iso.split("T")[1].split(":")[:2])
        sunset_hour, sunset_minute = map(int, sunset_iso.split("T")[1].split(":")[:2])

        return dt.time(sunrise_hour, sunrise_minute), dt.time(sunset_hour, sunset_minute)

    except Exception as e:
        print(f"Error fetching sunrise/sunset data: {e}")
        return dt.time(0, 0), dt.time(0, 0)

# print(sunrise_sunset())

def dark_check():
    sunrise_time, sunset_time = sunrise_sunset()
    now_time = dt.datetime.now().time()
    # print(now_time)

    if sunrise_time == dt.time(0, 0) and sunset_time == dt.time(0, 0):
        print(f"Now: {now_time.strftime('%H:%M')}  Sunrise: --:--  Sunset: --:--")
        return False

    if sunrise_time <= sunset_time:
        is_dark = (now_time < sunrise_time) or (now_time > sunset_time)
    else:
        is_dark = (sunset_time < now_time) and (now_time < sunrise_time)

        print(f"Now: {now_time.strftime('%H:%M')}  Sunrise: {sunrise_time.strftime('%H:%M')}  "
              f"Sunset: {sunset_time.strftime('%H:%M')}")
    return is_dark

# print(dark_check())