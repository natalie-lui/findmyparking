import streamlit as st
import pandas as pd
import pydeck as pdk
from utils.supabase_client import get_supabase_client
from utils.weather import get_weather
from utils.traffic import get_travel_time

# Set page config
st.set_page_config(page_title="FindMyParking", layout="wide")

# Initialize Supabase
supabase = get_supabase_client()

# --- SIDEBAR ---
st.sidebar.title("FindMyParking 🚗")
st.sidebar.markdown("Personalized Parking Recommendations")

# User Inputs
# For demo, fixed user location (UCI)
user_lat = 33.6405
user_lng = -117.8443
st.sidebar.write(f"**Current Location:** UCI ({user_lat}, {user_lng})")

max_cost = st.sidebar.slider("Max Cost per Hour ($)", 0.0, 10.0, 5.0, 0.5)
pref_covered = st.sidebar.checkbox("Prefer Covered Parking")
pref_accessible = st.sidebar.checkbox("Prefer Accessible Parking")

# --- MAIN CONTENT ---

# 1. Fetch Context
weather = get_weather(user_lat, user_lng)

# Context Widget
col1, col2, col3 = st.columns(3)
col1.metric("Weather", f"{weather['condition']}", f"{weather['temp']}°C")
col2.metric("Rain Status", "Raining" if weather['is_raining'] else "Clear")
# col3 could be traffic summary if we picked a specific route

# 2. Fetch Parking Spots
# Fetch all spots for demo ranking
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
ranked_spots = []

for spot in spots:
    # Extract location (simple handling)
    # PostGIS 'location' comes as WKT/GeoJSON string or binary. 
    # Supabase-py might return it as string representation.
    # For now, let's look for lat/lng columns if they existed, or parse WKT if straightforward.
    # NOTE: In previous setup we relied on `location` column. 
    # Let's assume for this Python demo we can't easily parse WKT without Shapely/GeoPandas.
    # To keep dependencies light, let's simulate location near UCI for the demo if parsing fails,
    # OR better: Assume the seed data put them near UCI.
    
    # Mock location parsing from WKT "POINT(-117.8443 33.6405)"
    try:
        wkt = spot['location'] # e.g. "POINT(-117.8443 33.6405)" or hex
        # Very hacky WKT parse for demo
        val = wkt.replace('POINT','').replace('(','').replace(')','')
        lng, lat = map(float, val.split())
    except:
        # Fallback if WKT parsing fails (e.g. binary format)
        lat, lng = user_lat + 0.001, user_lng + 0.001 

    # Mock Traffic
    traffic = get_travel_time(user_lat, user_lng, lat, lng)
    duration = traffic['duration'] if traffic else 0
    distance = traffic['distance'] if traffic else 0
    
    # Calculate Score
    score = 70 # Base
    
    # Distance/Time Penalty
    minutes = duration / 60
    score -= minutes * 2
    if minutes < 5: score += 10
    
    # Cost Penalty
    cost = spot['cost_per_hour']
    score -= cost * 2
    if cost < 3: score += 5
    
    # Preferences & Weather
    features = spot.get('features', [])
    is_covered = "Covered" in features
    
    if weather['is_raining']:
        if is_covered: score += 30 # Huge bonus for covered when raining here
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

# Sort
df = pd.DataFrame(ranked_spots)
if not df.empty:
    df = df.sort_values(by="score", ascending=False)

# Display Map
st.subheader("Parking Map")
if not df.empty:
    # Highlight top recommendation
    df['color'] = [[255, 0, 0, 160]] * len(df) # Default Red
    df.at[df.index[0], 'color'] = [0, 255, 0, 200] # Top 1 Green
    
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

# Display List
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
