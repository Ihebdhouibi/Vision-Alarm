import psycopg2
from configparser import ConfigParser
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    try:
        conn = psycopg2.connect(host="127.0.0.1",
                                user="postgres",
                                database="visionalarm",
                                password="root",
                                port="5432")
        cursor = conn.cursor()
        yield cursor, conn
    except Exception as error:
        print(f"Error while connecting to PostgreSQL: {error}")
    finally:
        conn.close()

def add_user(username, password):
    with get_db_connection() as (cursor, conn):
        query = "insert into users (username, password) values (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()    
    
def add_camera(address, nom):

    with get_db_connection() as (cursor, conn):
        try:
            query = "SELECT COUNT(*) FROM cameras"
            cursor.execute(query)
            number_cam = cursor.fetchone()[0]

            if number_cam < 4:
                query = "INERT INTO cameras (address, nom) VALUES (%s, %s)"
                cursor.execute(query, (address, nom))
                conn.commit()
            else:
                print("Maximun number of cameras added already")
        except Exception as e:
            print(f"Error adding camera: {e}")

def remove_camera(id):
    pass

def store_alert_data(alert_time, video_link, alert_class, alert_type):
    
    query = f"INSERT INTO {alert_type}_alerts (alert_time, video_link, class) VALUES (%s, %s, %s)"

    with get_db_connection() as (cursor, conn):
        try:
            cursor.execute(query, (alert_time, video_link, alert_class))
            conn.commit()
        except Exception as e:
            print(f"Error inserting alert into {alert_type}_alerts: {e}")

def retrieve_alerts(alert_type):
    
    query=f"SELECT * FROM {alert_type}_alerts"

    with get_db_connection() as (cursor, conn):
        cursor.execute(query)
        alerts = cursor.fetchall()
        print(f"{alert_type.capitalize()} alerts: \n ----------------------------------------------- \n")
        
        for row in alerts:
            print(f"ID: {row[0]} | Alert Time: {row[1]} | Video Link; {row[2]} | Class: {row[3]}")

def retrieve_all_alerts():

    retrieve_alerts("fire")
    retrieve_alerts("fall")
    retrieve_alerts("robbery")
    
def retrieve_users():

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        try:
            query = "select * from users"
            cursor.execute(query)
    
            result = cursor.fetchall()
            for row in result:
                print(f"ID: {row[0]} | Username: {row[1]}")
        except Exception as e:
            print(f"Error retrieving users: {e}")
        
def remove_camera(camera_id):

    with get_db_connection() as (cursor, conn):
        
        try:
            query = "DELETE FROM cameras WHERE id = %s"
            cursor.execute(query, (camera_id))
            conn.commit()
            print(f"Camera with ID {camera_id} removed successfully.")
        except Exception as e:
            print(f"Error removing camera: {e}")
