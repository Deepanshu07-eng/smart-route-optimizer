import streamlit as st
import pandas as pd
from database import get_connection

st.title("👨‍🎓 Student Management")

with st.form("student_form"):
    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    phone = st.text_input("Phone Number")
    location = st.text_input("Pickup Location")

    submit = st.form_submit_button("Add Student")

if submit:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO students (name, roll_no, phone, pickup_location)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (name, roll, phone, location))
    conn.commit()

    cursor.close()
    conn.close()

    st.success(f"{name} added successfully")

st.divider()
st.subheader("📋 All Students")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, name, roll_no, phone, pickup_location FROM students")
students = cursor.fetchall()

cursor.close()
conn.close()

if students:
    df = pd.DataFrame(
        students,
        columns=["ID", "Name", "Roll No", "Phone", "Pickup Location"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("No students found.")

st.divider()
st.subheader("🗑️ Delete Student")

delete_id = st.number_input("Enter Student ID to delete", min_value=1, step=1)

if st.button("Delete Student"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = %s", (delete_id,))
    conn.commit()

    cursor.close()
    conn.close()

    st.success(f"Student ID {delete_id} deleted successfully!")
    st.rerun()

st.divider()
st.subheader("✏️ Update Student")

update_id = st.number_input("Enter Student ID to update", min_value=1, step=1, key="update_id")

new_name = st.text_input("New Name")
new_roll = st.text_input("New Roll Number")
new_phone = st.text_input("New Phone Number")
new_location = st.text_input("New Pickup Location")

if st.button("Update Student"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE students
        SET name=%s, roll_no=%s, phone=%s, pickup_location=%s
        WHERE id=%s
        """,
        (new_name, new_roll, new_phone, new_location, update_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    st.success(f"Student ID {update_id} updated successfully!")
    st.rerun()