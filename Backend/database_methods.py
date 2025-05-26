
from dotenv import load_dotenv
from datetime import datetime, date
import pandas as pd
import os
import psycopg2
import warnings

class Database:
    @staticmethod
    def get_connection():
        load_dotenv()

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

    @staticmethod
    def set_cursor():
        conn = Database.get_connection()
        cursor = conn.cursor()
        return conn,cursor

    @staticmethod
    def get_bool(query, parameters = None):
        conn, cursor = Database.set_cursor()
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

    @staticmethod
    def get_df(query, parameters = None):
        conn = Database.get_connection()  #cursor wordt hier zelf aangemaakt door pd; set_cursor niet nodig
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

    @staticmethod
    def get_date(query, parameters = None):
        conn, cursor = Database.set_cursor()
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

    @staticmethod
    def write_value(query, parameters=None):
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, parameters)
            conn.commit()  # zorg dat wijzigingen worden opgeslagen
        except Exception as e:
            print(f"Error while writing to database: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def write_many(query, parameters_list):
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(query, parameters_list)
            conn.commit()
        except Exception as e:
            print(f"Error while performing batch write: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
