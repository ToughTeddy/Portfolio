import requests as r
import my_info as me


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