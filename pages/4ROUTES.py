import streamlit as st
import pandas as pd
from database import get_connection

st.title("🗺️ Route Planning & Student Assignment")

conn = get_connection()
cursor = conn.cursor()

# Fetch buses
cursor.execute("SELECT id, bus_number, capacity FROM buses")
buses = cursor.fetchall()

# Fetch students
cursor.execute("SELECT id, name, pickup_location FROM students")
students = cursor.fetchall()

cursor.close()
conn.close()

if not buses:
    st.warning("Please add buses first.")
elif not students:
    st.warning("Please add students first.")
else:
    st.subheader("Create New Route")

    bus_options = {
        f"{bus[1]} | Capacity: {bus[2]}": bus
        for bus in buses
    }

    student_options = {
        f"{student[0]} - {student[1]} | {student[2]}": student
        for student in students
    }

    with st.form("create_route_form"):
        route_name = st.text_input("Route Name", placeholder="Example: Route A - Rohini")
        selected_bus_label = st.selectbox("Select Bus", list(bus_options.keys()))

        selected_students_labels = st.multiselect(
            "Select Students for this Route",
            list(student_options.keys())
        )

        submit = st.form_submit_button("Create Route")

    if submit:
        bus_id, bus_number, capacity = bus_options[selected_bus_label]
        selected_students = [student_options[label] for label in selected_students_labels]

        if not route_name:
            st.error("Please enter route name.")

        elif len(selected_students) == 0:
            st.error("Please select students.")

        elif len(selected_students) > capacity:
            st.error(f"Bus capacity is {capacity}, but you selected {len(selected_students)} students.")

        else:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO routes (route_name, bus_id, bus_number, total_students, capacity)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (route_name, bus_id, bus_number, len(selected_students), capacity)
            )

            route_id = cursor.lastrowid

            for student in selected_students:
                student_id, student_name, pickup_location = student

                cursor.execute(
                    """
                    INSERT INTO route_students
                    (route_id, student_id, student_name, pickup_location)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (route_id, student_id, student_name, pickup_location)
                )

            conn.commit()
            cursor.close()
            conn.close()

            st.success("Route created successfully!")
            st.rerun()

st.divider()
st.subheader("📋 All Routes")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT id, route_name, bus_number, total_students, capacity
FROM routes
""")

routes = cursor.fetchall()

cursor.close()
conn.close()

if routes:
    df = pd.DataFrame(
        routes,
        columns=["Route ID", "Route Name", "Bus Number", "Total Students", "Bus Capacity"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("No routes created yet.")

st.divider()
st.subheader("👨‍🎓 View Route Students")

route_id_view = st.number_input("Enter Route ID", min_value=1, step=1)

if st.button("View Students in Route"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT student_id, student_name, pickup_location
        FROM route_students
        WHERE route_id = %s
        """,
        (route_id_view,)
    )

    route_students = cursor.fetchall()

    cursor.close()
    conn.close()

    if route_students:
        df_students = pd.DataFrame(
            route_students,
            columns=["Student ID", "Student Name", "Pickup Location"]
        )
        st.dataframe(df_students, use_container_width=True)
    else:
        st.warning("No students found for this route.")

st.divider()
st.subheader("🗑️ Delete Route")

delete_id = st.number_input("Enter Route ID to delete", min_value=1, step=1, key="delete_route")

if st.button("Delete Route"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM route_students WHERE route_id = %s", (delete_id,))
    cursor.execute("DELETE FROM routes WHERE id = %s", (delete_id,))

    conn.commit()
    cursor.close()
    conn.close()

    st.success(f"Route ID {delete_id} deleted successfully!")
    st.rerun()