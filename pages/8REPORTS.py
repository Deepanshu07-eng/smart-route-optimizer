import streamlit as st
from db_helper import get_db_connection
import pandas as pd

st.title("📋 Automated Management Report Generation")

report_type = st.selectbox("Choose Core Operational Layer", ["Students Registry", "Fleet Inventory Summary"])

if st.button("Compile Systems Live Audit Data"):
    conn = get_db_connection()
    if conn:
        try:
            if report_type == "Students Registry":
                query = "SELECT roll_number, name, phone_number, pickup_location FROM students"
            else:
                query = "SELECT bus_number, capacity, driver_name, status FROM buses"
                
            df = pd.read_sql(query, conn)
            conn.close()
            
            if not df.empty:
                st.write("### Audit Document Review Matrix")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Official Operational Report Sheet (.CSV)",
                    data=csv,
                    file_name=f"{report_type.lower().replace(' ', '_')}_report.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Selected target component collection logs are currently blank.")
        except Exception as e:
            st.error(f"Reporting Layer Exception: {e}")