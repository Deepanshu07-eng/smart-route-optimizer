import streamlit as st
from db_helper import get_db_connection
import pandas as pd

st.title("🗺️ Route & Bus Allocation")

conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, bus_number FROM buses WHERE status = 'Available'")
    buses = cursor.fetchall()
    bus_options = {b['bus_number']: b['id'] for b in buses}
    
    st.write("### Create New Route Path")
    with st.form("route_form", clear_on_submit=True):
        route_name = st.text_input("Route Name (e.g., Route A - North Zone)")
        selected_bus = st.selectbox("Assign Available Bus", list(bus_options.keys()))
        start_point = st.text_input("Start Hub Location")
        end_point = st.text_input("Destination Institution Hub")
        
        submit = st.form_submit_button("Generate & Assign Route")
        
    if submit and route_name:
        try:
            route_cursor = conn.cursor()
            query = "INSERT INTO routes (route_name, bus_id, start_point, end_point) VALUES (%s, %s, %s, %s)"
            route_cursor.execute(query, (route_name, bus_options[selected_bus], start_point, end_point))
            conn.commit()
            st.success(f"🎉 Route '{route_name}' successfully built!")
            route_cursor.close()
        except Exception as e:
            st.error(f"Error saving route: {e}")
            
    st.write("---")
    st.write("### Current Active System Routes")
    cursor.execute("""
        SELECT r.id, r.route_name, b.bus_number, r.start_point, r.end_point 
        FROM routes r LEFT JOIN buses b ON r.bus_id = b.id
    """)
    routes_data = cursor.fetchall()
    if routes_data:
        st.dataframe(pd.DataFrame(routes_data), use_container_width=True)
        
    cursor.close()
    conn.close()