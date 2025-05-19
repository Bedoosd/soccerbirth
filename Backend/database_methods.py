
from dotenv import load_dotenv
from datetime import datetime, date
import pandas as pd
import os
import psycopg2
import warnings


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

    def get_bool(self, query, parameters = None):
        conn, cursor = self.set_cursor()
        try:
            cursor.execute(query, parameters)
            result = cursor.fetchone()[0] #fetchone geeft steeds een tuple terug, steeds eerste resultaat er uit halen
            if isinstance(result, bool): return result
            else: raise TypeError (f"expected a boolean, got result: {result} : {type(result)}")

        except TypeError as e:
            print(f"Error trying to get a boolean from get_bool: {e}, : check query!")
        finally:
            cursor.close()
            conn.close()

    def get_df(self, query, parameters = None):
        conn = self.get_connection()  #cursor wordt hier zelf aangemaakt door pd; set_cursor niet nodig
        try:
            #ignores following warning from pandas:
            #pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection.
            # Other DBAPI2 objects are not tested. Please consider using SQLAlchemy
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = pd.read_sql_query(query, conn, params=parameters)
            return df
        finally:
            conn.close()

    def get_date(self, query, parameters = None):
        conn, cursor = self.set_cursor()
        try:
            cursor.execute(query, parameters)
            result = cursor.fetchone()[0]
            if isinstance(result, (datetime, date)):
                    return result.date() if isinstance(result, datetime) else result
            else: raise TypeError (f"expected a datetime, got result: {result} : {type(result)}")
        except TypeError as e:
            print(f"Error trying to get a date from get_date: {e}, : check query!")
        finally:
            cursor.close()
            conn.close()
