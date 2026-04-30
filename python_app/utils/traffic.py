import os
import requests
import streamlit as st

MAPBOX_ACCESS_TOKEN = st.secrets["GEOAPIFY_API_KEY"]

def get_travel_time(start_lat: float, start_lng: float, end_lat: float, end_lng: float):
    """
    Fetches travel time from Mapbox Directions API.
    Returns duration (seconds), distance (meters), and traffic congestion level.
    """
    if not MAPBOX_ACCESS_TOKEN:
        dist_deg = ((start_lat - end_lat)**2 + (start_lng - end_lng)**2)**0.5
        dist_km = dist_deg * 111
        duration_hours = dist_km / 30
        duration_seconds = duration_hours * 3600
        
        return {
            "duration": int(duration_seconds),
            "distance": int(dist_km * 1000),
            "traffic_congestion": "low"
        }

    try:
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{start_lng},{start_lat};{end_lng},{end_lat}?access_token={MAPBOX_ACCESS_TOKEN}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not data.get('routes'):
            return None

        route = data['routes'][0]
        duration = route['duration'] # seconds
        distance = route['distance'] # meters
        
        speed_mps = distance / duration if duration > 0 else 10
        speed_kmh = speed_mps * 3.6
        
        congestion = "low"
        if speed_kmh < 15:
            congestion = "severe"
        elif speed_kmh < 30:
            congestion = "heavy"
        elif speed_kmh < 50:
            congestion = "moderate"

        return {
            "duration": duration,
            "distance": distance,
            "traffic_congestion": congestion
        }
    except Exception as e:
        print(f"Error fetching traffic: {e}")
        return None
