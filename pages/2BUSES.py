import streamlit as st
import pandas as pd
from db_helper import get_db_connection

st.title("🚌 Bus & Driver Management")
st.caption("Manage your school transportation fleet.")

# =====================================================
# Fleet Statistics
# =====================================================
total_buses = 0
available = 0
running = 0
maintenance = 0

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) AS total FROM buses")
        total_buses = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) AS total FROM buses WHERE status='Available'")
        available = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) AS total FROM buses WHERE status='Running'")
        running = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) AS total FROM buses WHERE status='Maintenance'")
        maintenance = cursor.fetchone()["total"]
        
        cursor.close()
        conn.close()
    except Exception:
        pass

col1, col2, col3, col4 = st.columns(4)
col1.metric("🚌 Total", total_buses)
col2.metric("✅ Available", available)
col3.metric("🚍 Running", running)
col4.metric("🔧 Maintenance", maintenance)

st.divider()

# =====================================================
# Add Bus
# =====================================================
st.subheader("➕ Register New Bus")

with st.form("bus_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        bus_number = st.text_input("Bus Number")
        capacity = st.number_input("Capacity", min_value=1, max_value=100, value=40)
    with c2:
        driver_name = st.text_input("Driver Name")
        driver_phone = st.text_input("Driver Phone")
        
    status = st.selectbox("Bus Status", ["Available", "Running", "Maintenance"])
    submit = st.form_submit_button("Save Bus")

if submit:
    if not bus_number or not driver_name:
        st.warning("Bus Number and Driver Name are required.")
    else:
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO buses (bus_number, capacity, driver_name, driver_phone, status)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (bus_number, capacity, driver_name, driver_phone, status)
                )
                conn.commit()
                cursor.close()
                conn.close()
                
                st.toast("Bus Added Successfully 🚍")
                st.success("Fleet updated successfully! Refreshing dynamic panels...")
                
                # JavaScript fallback logic use karenge standard rerun bypass ke liye
                st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Database Error: {e}")

st.divider()

# =====================================================
# Fleet List
# =====================================================
st.subheader("🚍 Fleet List")
search = st.text_input("🔍 Search Bus Number")

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        if search:
            cursor.execute("SELECT * FROM buses WHERE bus_number LIKE %s", (f"%{search}%",))
        else:
            cursor.execute("SELECT * FROM buses ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No buses found.")
    except Exception as e:
        st.error(f"Error fetching logs: {e}")

st.divider()

# =====================================================
# Update Bus
# =====================================================
st.subheader("✏ Update Bus Status")

u1, u2 = st.columns(2)
with u1:
    update_id = st.number_input("Bus ID", min_value=1, step=1)
with u2:
    new_status = st.selectbox("New Status", ["Available", "Running", "Maintenance"], key="update_status_box")

if st.button("Update Status"):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE buses SET status=%s WHERE id=%s", (new_status, update_id))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Status Updated Successfully!")
            st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Update Failed: {e}")

st.divider()

# =====================================================
# Delete Bus
# =====================================================
st.subheader("🗑 Delete Bus from Fleet")

delete_id = st.number_input("Delete Bus ID", min_value=1, step=1, key="delete")

if st.button("Delete Bus"):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM buses WHERE id=%s", (delete_id,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Bus Deleted Successfully from Database.")
            st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Delete Failed: {e}")