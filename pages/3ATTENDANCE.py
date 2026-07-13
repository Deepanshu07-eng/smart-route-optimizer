import streamlit as st
from datetime import date
from db_helper import get_db_connection

st.title("Attendance Sheet")

selected_date = st.date_input("Date", date.today())

# 1. SELECT BUS NUMBER FIRST
bus_options = {}
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, bus_number FROM buses")
    for b in cursor.fetchall():
        bus_options[b['id']] = b['bus_number']
    cursor.close()
    conn.close()

selected_bus_id = st.selectbox(
    "Select Bus Number", 
    options=list(bus_options.keys()), 
    format_func=lambda x: bus_options[x]
)

# 2. FETCH ONLY ASSIGNED STUDENTS FOR THIS BUS
students = []
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, roll_number FROM students WHERE bus_id = %s ORDER BY name ASC", (selected_bus_id,))
        students = cursor.fetchall()
    except Exception:
        cursor.execute("SELECT id, name, roll_number FROM students WHERE bus_number = %s ORDER BY name ASC", (bus_options[selected_bus_id],))
        students = cursor.fetchall()
    cursor.close()
    conn.close()

# 3. MARK ATTENDANCE FOR THESE STUDENTS
if not students:
    st.info("No students are assigned to this bus.")
else:
    attendance_states = {}
    
    with st.form("attendance_form"):
        st.write("##### Mark Student Attendance Status:")
        for s in students:
            col1, col2 = st.columns([3, 2])
            col1.write(f"**{s['name']}** ({s['roll_number']})")
            attendance_states[s['id']] = col2.radio(
                "Status", ["Present", "Absent"], horizontal=True, 
                label_visibility="collapsed", key=f"r_{s['id']}"
            )
        
        submit = st.form_submit_button("Save Attendance", use_container_width=True)

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
            st.success("Attendance saved successfully.")
            st.rerun()

# 4. VIEW & RESET HISTORY LOGS
st.divider()
st.subheader("Attendance Logs")

history_date = st.date_input("Select Date to View", date.today(), key="history_date")

if st.button("Reset Attendance for Selected Date", type="primary", use_container_width=True):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "DELETE FROM attendance WHERE attendance_date = %s"
        cursor.execute(query, (history_date,))
        conn.commit()
        cursor.close()
        conn.close()
        st.warning("Data cleared.")
        st.rerun()

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
        st.info("No records found.")