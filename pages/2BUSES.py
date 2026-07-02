import streamlit as st
import pandas as pd
from database import get_connection

st.title("🚌 Bus Management")

with st.form("bus_form"):
    bus_number = st.text_input("Bus Number")
    driver_name = st.text_input("Driver Name")
    driver_phone = st.text_input("Driver Phone")
    capacity = st.number_input("Capacity", min_value=1, step=1)

    submit = st.form_submit_button("Add Bus")

if submit:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO buses (bus_number, driver_name, driver_phone, capacity)
        VALUES (%s, %s, %s, %s)
        """,
        (bus_number, driver_name, driver_phone, capacity)
    )

    conn.commit()
    cursor.close()
    conn.close()

    st.success("Bus added successfully!")
    st.rerun()

st.divider()
st.subheader("📋 All Buses")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, bus_number, driver_name, driver_phone, capacity FROM buses")
buses = cursor.fetchall()

cursor.close()
conn.close()

if buses:
    df = pd.DataFrame(
        buses,
        columns=["ID", "Bus Number", "Driver Name", "Driver Phone", "Capacity"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("No buses found yet.")