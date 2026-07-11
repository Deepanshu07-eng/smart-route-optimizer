import mysql.connector
from mysql.connector import Error
import streamlit as st

def get_db_connection():
    try:
        # Hum direct root se connect karenge taaki access denied ka chance hi na rahe
        connection = mysql.connector.connect(
            host='localhost',
            user='root',         # <--- 'bususer' ki jagah 'root' kar diya
            password='',         # <--- Agar root ka koi password rakha tha toh yahan likho, nahi toh blank "" chhod do
            database='bus_route_system'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                roll_number VARCHAR(50) UNIQUE NOT NULL,
                phone_number VARCHAR(20),
                pickup_location TEXT,
                latitude DECIMAL(10, 8) DEFAULT 0.0,
                longitude DECIMAL(11, 8) DEFAULT 0.0,
                route_id INT DEFAULT NULL
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS buses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bus_number VARCHAR(50) UNIQUE NOT NULL,
                capacity INT NOT NULL,
                driver_name VARCHAR(255),
                driver_phone VARCHAR(20),
                status VARCHAR(50) DEFAULT 'Available'
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                route_name VARCHAR(100) UNIQUE NOT NULL,
                bus_id INT,
                start_point TEXT,
                end_point TEXT
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                date DATE,
                status VARCHAR(20),
                UNIQUE KEY unique_student_date (student_id, date)
            )
            """)
            
            connection.commit()
            cursor.close()
        return connection
    except Error as e:
        st.error(f"❌ MySQL Live Connection Error: {e}")
        return None