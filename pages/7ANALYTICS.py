import streamlit as st
from db_helper import get_db_connection
import pandas as pd

st.title("📊 Enterprise Transportation Analytics")

conn = get_db_connection()
if conn:
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status")
        att_data = cursor.fetchall()
        
        cursor.execute("SELECT status, COUNT(*) FROM buses GROUP BY status")
        bus_data = cursor.fetchall()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Attendance Metrics Breakdown")
            if att_data:
                df_att = pd.DataFrame(att_data, columns=["Status", "Count"])
                st.bar_chart(df_att.set_index("Status"))
            else:
                st.info("Insufficient system logs for metrics matrix.")
                
        with col2:
            st.write("### Fleet Status Metric Spread")
            if bus_data:
                df_bus = pd.DataFrame(bus_data, columns=["Fleet Status", "Count"])
                st.line_chart(df_bus.set_index("Fleet Status"))
            else:
                st.info("No system asset fleet data recorded.")
                
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Analytical Layer Error: {e}")