import streamlit as st
from db_helper import get_db_connection

st.title("Bus & Driver Management")

# =====================================================
# 1. FLEET METRICS PANEL
# =====================================================
total_buses, available, running, maintenance = 0, 0, 0, 0
conn = get_db_connection()
if conn:
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

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", total_buses)
col2.metric("Available", available)
col3.metric("Running", running)
col4.metric("Maintenance", maintenance)

st.divider()

# =====================================================
# 2. REGISTER NEW BUS
# =====================================================
st.subheader("Register New Bus")
with st.form("bus_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    bus_number = c1.text_input("Bus Number")
    capacity = c1.number_input("Capacity", min_value=1, max_value=100, value=40)
    driver_name = c2.text_input("Driver Name")
    driver_phone = c2.text_input("Driver Phone")
    status = st.selectbox("Bus Status", ["Available", "Running", "Maintenance"])
    submit = st.form_submit_button("Save Bus")

if submit and bus_number and driver_name:
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO buses (bus_number, capacity, driver_name, driver_phone, status) VALUES (%s, %s, %s, %s, %s)",
            (bus_number, capacity, driver_name, driver_phone, status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Bus registered successfully.")
        st.rerun()

st.divider()

# =====================================================
# 3. ACTION MANAGEMENT PANEL
# =====================================================
st.subheader("Action Management Panel")
action_choice = st.selectbox(
    "Choose Operation Mode", 
    [
        "--- Select Action ---", 
        "👥 Assign Student to Bus", 
        "✏️ Update Bus Status", 
        "🗑️ Delete Bus from Fleet"
    ]
)

# Fetch current active fleet list for selector dropdowns
all_buses = {}
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, bus_number FROM buses")
    for b in cursor.fetchall():
        all_buses[b['id']] = b['bus_number']
    cursor.close()
    conn.close()

# 👥 DYNAMIC OPTION: TABLE STYLE BUS ASSIGNMENT (EXACTLY LIKE YOUR SCREENSHOT)
if action_choice == "👥 Assign Student to Bus":
    st.write("### Manage Student Bus Allocations")
    
    students_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, roll_number, bus_id FROM students ORDER BY name ASC")
        students_list = cursor.fetchall()
        cursor.close()
        conn.close()

    if not students_list:
        st.info("No students found in the system.")
    else:
        assignment_states = {}
        
        # Batch form layout
        with st.form("bulk_assignment_form"):
            h1, h2, h3 = st.columns([2, 1, 2])
            h1.markdown("**Student Name**")
            h2.markdown("**Roll No**")
            h3.markdown("**Assign Bus Allocation**")
            st.divider()
            
            # Options list creation for the selectbox (Including an unassigned option)
            bus_ids = [0] + list(all_buses.keys())
            
            def format_bus_display(x):
                return "Not Assigned" if x == 0 else all_buses[x]

            for s in students_list:
                c1, c2, c3 = st.columns([2, 1, 2])
                c1.write(s['name'])
                c2.write(s['roll_number'])
                
                # Check current bus link status fallback
                current_bus = s['bus_id'] if s['bus_id'] in all_buses else 0
                default_idx = bus_ids.index(current_bus) if current_bus in bus_ids else 0
                
                # Input dropdown element vectors mapping
                assignment_states[s['id']] = c3.selectbox(
                    f"Bus Selection for {s['id']}",
                    options=bus_ids,
                    format_func=format_bus_display,
                    index=default_idx,
                    label_visibility="collapsed",
                    key=f"select_{s['id']}"
                )
                
            save_allocations = st.form_submit_button("Save All Allocations", use_container_width=True)

        if save_allocations:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                summary_messages = []
                
                for s_id, allocated_bus in assignment_states.items():
                    db_val = None if allocated_bus == 0 else allocated_bus
                    cursor.execute("UPDATE students SET bus_id = %s WHERE id = %s", (db_val, s_id))
                    
                    
                conn.commit()
                cursor.close()
                conn.close()
                
                # Dynamic visual success box with exact mapping confirmations
                st.success("🎉 Your allocations have been successfully saved to the database!")
                for msg in summary_messages:
                    st.info(msg)
                    
                st.toast("Allocations Saved!")
                # Thoda pause de kar rerun karenge taaki user validation logs dekh sake
                if st.button("Click to Refresh Panel View"):
                    st.rerun()

# ✏️ DYNAMIC OPTION: UPDATE BUS STATUS
elif action_choice == "✏️ Update Bus Status":
    st.write("### Change Fleet Status")
    if all_buses:
        u_id = st.selectbox("Select Bus to Update", options=list(all_buses.keys()), format_func=lambda x: all_buses[x])
        new_status = st.selectbox("New Status Code", ["Available", "Running", "Maintenance"])
        if st.button("Update Status"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE buses SET status=%s WHERE id=%s", (new_status, u_id))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Status updated.")
                st.rerun()

# 🗑️ DYNAMIC OPTION: DELETE BUS
elif action_choice == "🗑️ Delete Bus from Fleet":
    st.write("### Remove Vehicle Record")
    if all_buses:
        d_id = st.selectbox("Select Bus to Delete", options=list(all_buses.keys()), format_func=lambda x: all_buses[x])
        if st.button("Confirm Delete", type="primary"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM buses WHERE id=%s", (d_id,))
                conn.commit()
                cursor.close()
                conn.close()
                st.warning("Bus removed.")
                st.rerun()

st.divider()

# =====================================================
# 4. ACTIVE FLEET LIST (PURE PYTHON VIEW)
# =====================================================
st.subheader("Active Fleet List")
search = st.text_input("Search Bus Number")
conn = get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    if search:
        cursor.execute("SELECT id, bus_number, capacity, driver_name, driver_phone, status FROM buses WHERE bus_number LIKE %s", (f"%{search}%",))
    else:
        cursor.execute("SELECT id, bus_number, capacity, driver_name, driver_phone, status FROM buses ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if rows:
        h1, h2, h3, h4, h5 = st.columns([1, 2, 1, 2, 2])
        h1.markdown("**ID**")
        h2.markdown("**Bus Number**")
        h3.markdown("**Cap**")
        h4.markdown("**Driver**")
        h5.markdown("**Status**")
        st.divider()
        for r in rows:
            c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 2, 2])
            c1.write(str(r['id']))
            c2.write(r['bus_number'])
            c3.write(str(r['capacity']))
            c4.write(r['driver_name'])
            c5.write(r['status'])
    else:
        st.info("No records found.")