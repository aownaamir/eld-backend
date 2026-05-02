import requests
import os
from dotenv import load_dotenv
load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

import requests
import urllib.parse

def geocode(place):
    encoded_place = urllib.parse.quote(place)

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_place}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "limit": 1
    }

    res = requests.get(url, params=params)
    data = res.json()

    if "features" not in data:
        raise Exception(f"Geocoding failed: {data}")

    if not data["features"]:
        raise Exception(f"Location not found: {place}")

    return data["features"][0]["center"]

def get_route(current, pickup, dropoff):
    start = geocode(current)
    pick = geocode(pickup)
    end = geocode(dropoff)

    coordinates = f"{start[0]},{start[1]};{pick[0]},{pick[1]};{end[0]},{end[1]}"

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}"

    params = {
        "access_token": MAPBOX_TOKEN,
        "geometries": "geojson"
    }

    res = requests.get(url, params=params).json()

    route = res["routes"][0]

    distance_miles = route["distance"] / 1609  # meters into miles
    duration_hours = route["duration"] / 3600  # seconds into hours

    geometry = route["geometry"]["coordinates"]

    return {
        "distance": round(distance_miles, 2),
        "duration": round(duration_hours, 2),
        "geometry": geometry
    }