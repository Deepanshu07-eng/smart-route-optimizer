import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection

st.title("✅ Daily Attendance")

selected_date = st.date_input("Select Date", date.today())

# ---------- FETCH STUDENTS ----------
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, name, roll_no FROM students ORDER BY roll_no")
students = cursor.fetchall()

cursor.close()
conn.close()

if not students:
    st.warning("No students found. Please add students first.")
else:
    st.subheader(f"Mark Attendance for {selected_date}")

    attendance_data = []

    with st.form("daily_attendance_form"):
        for student in students:
            student_id, name, roll_no = student

            col1, col2, col3 = st.columns([1, 3, 2])

            with col1:
                st.write(f"**{roll_no}**")

            with col2:
                st.write(name)

            with col3:
                status = st.radio(
                    "Status",
                    ["Present", "Absent"],
                    horizontal=True,
                    key=f"attendance_{student_id}",
                    label_visibility="collapsed"
                )

            attendance_data.append((student_id, name, status, selected_date))

        submit = st.form_submit_button("Save Attendance")

    if submit:
        conn = get_connection()
        cursor = conn.cursor()

        # same date ki old attendance delete, then new save
        cursor.execute(
            "DELETE FROM attendance WHERE attendance_date = %s",
            (selected_date,)
        )

        for record in attendance_data:
            cursor.execute(
                """
                INSERT INTO attendance
                (student_id, student_name, status, attendance_date)
                VALUES (%s, %s, %s, %s)
                """,
                record
            )

        conn.commit()
        cursor.close()
        conn.close()

        st.success("Attendance saved successfully!")
        st.rerun()

# ---------- VIEW ATTENDANCE ----------
st.divider()
st.subheader("📋 Attendance Records")

conn = get_connection()
cursor = conn.cursor()

cursor.execute(
    """
    SELECT id, student_id, student_name, status, attendance_date
    FROM attendance
    ORDER BY attendance_date DESC, student_id ASC
    """
)

records = cursor.fetchall()

cursor.close()
conn.close()

if records:
    df = pd.DataFrame(
        records,
        columns=["ID", "Student ID", "Student Name", "Status", "Date"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("No attendance records found.")