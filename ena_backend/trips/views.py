from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.route_service import get_route
from .services.hos_engine import simulate_trip
from datetime import datetime

@api_view(['POST'])
def create_trip(request):
    data = request.data

    route = get_route(
        data["current_location"],
        data["pickup"],
        data["dropoff"],
    )

    print("Route recieved:", data)

    logs = simulate_trip(
        distance_miles=route["distance"],
        # start_time=datetime.now(),
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0),
        cycle_used=data["cycle_used"]
    )

    return Response({
    "route": route,
    "logs": logs,
    "summary": {
        "total_days": len(logs),
        "total_distance": route["distance"],
        "total_hours": route["duration"],
        "cycle_used": data["cycle_used"]
    }
})