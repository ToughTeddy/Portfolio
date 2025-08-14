import requests as r
import my_position as me


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
        sunrise = int(sun_data["results"]["sunrise"].split("T")[1].split(":")[0])
        sunset = int(sun_data["results"]["sunset"].split("T")[1].split(":")[0])
    except:
        sunrise, sunset = 0, 0

    return sunrise, sunset

# print(sunrise_sunset())