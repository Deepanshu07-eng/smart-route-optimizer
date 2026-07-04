import streamlit as st
import pandas as pd
from database import get_connection

st.title("🚌 Bus Management")

# ---------- ADD BUS ----------
with st.form("bus_form"):
    bus_number = st.text_input("Bus Number")
    driver_name = st.text_input("Driver Name")
    capacity = st.number_input("Capacity", min_value=1, step=1)
    status = st.selectbox("Status", ["Active", "Inactive", "Maintenance"])

    submit = st.form_submit_button("Add Bus")

if submit:
    if bus_number and driver_name and capacity:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO buses (bus_number, driver_name, capacity, status)
            VALUES (%s, %s, %s, %s)
            """,
            (bus_number, driver_name, capacity, status)
        )

        conn.commit()
        cursor.close()
        conn.close()

        st.success(f"Bus {bus_number} added successfully!")
        st.rerun()
    else:
        st.error("Please fill all fields.")

# ---------- VIEW BUSES ----------
st.divider()
st.subheader("📋 All Buses")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, bus_number, driver_name, driver_phone, capacity FROM buses")
buses = cursor.fetchall()

df = pd.DataFrame(
    buses,
    columns=["ID", "Bus Number", "Driver Name", "Driver Phone", "Capacity"]
)

cursor.close()
conn.close()

if buses:
    df = pd.DataFrame(
        buses,
        columns=["ID", "Bus Number", "Driver Name", "Capacity", "Status"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("No buses found.")

# ---------- DELETE BUS ----------
st.divider()
st.subheader("🗑️ Delete Bus")

delete_id = st.number_input("Enter Bus ID to delete", min_value=1, step=1)

if st.button("Delete Bus"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM buses WHERE id = %s", (delete_id,))
    conn.commit()

    cursor.close()
    conn.close()

    st.success(f"Bus ID {delete_id} deleted successfully!")
    st.rerun()

# ---------- UPDATE BUS ----------
st.divider()
st.subheader("✏️ Update Bus")

update_id = st.number_input("Enter Bus ID to update", min_value=1, step=1, key="update_id")

new_bus_number = st.text_input("New Bus Number")
new_driver_name = st.text_input("New Driver Name")
new_capacity = st.number_input("New Capacity", min_value=1, step=1, key="new_capacity")
new_status = st.selectbox("New Status", ["Active", "Inactive", "Maintenance"], key="new_status")

if st.button("Update Bus"):
    if new_bus_number and new_driver_name and new_capacity:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE buses
            SET bus_number=%s, driver_name=%s, capacity=%s, status=%s
            WHERE id=%s
            """,
            (new_bus_number, new_driver_name, new_capacity, new_status, update_id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        st.success(f"Bus ID {update_id} updated successfully!")
        st.rerun()
    else:
        st.error("Please fill all update fields.")