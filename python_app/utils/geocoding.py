import requests
import streamlit as st

def get_api_key():
    try:
        return st.secrets["GEOAPIFY_API_KEY"]
    except:
        import os
        return os.getenv("GEOAPIFY_API_KEY")  # fallback for local dev

def geocode_address(address, user_lat=None, user_lng=None):
    if not address:
        return []

    api_key = get_api_key()
    if not api_key:
        st.error("Missing GEOAPIFY_API_KEY in secrets.")
        return []

    url = "https://api.geoapify.com/v1/geocode/autocomplete"
    params = {
        "text": address,
        "apiKey": api_key,
        "limit": 5
    }

    if user_lat and user_lng:
        params["bias"] = f"proximity:{user_lng},{user_lat}"

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        st.error(f"Geocoding error: {e}")
        return []

    results = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        name = props.get("formatted")
        lat = props.get("lat")
        lon = props.get("lon")
        if name and lat and lon:
            results.append({
                "name": name,
                "lat": lat,
                "lng": lon
            })

    if user_lat and user_lng:
        results.append({"name": "📍 Use Current Location", "lat": user_lat, "lng": user_lng})

    return results