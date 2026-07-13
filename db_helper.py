import streamlit as st
import mysql.connector
from mysql.connector import Error


def create_tables(connection):
    cursor = None

    try:
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
                bus_id INT DEFAULT NULL,
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

    except Error as error:
        connection.rollback()
        st.error(f"Table creation failed: {error}")

    finally:
        if cursor is not None:
            cursor.close()


def get_db_connection():
    try:
        # Streamlit Cloud / TiDB
        if "mysql" in st.secrets:
            connection = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                port=int(st.secrets["mysql"]["port"]),
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                database=st.secrets["mysql"]["database"],
                ssl_disabled=False,
                connection_timeout=20
            )

        # Local PC / XAMPP
        else:
            connection = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="root",
                password="",
                database="bus_route_system",
                connection_timeout=10
            )

        if connection.is_connected():
            create_tables(connection)
            return connection

        st.error("Database connection could not be established.")
        return None

    except Error as error:
        st.error(f"Database connection failed: {error}")
        return None

    except Exception as error:
        st.error(f"Unexpected database error: {error}")
        return None


def close_db_connection(connection, cursor=None):
    try:
        if cursor is not None:
            cursor.close()
    except Exception:
        pass

    try:
        if connection is not None and connection.is_connected():
            connection.close()
    except Exception:
        pass