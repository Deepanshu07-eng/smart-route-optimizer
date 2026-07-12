import streamlit as st
from datetime import date
from db_helper import get_db_connection

st.title("✅ Daily Attendance Sheet")

# =====================================================
# 1. MARK ATTENDANCE
# =====================================================
selected_date = st.date_input("🗓️ Date", date.today())

students = []
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, roll_number FROM students ORDER BY name ASC")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

if not students:
    st.info("No students found.")
else:
    attendance_states = {}
    
    with st.form("attendance_form"):
        for s in students:
            col1, col2 = st.columns([3, 2])
            col1.write(f"**{s['name']}** ({s['roll_number']})")
            attendance_states[s['id']] = col2.radio(
                "Status", ["Present", "Absent"], horizontal=True, 
                label_visibility="collapsed", key=f"r_{s['id']}"
            )
        
        submit = st.form_submit_button("🔥 Save Attendance", use_container_width=True)

    if submit:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            for s_id, status in attendance_states.items():
                query = """
                    INSERT INTO attendance (student_id, attendance_date, status) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status)
                """
                cursor.execute(query, (s_id, selected_date, status))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("🎉 Saved!")
            st.rerun()

# =====================================================
# 2. VIEW & RESET PAST ATTENDANCE (HISTORY LOGS)
# =====================================================
st.divider()
st.subheader("📅 History Logs")

# Date picker for history
history_date = st.date_input("Choose Date to View", date.today(), key="history_date")

# --- RESET BUTTON CODE ---
# Delete query for the selected history date
if st.button("🗑️ Reset Selected Date Attendance", type="primary", use_container_width=True):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM attendance WHERE attendance_date = %s"
        cursor.execute(query, (history_date,))
        conn.commit()
        cursor.close()
        conn.close()
        st.warning(f"💥 Attendance for {history_date} has been cleared!")
        st.rerun()

st.write("") # Thoda space dene ke liye

# Fetch and display the logs
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT s.roll_number, s.name, a.status 
        FROM attendance a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.attendance_date = %s
    """
    cursor.execute(query, (history_date,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if rows:
        for r in rows:
            c1, c2, c3 = st.columns([1, 2, 1])
            c1.write(r['roll_number'])
            c2.write(r['name'])
            
            if r['status'] == "Present":
                c3.success("Present")
            else:
                c3.error("Absent")
    else:
        st.info("No records for this date.")