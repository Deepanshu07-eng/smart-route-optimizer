import mysql.connector

def get_connection():
    return mysql.connector.connect(
    host="localhost",
    user="bususer",
    password="bus123",
    database="bus_route_system",
    port=3306

    )