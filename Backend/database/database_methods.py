
from dotenv import load_dotenv
from datetime import datetime, date
import pandas as pd
import os
import psycopg2

class Database:
    def __init__(self, name):
        self.name = name
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
            result = cursor.fetchone()
            if result is None:
                return False
            return bool(result[0])
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
            result = cursor.fetchone()
            if result is None or result[0] is None:
                raise ValueError (f"expected a date, got: {type(result)}")
            value = result[0]
            if isinstance(value, (datetime, date)):
                return value.date() if isinstance(value, datetime) else value
            raise ValueError(f"expected a date, got: {type(value)}")
        finally:
            cursor.close()
            conn.close()
