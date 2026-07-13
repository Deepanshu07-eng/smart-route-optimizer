import streamlit as st
import mysql.connector
from mysql.connector import Error


def get_db_config():
    """
    Local computer aur Streamlit Cloud dono ke liye
    database configuration return karta hai.
    """

    try:
        # Streamlit Cloud / secrets.toml configuration
        return {
            "host": st.secrets["mysql"]["host"],
            "port": int(st.secrets["mysql"].get("port", 3306)),
            "user": st.secrets["mysql"]["user"],
            "password": st.secrets["mysql"]["password"],
            "database": st.secrets["mysql"]["database"],
        }

    except (KeyError, FileNotFoundError):
        # Local MySQL configuration
        return {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "bus_route_system",
        }


def create_tables(connection):
    """
    Required database tables create karta hai.
    Tables already present hon to unhe delete nahi karega.
    """

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
                start_point TEXT NOT NULL,
                end_point TEXT NOT NULL,
                distance_km DECIMAL(10, 2) DEFAULT 0.00,
                estimated_time VARCHAR(50),
                route_status VARCHAR(30) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL,
                UNIQUE KEY unique_student_date (student_id, date)
            )
        """)

        connection.commit()

    except Error as error:
        connection.rollback()
        raise RuntimeError(f"Table creation failed: {error}") from error

    finally:
        if cursor is not None:
            cursor.close()


def get_db_connection(show_error=True):
    """
    MySQL connection create karke return karta hai.
    Connection fail hone par None return karta hai.
    """

    try:
        config = get_db_config()

        connection = mysql.connector.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            connection_timeout=15,
            autocommit=False,
        )

        # New connector versions mein connected property recommended hai.
        if not connection.connected:
            if show_error:
                st.error("Database connection establish nahi ho paya.")
            return None

        create_tables(connection)

        return connection

    except Error as error:
        if show_error:
            st.error(f"Database connection failed: {error}")
        return None

    except RuntimeError as error:
        if show_error:
            st.error(str(error))
        return None

    except Exception as error:
        if show_error:
            st.error(f"Unexpected database error: {error}")
        return None


def close_db_connection(connection, cursor=None):
    """
    Cursor aur connection safely close karta hai.
    """

    try:
        if cursor is not None:
            cursor.close()
    except Error:
        pass

    try:
        if connection is not None and connection.connected:
            connection.close()
    except Error:
        pass