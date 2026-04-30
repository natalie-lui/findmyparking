import requests
import streamlit as st

def get_travel_time(start_lat: float, start_lng: float, end_lat: float, end_lng: float):
    try:
        MAPBOX_ACCESS_TOKEN = st.secrets["MAPBOX_ACCESS_TOKEN"]  # ✅ correct key
    except:
        MAPBOX_ACCESS_TOKEN = None

    # Fallback if no token
    if not MAPBOX_ACCESS_TOKEN:
        dist_deg = ((start_lat - end_lat)**2 + (start_lng - end_lng)**2)**0.5
        dist_km = dist_deg * 111
        duration_seconds = (dist_km / 30) * 3600
        return {
            "duration": int(duration_seconds),
            "distance": int(dist_km * 1000),
            "traffic_congestion": "low"
        }

    try:
        url = (
            f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"
            f"{start_lng},{start_lat};{end_lng},{end_lat}"
            f"?access_token={MAPBOX_ACCESS_TOKEN}"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not data.get('routes'):
            return None

        route = data['routes'][0]
        duration = route['duration']
        distance = route['distance']

        speed_kmh = (distance / duration) * 3.6 if duration > 0 else 10
        if speed_kmh < 15:
            congestion = "severe"
        elif speed_kmh < 30:
            congestion = "heavy"
        elif speed_kmh < 50:
            congestion = "moderate"
        else:
            congestion = "low"

        return {
            "duration": duration,
            "distance": distance,
            "traffic_congestion": congestion
        }
    except Exception as e:
        print(f"Error fetching traffic: {e}")
        return None