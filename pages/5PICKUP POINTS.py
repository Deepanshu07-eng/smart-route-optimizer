import streamlit as st
from db_helper import get_db_connection
import pandas as pd

st.title("📍 Active Pickup Hub Stations")

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, pickup_location, latitude, longitude FROM students WHERE pickup_location IS NOT NULL")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows)
            df.columns = ["Student Name", "Station Location Pool", "Latitude", "Longitude"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No pickup points detected yet. Add students with valid addresses first.")
    except Exception as e:
        st.error(f"Error fetching spatial nodes: {e}")