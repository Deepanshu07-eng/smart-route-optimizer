import streamlit as st
# Dono functions ko ek sath proper import kiya
from db_helper import get_db_connection

st.set_page_config(
    page_title="Smart Bus Route System",
    page_icon="🚌",
    layout="wide"
)




st.title("🚌 Smart Bus Route Optimization System")
st.subheader("Admin Dashboard")

# Initialize Default Values
total_students = 0
total_buses = 0
total_routes = 0
attendance_percentage = 0

# Fetch Live Data
conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM buses")
        total_buses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM routes")
        total_routes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = CURDATE() AND status = 'Present'")
        present_students = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = CURDATE()")
        total_attendance = cursor.fetchone()[0]

        if total_attendance > 0:
            attendance_percentage = int((present_students / total_attendance) * 100)

        cursor.close()
        conn.close()
    except Exception:
        pass

# =====================================================
# Step 2: Display UI Component Cards (Using Fetched Values)
# =====================================================
st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    with st.container(border=True):
        st.metric(
            label="👨‍🎓 Total Students",
            value=total_students
        )

with col2:
    with st.container(border=True):
        st.metric(
            label="🚌 Total Buses",
            value=total_buses
        )

with col3:
    with st.container(border=True):
        st.metric(
            label="🗺️ Total Routes",
            value=total_routes
        )

with col4:
    with st.container(border=True):
        st.metric(
            label="📅 Attendance Today",
            value=f"{attendance_percentage}%"
        )

st.divider()

# =====================================================
# Quick Overview Section
# =====================================================
st.subheader("Quick Overview")

col1, col2 = st.columns(2)

with col1:
    st.info(f"Students Registered: {total_students}")
    st.info(f"Buses Registered: {total_buses}")

with col2:
    st.info(f"Routes Created: {total_routes}")
    st.info(f"Today's Attendance: {attendance_percentage}%")

st.divider()

# =====================================================
# Project Modules Routing Section
# =====================================================
st.subheader("Project Modules")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("👨‍🎓 Students")
        st.write("Add, update, delete, and view students.")

    with st.container(border=True):
        st.subheader("✅ Attendance")
        st.write("Mark daily student attendance.")

with col2:
    with st.container(border=True):
        st.subheader("🚌 Buses")
        st.write("Manage buses and driver details.")

    with st.container(border=True):
        st.subheader("📍 Pickup Points")
        st.write("Manage student pickup locations.")

with col3:
    with st.container(border=True):
        st.subheader("🗺️ Routes")
        st.write("Create and manage bus routes.")

    with st.container(border=True):
        st.subheader("📊 Analytics")
        st.write("View charts and reports.")

st.divider()

# =====================================================
# System Status Section
# =====================================================
st.subheader("System Status")

# Re-checking connection health status safely
status_conn = get_db_connection()
if status_conn:
    st.success("Database connected successfully.")
    status_conn.close()
else:
    st.error("Database connection failed.")