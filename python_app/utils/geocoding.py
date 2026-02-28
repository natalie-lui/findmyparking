import os
import requests
import urllib.parse


MAPBOX_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

def geocode_address(address, user_lat, user_lng):
    #no destination inputted
    if not address:
        return None
    
    encoded_query = urllib.parse.quote(address)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_query}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "autocomplete": "true",
        "limit": 5,
        "proximity": f"{user_lng},{user_lat}"
    }

    response = requests.get(url, params=params)
    data = response.json()

    #return coordinates
    results = []
    for feature in data.get("features", []):
        results.append({
            "name": feature["place_name"],
            "lat": feature["center"][1],
            "lng": feature["center"][0]
        })

    return results