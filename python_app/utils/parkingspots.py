import requests
import streamlit as st

@st.cache_data(ttl=3600)
def get_parking_spots_near(lat, lng, radius=2000):
    """
    return parking spots near user's location using GEOAPIFY
    """

    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="parking"](around:{radius},{lat},{lng});
      way["amenity"="parking"](around:{radius},{lat},{lng});
      relation["amenity"="parking"](around:{radius},{lat},{lng});
    );
    out center 25;
    """

    try:
        response = requests.post(overpass_url, data=query, timeout=60)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        st.error(f"Error fetching parking data: {e}")
        return []

    spots = []
    seen = set()

    for element in data.get("elements", []):

        # get lat/lng
        if "lat" in element:
            el_lat = element["lat"]
            el_lon = element["lon"]
        else:
            el_lat = element["center"]["lat"]
            el_lon = element["center"]["lon"]

        # remove duplicates
        coord_key = (round(el_lat, 5), round(el_lon, 5))
        if coord_key in seen:
            continue
        seen.add(coord_key)

        tags = element.get("tags", {})
        features = []

        # covered parking detection
        parking_type = tags.get("parking")
        covered = tags.get("covered")

        if covered == "yes" or parking_type in ["multi-storey", "underground"]:
            features.append("Covered")

        # accessibility detection
        wheelchair = tags.get("wheelchair")

        if wheelchair == "yes":
            features.append("Accessible")
        elif wheelchair == "limited":
            features.append("Partially Accessible")

        name = tags.get("name", "Parking Lot")

        # cost detection
        cost = 0

        if "charge:hourly" in tags:
            try:
                cost = float(tags["charge:hourly"])
            except:
                pass

        elif "charge" in tags:
            try:
                cost = float(tags["charge"].replace("$", ""))
            except:
                cost = 3

        elif tags.get("fee") == "no":
            cost = 0

        elif tags.get("fee") == "yes":
            cost = 3

        spots.append({
            "name": name,
            "lat": el_lat,
            "lon": el_lon,
            "features": features,
            "cost_per_hour": cost
        })

    return spots