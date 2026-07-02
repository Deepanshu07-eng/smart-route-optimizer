import streamlit as st

st.set_page_config(
    page_title="Smart Bus Route System",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Smart Bus Route System")
st.subheader("Admin Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Students", "0")

with col2:
    st.metric("Buses", "0")

with col3:
    st.metric("Routes", "0")

with col4:
    st.metric("Attendance", "0%")