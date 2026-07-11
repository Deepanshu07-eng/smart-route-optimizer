import streamlit as st
from db_helper import get_db_connection
import pandas as pd
from datetime import date

st.title("📅 Daily Attendance Tracker")

today = date.today()
st.write(f"### Date: {today}")

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, roll_number FROM students")
        students = cursor.fetchall()
        
        if students:
            with st.form("attendance_form"):
                attendance_data = {}
                for s in students:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{s['name']}** ({s['roll_number']})")
                    with col2:
                        attendance_data[s['id']] = st.radio(
                            "Status", ["Present", "Absent", "Late"], 
                            key=f"att_{s['id']}", label_visibility="collapsed"
                        )
                
                submit = st.form_submit_button("Submit Attendance")
                
            if submit:
                save_cursor = conn.cursor()
                for s_id, status in attendance_data.items():
                    query = """
                    INSERT INTO attendance (student_id, date, status)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = %s
                    """
                    save_cursor.execute(query, (s_id, today, status, status))
                conn.commit()
                st.success("🎉 Attendance marked successfully for today!")
                save_cursor.close()
        else:
            st.info("No students registered yet to mark attendance.")
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")