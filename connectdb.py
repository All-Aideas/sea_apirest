import os
import mysql.connector

config = {
    'user': os.environ['DATABASE_USER'],
    'password': os.environ['DATABASE_PASSWORD'],
    'host': os.environ['DATABASE_HOST'],
    'database': os.environ['DATABASE_NAME'],
    'raise_on_warnings': True
}

class ConnectDB:
    
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        print(self.cnx)

    def close_connection_db(self, cnx):
        cnx.close()

    def add_frase(self, tiemporespuesta, fraseinput, fraseoutput):
        add_frase_predict = ("INSERT INTO log_predict "
                    "(tiemporespuesta, fraseinput, fraseoutput) "
                    "VALUES (%s, %s, %s)")
        data_frase_predict = (tiemporespuesta, fraseinput, fraseoutput)
        cursor = self.cnx.cursor()
        cursor.execute(add_frase_predict, data_frase_predict)
        id_frase_predict = cursor.lastrowid
        self.cnx.commit()
        cursor.close()
        return id_frase_predict
