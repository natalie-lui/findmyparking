import requests
import os

GEOAPIFY_KEY = st.secrets["GEOAPIFY_API_KEY"]

def reverse_geocode(lat, lon):
    """Convert lat/lon to a human-readable address using Geoapify."""
    try:
        url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={GEOAPIFY_KEY}"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        features = data.get("features", [])
        if features:
            props = features[0].get("properties", {})
            # Build a short address: street number + street + city
            parts = [
                props.get("housenumber", ""),
                props.get("street", ""),
                props.get("city", ""),
            ]
            address = " ".join(p for p in parts if p)
            return address if address else props.get("formatted", "Address unavailable")
        return "Address unavailable"
    except:
        return "Address unavailable"