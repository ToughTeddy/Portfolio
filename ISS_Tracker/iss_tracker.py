import requests as r
import my_position as me


def iss_position():
    try:
        response = r.get(url="http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
        data = response.json()

        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])
    except:
        iss_latitude = 0
        iss_longitude = 0

    return iss_latitude, iss_longitude

print(iss_position())

