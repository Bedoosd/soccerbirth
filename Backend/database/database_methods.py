
from dotenv import load_dotenv
from datetime import datetime, date
import pandas as pd
import os
import psycopg2

class Database:
    def __init__(self):

        load_dotenv()

    def get_connection(self):

        try:
            return psycopg2.connect(
                host=os.environ["DB_HOST"],
                database=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                options = '-c search_path=soccerbirth_staging'

            )
        except KeyError as e:
            raise RuntimeError(f"Omgevingsvariabele ontbreekt: {e}")

    def set_cursor(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        return conn,cursor

    def get_bool(self, query):
        conn, cursor = self.set_cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()[0] #fetchone geeft steeds een tuple terug, steeds eerste resultaat er uit halen
            print (f"result_getbool = {result}")
            if isinstance(result, bool): return result
            else: raise TypeError (f"expected a boolean, got result: {result} : {type(result)}")

        except TypeError as e:
            print(f"Error trying to get a boolean from get_bool: {e}, : check query!")
        finally:
            cursor.close()
            conn.close()

    def get_df(self, query):
        conn = self.get_connection()  #cursor wordt hier zelf aangemaakt door pd; set_cursor niet nodig
        try:
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()

    def get_date(self, query):
        conn, cursor = self.set_cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()[0]
            if isinstance(result, (datetime, date)):
                    return result.date() if isinstance(result, datetime) else result
            else: raise TypeError (f"expected a datetime, got result: {result} : {type(result)}")
        except TypeError as e:
            print(f"Error trying to get a date from get_date: {e}, : check query!")
        finally:
            cursor.close()
            conn.close()
