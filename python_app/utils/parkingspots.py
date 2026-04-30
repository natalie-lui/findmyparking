import requests
import streamlit as st

@st.cache_data(ttl=3600)
def get_parking_spots_near(lat, lng, radius=2000):
    """
    Generate set of spots near a destination's [lat, lng]
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

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "FindMyParking/1.0"
    }

    try:
        response = requests.post(
            overpass_url,
            data={"data": query},  # ✅ wrap query in dict with "data" key
            headers=headers,
            timeout=60
        )
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
        elif "center" in element:
            el_lat = element["center"]["lat"]
            el_lon = element["center"]["lon"]
        else:
            continue

        # Prevent duplicates
        coord_key = (round(el_lat, 5), round(el_lon, 5))
        if coord_key in seen:
            continue
        seen.add(coord_key)

        tags = element.get("tags", {})
        features = []

        # Detect covered parking
        covered = tags.get("covered")
        parking_type = tags.get("parking")

        if covered == "yes" or parking_type in ["multi-storey", "underground"]:
            features.append("Covered")

        # Detect accessibility
        wheelchair = tags.get("wheelchair")
        if wheelchair == "yes":
            features.append("Accessible")
        elif wheelchair == "limited":
            features.append("Partially Accessible")

        # Detect cost
        cost = 0
        if "charge:hourly" in tags:
            try:
                cost = float(tags["charge:hourly"])
            except:
                cost = 3.0
        elif "charge" in tags:
            try:
                cost = float(tags["charge"].replace("$", "").strip())
            except:
                cost = 3.0
        elif tags.get("fee") == "yes":
            cost = 3.0
        elif tags.get("fee") == "no":
            cost = 0.0

        name = tags.get("name") or tags.get("operator") or f"Parking ({element['id']})"

        spots.append({
            "name": name,
            "lat": el_lat,
            "lon": el_lon,
            "features": features,
            "cost_per_hour": cost
        })

    return spots