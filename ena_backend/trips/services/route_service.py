# import requests
# import os

MAPBOX_TOKEN = "YOUR_TOKEN"

def get_route(start, pickup, dropoff):
    # For now just simulate coordinates
    # You can upgrade later to real API

    return {
        "distance": 2800,  # miles
        "duration": 40,    # hours
        "geometry": []     # frontend will use later
    }