import streamlit as st
import pandas as pd
import struct
import binascii
import pydeck as pdk
from utils.supabase_client import get_supabase_client
from utils.weather import get_weather
from utils.traffic import get_travel_time

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

ranked_spots = []

for spot in spots:
    lng, lat = parse_location(spot['location'])
    
    if lat is None or lng is None:
        lat, lng = user_lat + 0.001, user_lng + 0.001 

    traffic = get_travel_time(user_lat, user_lng, lat, lng)
    duration = traffic['duration'] if traffic else 0
    distance = traffic['distance'] if traffic else 0
    
    score = 70 # base score
    
    minutes = duration / 60 #distance
    score -= minutes * 2
    if minutes < 5: score += 10
    
    cost = spot['cost_per_hour'] #cost
    score -= cost * 2
    if cost < 3: score += 5
    
    features = spot.get('features', []) # weather
    is_covered = "Covered" in features
    
    if weather['is_raining']:
        if is_covered: score += 30
        else: score -= 20
        
    if pref_covered and is_covered: score += 15
    if cost > max_cost: score -= 50

    ranked_spots.append({
        "name": spot['name'],
        "score": int(score),
        "cost": f"${cost}/hr",
        "time": f"{int(minutes)} min",
        "features": ", ".join(features),
        "lat": lat,
        "lon": lng,
        "why": "Covered & Close" if is_covered and minutes < 5 else "Best Value"
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
    for idx, row in df.iterrows():
        with st.expander(f"#{idx+1 if isinstance(idx, int) else '?'} - {row['name']} (Score: {row['score']})"):
            st.write(f"**Cost**: {row['cost']}")
            st.write(f"**Travel Time**: {row['time']}")
            st.write(f"**Features**: {row['features']}")
            st.write(f"**Why**: {row['why']}")
else:
    st.write("No spots match your criteria.")
