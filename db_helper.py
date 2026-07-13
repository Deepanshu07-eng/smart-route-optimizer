import streamlit as st
import mysql.connector
from mysql.connector import Error


def get_database_config():
    """Local aur deployed database configuration return karta hai."""

    if "mysql" in st.secrets:
        return {
            "host": st.secrets["mysql"]["host"],
            "port": int(st.secrets["mysql"]["port"]),
            "user": st.secrets["mysql"]["user"],
            "password": st.secrets["mysql"]["password"],
            "database": st.secrets["mysql"]["database"],
            "ssl_disabled": False,
        }

    return {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "bus_route_system",
    }


def get_db_connection(show_error=True):
    """Fresh MySQL connection return karta hai."""

    try:
        config = get_database_config()

        connection = mysql.connector.connect(
            **config,
            connection_timeout=10,
            autocommit=True,
        )

        return connection

    except Error as error:
        if show_error:
            st.error(f"Database connection failed: {error}")
        return None


def close_db_connection(connection, cursor=None):
    """Cursor aur database connection safely close karta hai."""

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