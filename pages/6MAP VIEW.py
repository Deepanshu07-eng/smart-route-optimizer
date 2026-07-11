import streamlit as st
from db_helper import get_db_connection
import pandas as pd

st.title("🗺️ Smart Fleet Live GIS Engine Mapping")

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, latitude, longitude FROM students WHERE latitude != 0.0")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows)
            df.columns = ["name", "latitude", "longitude"]
            st.map(df)
            st.success("💡 Dynamic Student Location Clusters loaded on standard system map canvas above.")
        else:
            st.info("No valid geographical coordinates found. Add student addresses to view spatial matrix.")
    except Exception as e:
        st.error(f"Map Rendering Error: {e}")