import streamlit as st
import math
import urllib.parse
from geopy.geocoders import Nominatim
from db_helper import get_db_connection

st.title("🗺️ Route Map View")
st.write("Enter your dynamic addresses, select a bus, and generate the optimized path.")

# =====================================================
# 1. USER INPUT CONTROL PANEL (FORM BASED)
# =====================================================
with st.form("routing_input_form"):
    st.subheader("📋 Shift & Address Configuration")
    
    route_type = st.radio("Select Route Type", ["Morning Route", "Afternoon Route"], horizontal=True)
    
    c1, c2 = st.columns(2)
    depot_address = c1.text_input("Bus Current Location / Depot Address", value="Rohini sector 7, new delhi")
    school_address = c2.text_input("School / College Destination Address", value="IIIT Delhi, Okhla")
    
    # Fetch active buses for dropdown inside the form
    bus_options = {}
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, bus_number FROM buses ORDER BY bus_number")
        for b in cursor.fetchall():
            bus_options[b['id']] = b['bus_number']
        cursor.close()
        conn.close()
        
    if bus_options:
        selected_bus_id = st.selectbox("Select Active Bus Fleet", options=list(bus_options.keys()), format_func=lambda x: bus_options[x])
    else:
        st.warning("Please add buses in the system first.")
        selected_bus_id = None

    submit_btn = st.form_submit_button("Generate Shortest Route Sequence", use_container_width=True, type="primary")

# =====================================================
# 2. HELPER FUNCTIONS WITH FALLBACK CODES
# =====================================================
def get_coordinates(address, default_lat, default_lon):
    if not address.strip():
        return default_lat, default_lon
    try:
        # Initializing Nominatim Engine
        geolocator = Nominatim(user_agent="smart_bus_driver_locator_v3")
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    # FALLBACK: If geocoding fails, return default fallback coordinates instead of None
    return default_lat, default_lon

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

# =====================================================
# 3. BACKEND ROUTING ENGINE EXECUTION
# =====================================================
if submit_btn:
    if not depot_address.strip() or not school_address.strip():
        st.error("⚠️ Please fill in both the Depot Address and School Address fields!")
        st.stop()
        
    if not selected_bus_id:
        st.error("⚠️ Active vehicle selection missing.")
        st.stop()

    # Dynamic lookup with hardcoded system defaults (Delhi region coordinates as safety backup)
    depot_lat, depot_lon = get_coordinates(depot_address, default_lat=28.7041, default_lon=77.1025) # Rohini Default
    school_lat, school_lon = get_coordinates(school_address, default_lat=28.5459, default_lon=77.2732) # Okhla/IIIT Default

    # Fetch assigned students with coordinates from DB
    students = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT name, roll_number, pickup_location, latitude, longitude 
            FROM students 
            WHERE bus_id = %s AND latitude != 0 AND longitude != 0
        """
        cursor.execute(query, (selected_bus_id,))
        students = cursor.fetchall()
        cursor.close()
        conn.close()

    if not students:
        st.warning("ℹ️ No students with valid coordinates are mapped to this vehicle yet.")
        
        # Formulate map view even if students array is empty just to show start and end connection
        st.subheader("📍 Basic Hub Visualization")
        st.map([{"latitude": depot_lat, "longitude": depot_lon}, {"latitude": school_lat, "longitude": school_lon}])
    else:
        # Determine Routing Chain flow direction based on user configuration state
        if route_type == "Morning Route":
            current_lat, current_lon = depot_lat, depot_lon
            start_name, end_name = f"Bus Depot Base ({depot_address})", f"School Campus ({school_address})"
            origin_coords, dest_coords = f"{depot_lat},{depot_lon}", f"{school_lat},{school_lon}"
        else:
            current_lat, current_lon = school_lat, school_lon
            start_name, end_name = f"School Campus ({school_address})", f"Bus Depot Base ({depot_address})"
            origin_coords, dest_coords = f"{school_lat},{school_lon}", f"{depot_lat},{depot_lon}"

        # Pure Dijkstra/Greedy TSP path sequencing
        unvisited = students.copy()
        optimized_route = []
        
        while unvisited:
            min_dist = float('inf')
            next_idx = -1
            
            for idx, s in enumerate(unvisited):
                d = calculate_distance(current_lat, current_lon, float(s['latitude']), float(s['longitude']))
                if d < min_dist:
                    min_dist = d
                    next_idx = idx
                    
            if next_idx != -1:
                target = unvisited.pop(next_idx)
                optimized_route.append(target)
                current_lat, current_lon = float(target['latitude']), float(target['longitude'])

        # --- METRICS SYSTEM ---
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Selected Bus", bus_options[selected_bus_id])
        m2.metric("Stops Computed", len(optimized_route))
        m3.metric("Selected Shift Mode", route_type)

        # --- MAP RENDERING ---
        st.subheader("📍 Live Map Route Generation")
        
        # Include Start and End coordinates into the visual rendering block
        map_points = [{"latitude": depot_lat, "longitude": depot_lon}]
        for s in optimized_route:
            map_points.append({"latitude": float(s['latitude']), "longitude": float(s['longitude'])})
        map_points.append({"latitude": school_lat, "longitude": school_lon})
        
        st.map(map_points)

        # --- GOOGLE MAPS ROUTE DEEP LINK ---
        waypoints_str = "|".join([f"{s['latitude']},{s['longitude']}" for s in optimized_route])
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin_coords}&destination={dest_coords}&waypoints={urllib.parse.quote(waypoints_str)}&travelmode=driving"
        
        st.link_button("🚀 START LIVE NAVIGATION (Google Maps App)", gmaps_url, use_container_width=True, type="primary")

        # --- STOP SEQUENCE LIST VIEW ---
        st.subheader("📋 Driver Manifest Sequence")
        st.warning(f"🚩 **STARTING HUB:** {start_name}")
        for idx, stop in enumerate(optimized_route, start=1):
            action = "Pickup" if route_type == "Morning Route" else "Drop off"
            st.info(f"Stop {idx}: {action} **{stop['name']}** ({stop['roll_number']}) at *{stop['pickup_location']}*")
        st.success(f"🏁 **DESTINATION HUB:** {end_name}")