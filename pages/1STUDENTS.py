import streamlit as st
import pandas as pd
from db_helper import get_db_connection
from geopy.geocoders import Nominatim

import streamlit as st

#css code
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_coordinates(address):
    try:
        geolocator = Nominatim(
            user_agent="smart_bus_route_system"
        )

        location = geolocator.geocode(
            address + ", India",
            timeout=10
        )

        if location:
            return location.latitude, location.longitude

        return None, None

    except Exception:
        return None, None



st.title("🎓 Student Management")
st.caption("Manage student registrations and their pickup locations.")

# Helper function for GeoCoding (Address to Latitudee/Lngitude)
def get_coordinates(address):
    try:
        geolocator = Nominatim(user_agent="bus_route_app_2026")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        return 0.0, 0.0
    except:
        return 0.0, 0.0

#students deatils
total_students = 0
mapped_students = 0

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) AS total FROM students")
        total_students = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) AS total FROM students WHERE latitude != 0.0 AND longitude != 0.0")
        mapped_students = cursor.fetchone()["total"]
        
        cursor.close()
        conn.close()
    except Exception:
        pass

col1, col2 = st.columns(2)
col1.metric("Total Students Registered", total_students)
col2.metric("Geocoded (Mapped) Students", mapped_students)

st.divider()

#add studenT
st.subheader("Register New Student")

with st.form("student_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Student Name")
        roll_number = st.text_input("Roll Number / ID")
    with c2:
        phone_number = st.text_input("Parent Phone Number")
        address = st.text_input("Pickup Address (e.g., Connaught Place, Delhi)")
        
    submit = st.form_submit_button("Save Student Details")

if submit:
    if not name or not roll_number or not address:
        st.warning("Name, Roll Number, and Pickup Address are required.")
    
    else:
        conn = get_db_connection()
        if conn:
            try:
                with st.spinner("Converting address to GIS coordinates..."):
                    lat, lng = get_coordinates(address)
                
                cursor = conn.cursor()
                query = """
                INSERT INTO students (name, roll_number, phone_number, pickup_location, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name, roll_number, phone_number, address, lat, lng))
                conn.commit()
                cursor.close()
                conn.close()
                
                st.toast("Student Registered Successfully! 🎓")
                st.success(f"🎉 Student {name} successfully added with coordinates ({lat}, {lng})!")
                st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Database Error: {e}")
        else:
            st.error("Could not connect to database.")

st.divider()

#studentslist and search students
st.subheader("Registered Students Directory")
search = st.text_input("Search Student by Name or Roll Number")

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        if search:
            cursor.execute(
                "SELECT id, name, roll_number, phone_number, pickup_location, latitude, longitude FROM students WHERE name LIKE %s OR roll_number LIKE %s",
                (f"%{search}%", f"%{search}%")
            )
        else:
            cursor.execute("SELECT id, name, roll_number, phone_number, pickup_location, latitude, longitude FROM students ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows)
            df.columns = ["ID", "Name", "Roll Number", "Phone", "Pickup Address", "Latitude", "Longitude"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No students found.")
    except Exception as e:
        st.error(f"Error fetching logs: {e}")

st.divider()

#student location updation

st.subheader("Update Student Location / Address")

u1, u2 = st.columns([1, 2])
with u1:
    update_id = st.number_input("Student ID", min_value=1, step=1, key="update_sid")
with u2:
    new_address = st.text_input("New Pickup Address", key="update_address")

if st.button("Update Address Details"):
    if not new_address:
        st.warning("Please enter the new address.")
    else:
        conn = get_db_connection()
        if conn:
            try:
                with st.spinner("Fetching new coordinates..."):
                    lat, lng = get_coordinates(new_address)
                    
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE students SET pickup_location=%s, latitude=%s, longitude=%s WHERE id=%s",
                    (new_address, lat, lng, update_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Student location successfully updated!")
                st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Update Failed: {e}")

st.divider()

#delete student
st.subheader("🗑 Delete Student Record")

delete_id = st.number_input("Delete Student ID", min_value=1, step=1, key="delete_sid")

if st.button("Remove Student"):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=%s", (delete_id,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Student record deleted successfully.")
            st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Delete Failed: {e}")