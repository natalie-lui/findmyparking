import requests
import streamlit as st

@st.cache_data(ttl=3600)
def get_parking_spots_near(lat, lng, radius=2000):
    """
    generate set of spots near a destination's [lat,lng]
    """

    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      node["amenity"="parking"](around:{radius},{lat},{lng});
      way["amenity"="parking"](around:{radius},{lat},{lng});
      relation["amenity"="parking"](around:{radius},{lat},{lng});
    );
    out center;
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

        # Extract coordinates
        if "lat" in element:
            el_lat = element["lat"]
            el_lon = element["lon"]
        else:
            el_lat = element["center"]["lat"]
            el_lon = element["center"]["lon"]

        # Prevent duplicates
        coord_key = (round(el_lat, 5), round(el_lon, 5))
        if coord_key in seen:
            continue
        seen.add(coord_key)

        tags = element.get("tags", {})
        features = []

        #detect covered parking
        covered = tags.get("covered")
        parking_type = tags.get("parking")

        if covered == "yes":
            features.append("Covered")

        elif parking_type in ["multi-storey", "underground"]:
            features.append("Covered")

        # detect accessibility
        wheelchair = tags.get("wheelchair")

        if wheelchair == "yes":
            features.append("Accessible")

        elif wheelchair == "limited":
            features.append("Partially Accessible")

        # Pull parking lot name
        name = tags.get("name", "Parking Lot")

        # detect cost
        cost = 0

        if "charge:hourly" in tags:
            try:
                cost = float(tags["charge:hourly"])
            except:
                cost = 3

        elif "charge" in tags:
            try:
                cost = float(tags["charge"].replace("$", ""))
            except:
                cost = 3

        elif tags.get("fee") == "yes":
            cost = 3

        elif tags.get("fee") == "no":
            cost = 0

        spots.append({
            "name": name,
            "lat": el_lat,
            "lon": el_lon,
            "features": features,
            "cost_per_hour": cost
        })

    return spots