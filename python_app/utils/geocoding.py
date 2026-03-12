import os
import requests

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

def geocode_address(address, user_lat=None, user_lng=None):
    if not address:
        return []

    url = "https://api.geoapify.com/v1/geocode/autocomplete"
    params = {
        "text": address,
        "apiKey": GEOAPIFY_API_KEY,
        "limit": 5
    }

    # bias by proximity if available
    if user_lat and user_lng:
        params["bias"] = f"proximity:{user_lng},{user_lat}"

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("Geoapify error:", e)
        return []

    results = []
    for feature in data.get("features", []):
        loc = feature.get("properties", {})
        name = loc.get("formatted")
        lat = loc.get("lat")
        lon = loc.get("lon")
        if name and lat and lon:
            results.append({
                "name": name,
                "lat": lat,
                "lng": lon
            })

    # fallback: use current location
    results.append({"name": "Use Current Location", "lat": user_lat, "lng": user_lng})

    return results