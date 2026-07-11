import streamlit as st
from db_helper import get_db_connection

st.set_page_config(
    page_title="Smart Bus Route System",
    page_icon="🚌",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚌 Smart Bus Route Optimization System")
st.subheader("Admin Command Center")
st.write("---")

total_students = 0
conn = get_db_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]
    cursor.close()
    conn.close()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="metric-card"><h3>Students</h3><h2>{total_students}</h2></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card"><h3>Active Buses</h3><h2>4</h2></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card"><h3>Routes</h3><h2>3</h2></div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card"><h3>Attendance Today</h3><h2>92%</h2></div>', unsafe_allow_html=True)

st.write("### Quick Overview")
st.info("System fully operational. Ready to optimize student pickup paths.")