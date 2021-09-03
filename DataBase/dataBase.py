import psycopg2
from configparser import ConfigParser


def storeFireAlertData(alertTime, videoLink, AlertClass):
    """

    TODO: develop a method that stores data alert in AlertsTable
    """
    # parser = ConfigParser()
    # parser.read(r'\home\iheb\PycharmProjects\Vision-Alarm\DataBase\config.ini')
    # host = parser.get("LOGIN", "host")
    # database = parser.get("LOGIN", "visionalarm")
    # password = parser.get("LOGIN", "password")
    # port = parser.get("LOGIN", "port")
    # user = parser.get("LOGIN", "user")

    # Try connection
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

    # Connection achieved
    # Storing alert data
    query = "insert into fire_alerts (alert_time, video_link, class) values ( %s, %s, %s)"

    cursor.execute(query, (alertTime, videoLink, AlertClass))
    conn.commit()

    # Close connection
    conn.close()


def storeFallAlertData(alertTime, videoLink, AlertClass):
    # Try connection
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

    # Connection achieved
    # Storing alert data
    try:
        query = "insert into fall_alerts (alert_time, video_link, class) values (%s, %s, %s)"

        cursor.execute(query, (alertTime, videoLink, AlertClass))
        conn.commit()
    except Exception as e :
        print("There is an issue inserting alert information into fall_alerts")
    # close connection
    conn.close()


def storeRobberyAlertData(alertTime, videoLink, AlertClass):
    """

    TODO: develop a method that stores data alert in AlertsTable
    """
    # parser = ConfigParser()
    # parser.read(r'\home\iheb\PycharmProjects\Vision-Alarm\DataBase\config.ini')
    # host = parser.get("LOGIN", "host")
    # database = parser.get("LOGIN", "visionalarm")
    # password = parser.get("LOGIN", "password")
    # port = parser.get("LOGIN", "port")
    # user = parser.get("LOGIN", "user")

    # Try connection
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

    # Connection achieved
    # Storing alert data
    query = "insert into robbery_alerts (alert_time, video_link, class) values ( %s, %s, %s)"

    cursor.execute(query, (alertTime, videoLink, AlertClass))
    conn.commit()

    # Close connection
    conn.close()


def retrieve_fire_alerts():
    """
    TODO: develop a method that fetch data from AlertsTables
    """
    try:
        conn = psycopg2.connect(host="127.0.0.1",
                                user="postgres",
                                database="visionalarm",
                                password="root",
                                port="5432")
        cursor = conn.cursor()
        print("Connection settings : ", conn.get_dsn_parameters())
    except (Exception, psycopg2.Error) as error:
        print("Error while trying to connect to PostgreSQL ",error)

    #
    query = "select * from fire_alerts"
    cursor.execute(query)
    print("Fire alerts : \n ------------------------------------ \n")
    fire_alerts = cursor.fetchall()
    for row in fire_alerts:
        print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")


def retrieve_fall_alerts():
    """
    TODO: develop a method that fetch data from AlertsTables
    """
    try:
        conn = psycopg2.connect(host="127.0.0.1",
                                user="postgres",
                                database="visionalarm",
                                password="root",
                                port="5432")
        cursor = conn.cursor()
        print("Connection settings : ", conn.get_dsn_parameters())
    except (Exception, psycopg2.Error) as error:
        print("Error while trying to connect to PostgreSQL ", error)

    #
    query = "select * from fall_alerts"
    cursor.execute(query)
    print("Fall alerts : \n ------------------------------------ \n")
    fall_alerts = cursor.fetchall()
    for row in fall_alerts:
        print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")


def retrieve_robbery_alerts():
    """
    TODO: develop a method that fetch data from AlertsTables
    """
    try:
        conn = psycopg2.connect(host="127.0.0.1",
                                user="postgres",
                                database="visionalarm",
                                password="root",
                                port="5432")
        cursor = conn.cursor()
        print("Connection settings : ", conn.get_dsn_parameters())
    except (Exception, psycopg2.Error) as error:
        print("Error while trying to connect to PostgreSQL ", error)

    #
    query = "select * from robbery_alerts"
    cursor.execute(query)
    print("Robbery alerts : \n ------------------------------------ \n")
    robbery_alerts = cursor.fetchall()
    for row in robbery_alerts:
        print(f"ID : {row[0]} | alert time : {row[1]} | video link : {row[2]} | class : {row[3]}")

def retrieve_all_alerts():
    try:
        conn = psycopg2.connect(host="127.0.0.1",
                                user="postgres",
                                database="visionalarm",
                                password="root",
                                port="5432")
        cursor = conn.cursor()
        print("Connection settings : ", conn.get_dsn_parameters())
    except (Exception, psycopg2.Error) as error:
        print("Error while trying to connect to PostgreSQL ", error)

    retrieve_fire_alerts()
    retrieve_fall_alerts()
    retrieve_robbery_alerts()

# storeFireAlertData("{20:20:20}", "{link}", True)
# storeMouvementAlertData("{20:20:20}", "{link}", True)
