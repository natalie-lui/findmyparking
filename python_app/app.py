import streamlit as st
import pandas as pd
import struct
import binascii
import pydeck as pdk
from utils.supabase_client import get_supabase_client
from utils.weather import get_weather
from utils.traffic import get_travel_time
from utils.geocoding import geocode_address

# Set page config
st.set_page_config(page_title="FindMyParking", layout="wide")

# Initialize Supabase
supabase = get_supabase_client()

st.sidebar.title("FindMyParking 🚗")
st.sidebar.markdown("Personalized Parking Recommendations")

# User Inputs
user_lat = 33.6405
user_lng = -117.8443
st.sidebar.write(f"**Current Location:** UCI ({user_lat}, {user_lng})")

# Input Destination
st.sidebar.write("Your Destination")

dest_query = st.sidebar.text_input(
    "Enter your destination: ",
    placeholder = "e.g. UCI Student Center"
)

suggestions = geocode_address(dest_query, user_lat, user_lng)

destination = None
dest_lat = None
dest_lng = None

if suggestions:
    selected_place = st.sidebar.selectbox(
        "Select a location",
        options=suggestions,
        format_func=lambda x: x["name"]
    )

    if selected_place:
        dest_lat = selected_place["lat"]
        dest_lng = selected_place["lng"]
        st.sidebar.success(f"Selected: {selected_place['name']}")
        destination = selected_place

max_cost = st.sidebar.slider("Max Cost per Hour ($)", 0.0, 10.0, 5.0, 0.5)
pref_covered = st.sidebar.checkbox("Prefer Covered Parking")
pref_accessible = st.sidebar.checkbox("Prefer Accessible Parking")


weather = get_weather(user_lat, user_lng)

col1, col2, col3 = st.columns(3)
col1.metric("Weather", f"{weather['condition']}", f"{weather['temp']}°C")
col2.metric("Rain Status", "Raining" if weather['is_raining'] else "Clear")


try:
    response = supabase.table('parking_spots').select("*").execute()
    spots = response.data
except Exception as e:
    st.error(f"Error fetching spots: {e}")
    spots = []

if not spots:
    st.warning("No parking spots found. Run seed script or check database.")
    st.stop()

# 3. Ranking Algorithm

def parse_location(location_data):
    """
    Parses location data from Supabase/PostGIS.
    Handles:
    1. WKT String (e.g. "POINT(-117.8443 33.6405)")
    2. WKB Hex String (e.g. "0101000020E6100000...")
    Returns (longitude, latitude) as floats.
    """
    try:
        if isinstance(location_data, str) and location_data.startswith("POINT"):
            val = location_data.replace('POINT','').replace('(','').replace(')','')
            lng, lat = map(float, val.split())
            return lng, lat
            
        if isinstance(location_data, str):
            data = binascii.unhexlify(location_data)

            endian = data[0]
            fmt = '<' if endian == 1 else '>'
            offset = 5
            
            wkb_type = struct.unpack(fmt + 'I', data[1:5])[0]
            if (wkb_type & 0x20000000):
                offset += 4
            
            x = struct.unpack(fmt + 'd', data[offset:offset+8])[0]
            y = struct.unpack(fmt + 'd', data[offset+8:offset+16])[0]
            return x, y
            
    except Exception as e:
        pass
        
    return None, None

#stop ranking if destination not selected
if dest_lat is None or dest_lng is None:
    st.stop()

ranked_spots = []

for spot in spots:
    lng, lat = parse_location(spot['location'])
    
    if lat is None or lng is None:
        lat, lng = user_lat + 0.001, user_lng + 0.001 

    #calculate travel times
    #curr -> parking
    traffic_to_spot = get_travel_time(user_lat, user_lng, lat, lng)
    duration_to_spot = traffic_to_spot['duration'] if traffic_to_spot else 0

    #parking -> destination
    traffic_to_dest = get_travel_time(lat, lng, dest_lat, dest_lng)
    duration_to_dest = traffic_to_dest['duration'] if traffic_to_dest else 0

    #convert time
    drive_minutes = duration_to_spot / 60
    walk_minutes = duration_to_dest / 60
    total_minutes = drive_minutes + walk_minutes

    score = 70 # base score
    
    score -= drive_minutes * 1.2
    score -= walk_minutes * 2.5 #walking = penalized heavier
    
    cost = spot['cost_per_hour'] #cost
    score -= cost * 2
    if cost < 3: score += 5
    
    features = spot.get('features', []) # weather
    is_covered = "Covered" in features
    
    if weather['is_raining']:
        if is_covered: score += 30
        else: score -= 20
        
    if pref_covered and not is_covered:
        continue # Skip uncovered spots if preference is set
    if cost > max_cost:
        continue # Skip spots that are too expensive

    ranked_spots.append({
        "name": spot['name'],
        "score": int(score),
        "cost": f"${cost}/hr",
        "drive_time": f"{int(drive_minutes)} min",
        "walk_time": f"{int(walk_minutes)} min",
        "total_time": f"{int(total_minutes)} min",
        "features": ", ".join(features),
        "lat": lat,
        "lon": lng,
        "why": "Covered & Close" if is_covered and total_minutes < 5 else "Best Value"
    })

#sorting
df = pd.DataFrame(ranked_spots)
if not df.empty:
    df = df.sort_values(by="score", ascending=False)
st.subheader("Parking Map")
if not df.empty:
    df['color'] = [[255, 0, 0, 160]] * len(df)
    df.at[df.index[0], 'color'] = [0, 255, 0, 200] 
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=100,
        pickable=True,
    )
    
    view_state = pdk.ViewState(latitude=user_lat, longitude=user_lng, zoom=14)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}\nScore: {score}\nCost: {cost}"})
    st.pydeck_chart(r)

st.subheader("Recommended Spots")
if not df.empty:
    # Show only top 5 unique spots
    top_5_df = df.head(5)
    for idx, (index, row) in enumerate(top_5_df.iterrows(), 1):
        with st.expander(f"#{idx} - {row['name']} (Score: {row['score']})"):
            st.write(f"**Cost**: {row['cost']}")
            st.write(f"**Drive Time**: {row['drive_time']}")
            st.write(f"**Walk Time**: {row['walk_time']}")
            st.write(f"**Total Trip Time**: {row['total_time']}")
            st.write(f"**Features**: {row['features']}")
            st.write(f"**Why**: {row['why']}")
else:
    st.write("No spots match your criteria.")
