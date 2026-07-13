import streamlit as st
import pandas as pd
from datetime import date
from mysql.connector import Error

from db_helper import get_db_connection


st.title("🗺️ Route & Bus Allocation")


# ================= CREATE ROUTE =================

st.subheader("Create New Route")

with st.form("route_form", clear_on_submit=True):
    route_name = st.text_input("Route Name")
    start_point = st.text_input("Start Point")
    end_point = st.text_input("End Point")
    distance = st.number_input("Distance in KM", min_value=0.0, step=0.5)
    estimated_time = st.text_input("Estimated Time")
    route_status = st.selectbox("Route Status", ["Active", "Inactive"])

    create_route = st.form_submit_button("Create Route")

if create_route:
    if route_name and start_point and end_point:
        conn = get_db_connection()

        if conn is None:
            st.stop()

        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO routes
                (
                    route_name,
                    start_point,
                    end_point,
                    distance_km,
                    estimated_time,
                    route_status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    route_name,
                    start_point,
                    end_point,
                    distance,
                    estimated_time,
                    route_status
                )
            )

            conn.commit()
            st.success("Route created successfully!")
            st.rerun()

        except Error as error:
            conn.rollback()

            if error.errno == 1062:
                st.error("Route name already exists.")
            else:
                st.error(f"Route create nahi hua: {error}")

        finally:
            cursor.close()
            conn.close()

    else:
        st.warning("Route Name, Start Point aur End Point fill karo.")


st.divider()


# ================= LOAD ROUTES AND BUSES =================

conn = get_db_connection()

if conn is None:
    st.stop()

cursor = conn.cursor()

try:
    cursor.execute(
        "SELECT id, route_name FROM routes ORDER BY route_name"
    )
    routes = cursor.fetchall()

    cursor.execute(
        """
        SELECT id, bus_number, driver_name, capacity
        FROM buses
        ORDER BY bus_number
        """
    )
    buses = cursor.fetchall()

finally:
    cursor.close()
    conn.close()


# ================= ALLOCATE BUS =================

st.subheader("Allocate Bus to Route")

if routes and buses:
    route_options = {
        f"{route[0]} - {route[1]}": route[0]
        for route in routes
    }

    bus_options = {
        f"{bus[1]} | {bus[2] or 'No Driver'} | Capacity: {bus[3]}": bus[0]
        for bus in buses
    }

    with st.form("allocation_form"):
        selected_route = st.selectbox(
            "Select Route",
            list(route_options.keys())
        )

        selected_bus = st.selectbox(
            "Select Bus",
            list(bus_options.keys())
        )

        allocation_date = st.date_input(
            "Allocation Date",
            date.today()
        )

        allocate = st.form_submit_button("Allocate Bus")

    if allocate:
        conn = get_db_connection()

        if conn is None:
            st.stop()

        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO route_bus_allocation
                (route_id, bus_id, allocation_date)
                VALUES (%s, %s, %s)
                """,
                (
                    route_options[selected_route],
                    bus_options[selected_bus],
                    allocation_date
                )
            )

            conn.commit()
            st.success("Bus allocated successfully!")
            st.rerun()

        except Error as error:
            conn.rollback()

            if error.errno == 1062:
                st.error("Route ya bus already allocated hai.")
            else:
                st.error(f"Allocation failed: {error}")

        finally:
            cursor.close()
            conn.close()

elif not routes:
    st.info("Pehle route create karo.")

else:
    st.info("Pehle bus add karo.")


st.divider()


# ================= VIEW ROUTES =================

st.subheader("Routes and Bus Allocations")

conn = get_db_connection()

if conn is None:
    st.stop()

cursor = conn.cursor()

try:
    cursor.execute(
        """
        SELECT
            r.id,
            r.route_name,
            r.start_point,
            r.end_point,
            r.distance_km,
            r.estimated_time,
            r.route_status,
            b.bus_number,
            b.driver_name,
            b.capacity,
            a.allocation_date
        FROM routes r
        LEFT JOIN route_bus_allocation a
            ON r.id = a.route_id
        LEFT JOIN buses b
            ON a.bus_id = b.id
        ORDER BY r.id DESC
        """
    )

    rows = cursor.fetchall()

finally:
    cursor.close()
    conn.close()

if rows:
    df = pd.DataFrame(
        rows,
        columns=[
            "Route ID",
            "Route Name",
            "Start Point",
            "End Point",
            "Distance",
            "Estimated Time",
            "Status",
            "Bus Number",
            "Driver",
            "Capacity",
            "Allocation Date"
        ]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No routes found.")


st.divider()


# ================= REMOVE ALLOCATION =================

st.subheader("Remove Bus Allocation")

remove_id = st.number_input(
    "Enter Route ID",
    min_value=1,
    step=1,
    key="remove_allocation"
)

if st.button("Remove Allocation"):
    conn = get_db_connection()

    if conn is None:
        st.stop()

    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM route_bus_allocation
            WHERE route_id = %s
            """,
            (remove_id,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            st.success("Allocation removed successfully!")
        else:
            st.warning("Allocation not found.")

        st.rerun()

    finally:
        cursor.close()
        conn.close()


st.divider()


# ================= DELETE ROUTE =================

st.subheader("Delete Route")

delete_id = st.number_input(
    "Enter Route ID to Delete",
    min_value=1,
    step=1,
    key="delete_route"
)

if st.button("Delete Route", type="primary"):
    conn = get_db_connection()

    if conn is None:
        st.stop()

    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM route_bus_allocation
            WHERE route_id = %s
            """,
            (delete_id,)
        )

        cursor.execute(
            """
            DELETE FROM routes
            WHERE id = %s
            """,
            (delete_id,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            st.success("Route deleted successfully!")
        else:
            st.warning("Route not found.")

        st.rerun()

    finally:
        cursor.close()
        conn.close()