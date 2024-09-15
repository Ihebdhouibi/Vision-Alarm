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
        query = "select * from cameras"
        cursor.execute(query)

        result = cursor.fetchall()
        number_cam = 0
        for rows in result:
            number_cam += 1

        print("Number cameras = ", number_cam)

        if number_cam < 4:
            query = "insert into cameras (address, nom) values (%s, %s)"
            cursor.execute(query, (address, nom))
            conn.commit()
        else:
            print("Maximum number of cameras added already")

def remove_camera(id):
    pass


def storeFireAlertData(alertTime, videoLink, AlertClass):

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "insert into fire_alerts (alert_time, video_link, class) values ( %s, %s, %s)"
        cursor.execute(query, (alertTime, videoLink, AlertClass))
        conn.commit()

def storeFallAlertData(alertTime, videoLink, AlertClass):

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "insert into fall_alerts (alert_time, video_link, class) values (%s, %s, %s)"
        cursor.execute(query, (alertTime, videoLink, AlertClass))
        conn.commit()

def storeRobberyAlertData(alertTime, videoLink, AlertClass):

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "insert into robbery_alerts (alert_time, video_link, class) values ( %s, %s, %s)"
        cursor.execute(query, (alertTime, videoLink, AlertClass))
        conn.commit()

def retrieve_fire_alerts():

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "select * from fire_alerts"
        cursor.execute(query)
        print("Fire alerts : \n ------------------------------------ \n")
        fire_alerts = cursor.fetchall()
        for row in fire_alerts:
            print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")


def retrieve_fall_alerts():

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "select * from fall_alerts"
        cursor.execute(query)
        print("Fall alerts : \n ------------------------------------ \n")
        fall_alerts = cursor.fetchall()
        for row in fall_alerts:
            print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")

def retrieve_robbery_alerts():

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "select * from robbery_alerts"
        cursor.execute(query)
        print("Robbery alerts : \n ------------------------------------ \n")
        robbery_alerts = cursor.fetchall()
        for row in robbery_alerts:
            print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")

def retrieve_all_alerts():

    retrieve_fire_alerts()
    retrieve_fall_alerts()
    retrieve_robbery_alerts()
    
def retrieve_users():

    # Establishing Connection to DB
    with get_db_connection() as (cursor, conn):
        query = "select * from users"
        cursor.execute(query)

        result = cursor.fetchall()
        for row in result:
            print(f"id {row[0]} | username : {row[1]}  | password : {row[2]}")
