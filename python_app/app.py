import streamlit as st
import pandas as pd
import struct
import binascii
import pydeck as pdk
import requests
from utils.supabase_client import get_supabase_client
from utils.weather import get_weather
from utils.traffic import get_travel_time
from utils.geocoding import geocode_address
from utils.parkingspots import get_parking_spots_near

# Set page config
st.set_page_config(page_title="FindMyParking", layout="wide")

# Initialize Supabase
supabase = get_supabase_client()

st.sidebar.title("FindMyParking 🚗")
st.sidebar.markdown("Personalized Parking Recommendations")

#Detect User Location
def get_user_location():
    try:
        resp = requests.get("https://ipinfo.io/json") #get location from ipaddress
        data = resp.json()
        loc = data["loc"].split(",")
        return float(loc[0]), float(loc[1])
    except:
        return 33.6405, -117.8443  # fallback: UCI

user_lat, user_lng = get_user_location()

st.sidebar.write(f"**Current Location:** ({user_lat}, {user_lng})")

# Input Destination
st.sidebar.write("Your Destination")

dest_query = st.sidebar.text_input("Enter destination:", placeholder="e.g. UCI Student Center")

destination = None
dest_lat = None
dest_lng = None

if dest_query:
    # fetch suggestions every time input changes
    suggestions = geocode_address(dest_query, user_lat, user_lng)

    if suggestions:
        selected = st.sidebar.selectbox(
            "Select destination", options=suggestions, format_func=lambda x: x["name"]
        )
        if selected:
            dest_lat = selected["lat"]
            dest_lng = selected["lng"]
            destination = selected
            st.sidebar.success(f"Destination: {selected['name']}")

#User Preferences
max_cost = st.sidebar.slider("Max Cost per Hour ($)", 0.0, 10.0, 5.0, 0.5)
pref_covered = st.sidebar.checkbox("Prefer Covered Parking")
pref_accessible = st.sidebar.checkbox("Prefer Accessible Parking")


weather = get_weather(user_lat, user_lng)

col1, col2, col3 = st.columns(3)
col1.metric("Weather", f"{weather['condition']}", f"{weather['temp']}°C")
col2.metric("Rain Status", "Raining" if weather['is_raining'] else "Clear")


#get parking spots
center_lat, center_lng = (dest_lat, dest_lng) if destination else (user_lat, user_lng) #center location around destination
spots = get_parking_spots_near(center_lat, center_lng)
MAX_SPOTS = 50
spots = spots[:MAX_SPOTS] #limit amount of spots

if not spots:
    st.warning("No parking spots found nearby.")
    st.stop()

# Ranking Algorithm
#stop ranking if destination not selected
if dest_lat is None or dest_lng is None:
    st.stop()

ranked_spots = []

for spot in spots:
    lng = spot['lon']
    lat = spot['lat']
    
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

#Show Map
st.subheader("Parking Map")
if not df.empty:
    df['color'] = [[255, 0, 0, 160]] * len(df)
    df.at[df.index[0], 'color'] = [0, 255, 0, 200] 

    df_map = df.head(20) #only render 20
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_map,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=100,
        pickable=True,
    )
    
    map_lat = df['lat'].mean()
    map_lng = df['lon'].mean()
    view_state = pdk.ViewState(latitude=map_lat, longitude=map_lng, zoom=14)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}\nScore: {score}\nCost: {cost}"})
    st.pydeck_chart(r)

#Show Top Recommended
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
