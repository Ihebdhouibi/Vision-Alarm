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
        conn = psycopg2.connect(host= "127.0.0.1",
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

def storeMouvementAlertData(alertTime, videoLink, AlertClass):
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
        conn = psycopg2.connect(host= "127.0.0.1",
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
    query = "insert into mouvement_alerts (alert_time, video_link, class) values ( %s, %s, %s)"



    cursor.execute(query, (alertTime, videoLink, AlertClass))
    conn.commit()

    # Close connection
    conn.close()

def retrieveAlertData():
    """
    TODO: develop a method that fetch data from AlertsTables
    """

storeFireAlertData("{20:20:20}", "{link}", True)
storeMouvementAlertData("{20:20:20}", "{link}", True)