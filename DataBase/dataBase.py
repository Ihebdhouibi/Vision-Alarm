import psycopg2
from configparser import ConfigParser

def add_user(username, password):
    cursor, conn = connect()

    query = "insert into users (username, password) values (%s, %s)"

    cursor.execute(query, (username, password))
    conn.commit()

    conn.close()

def connect():
    try:
        conn = psycopg2.connect(host="127.0.0.1",
                                user="postgres",
                                database="visionalarm",
                                password="root",
                                port="5432")
        cursor = conn.cursor()
        # print connexion settings
        print("Connexion settings : ", conn.get_dsn_parameters())
    except (Exception, psycopg2.Error) as error:
        print("Error while trying to connect to PostgreSQL ", error)

    return cursor, conn

def add_camera(address, nom):

    cursor, conn = connect()

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

    conn.close()

def remove_camera(id):
    pass


def storeFireAlertData(alertTime, videoLink, AlertClass):

    cursor, conn = connect()
    # Connection achieved
    # Storing alert data
    query = "insert into fire_alerts (alert_time, video_link, class) values ( %s, %s, %s)"

    cursor.execute(query, (alertTime, videoLink, AlertClass))
    conn.commit()

    # Close connection
    conn.close()


def storeFallAlertData(alertTime, videoLink, AlertClass):
    # Try connection
    cursor, conn = connect()
    # Connection achieved
    # Storing alert data
    try:
        query = "insert into fall_alerts (alert_time, video_link, class) values (%s, %s, %s)"

        cursor.execute(query, (alertTime, videoLink, AlertClass))
        conn.commit()
    except Exception as e:
        print("There is an issue inserting alert information into fall_alerts")
    # close connection
    conn.close()


def storeRobberyAlertData(alertTime, videoLink, AlertClass):

    cursor, conn = connect()
    # Connection achieved
    # Storing alert data
    query = "insert into robbery_alerts (alert_time, video_link, class) values ( %s, %s, %s)"

    cursor.execute(query, (alertTime, videoLink, AlertClass))
    conn.commit()

    # Close connection
    conn.close()


def retrieve_fire_alerts():

    cursor, conn = connect()

    query = "select * from fire_alerts"
    cursor.execute(query)
    print("Fire alerts : \n ------------------------------------ \n")
    fire_alerts = cursor.fetchall()
    for row in fire_alerts:
        print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")

    conn.close()


def retrieve_fall_alerts():

    cursor, conn = connect()
    query = "select * from fall_alerts"
    cursor.execute(query)
    print("Fall alerts : \n ------------------------------------ \n")
    fall_alerts = cursor.fetchall()
    for row in fall_alerts:
        print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")

    conn.close()


def retrieve_robbery_alerts():

    cursor, conn = connect()

    query = "select * from robbery_alerts"
    cursor.execute(query)
    print("Robbery alerts : \n ------------------------------------ \n")
    robbery_alerts = cursor.fetchall()
    for row in robbery_alerts:
        print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")

    conn.close()


def retrieve_all_alerts():

    cursor, conn = connect()

    retrieve_fire_alerts()
    retrieve_fall_alerts()
    retrieve_robbery_alerts()
    conn.close()

# storeFireAlertData("{20:20:20}", "{link}", True)
# storeMouvementAlertData("{20:20:20}", "{link}", True)

def retrieve_users():
    cursor, conn = connect()

    query = "select * from users"
    cursor.execute(query)

    result = cursor.fetchall()
    for row in result:
        print(f"id {row[0]} | username : {row[1]}  | password : {row[2]}")

    conn.close()

# add_user("user", "user")

# retrieve_users()