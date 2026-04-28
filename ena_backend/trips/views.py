from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# @api_view(['POST'])
# def create_trip(request):
#     data = request.data

#     return Response({
#         "message": "Trip API working",
#         "input": data
#     })


from .services.route_service import get_route
from .services.hos_engine import simulate_trip
from datetime import datetime

@api_view(['POST'])
def create_trip(request):
    data = request.data

    route = get_route(
        data["current_location"],
        data["pickup"],
        data["dropoff"]
    )

    print("Route recieved:", data)

    logs = simulate_trip(
        distance_miles=route["distance"],
        start_time=datetime.now(),
        cycle_used=data["cycle_used"]
    )

    return Response({
    "route": route,
    "logs": logs,
    "summary": {
        "total_days": len(logs),
        "total_distance": route["distance"],
        "total_hours": route["duration"]
    }
})

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

    distance_miles = route["distance"] / 1609  # meters → miles
    duration_hours = route["duration"] / 3600  # seconds → hours

    geometry = route["geometry"]["coordinates"]

    return {
        "distance": round(distance_miles, 2),
        "duration": round(duration_hours, 2),
        "geometry": geometry
    }