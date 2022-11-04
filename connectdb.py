import os
import time
import mysql.connector
from pandas.io import sql
from openpyxl import load_workbook

config = {
    "user": os.environ["DATABASE_USER"],
    "password": os.environ["DATABASE_PASSWORD"],
    "host": os.environ["DATABASE_HOST"],
    "database": os.environ["DATABASE_NAME"],
    "raise_on_warnings": True,
}


class ConnectDB:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        print(self.cnx)

    def close_connection_db(self, cnx):
        cnx.close()

    def add_frase(
        self, tiemporespuesta, remote_addr, user_agent, fraseinput, fraseoutput
    ):
        try:
            add_frase_predict = (
                "INSERT INTO log_predict "
                "(tiemporespuesta, fraseinput, fraseoutput, origin, useragent) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            data_frase_predict = (
                tiemporespuesta,
                fraseinput,
                fraseoutput,
                remote_addr,
                user_agent,
            )
            cursor = self.cnx.cursor()
            cursor.execute(add_frase_predict, data_frase_predict)
            id_frase_predict = cursor.lastrowid
            self.cnx.commit()
            cursor.close()
            return id_frase_predict
        except Exception as exception_error:
            print(exception_error)
            return 0

    def get_predicciones(self):
        get_frases = (
            "SELECT fechapredict, tiemporespuesta, fraseinput, fraseoutput, iscorrect "
            "FROM log_predict WHERE fechapredict "
            "ORDER BY fechapredict DESC"
        )
        df_log_predict = sql.read_sql(get_frases, self.cnx)
        directory = "temp"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name_temp = f"{directory}/{time.time()}_temp.xlsx"
        df_log_predict.to_excel(file_name_temp)
        wb_log_predict = load_workbook(file_name_temp)
        wb_log_predict.save(file_name_temp)
        return file_name_temp
