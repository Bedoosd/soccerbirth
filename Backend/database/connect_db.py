from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

def get_connection():
    try:
        return psycopg2.connect(
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"]
        )
    except KeyError as e:
        raise RuntimeError(f"Omgevingsvariabele ontbreekt: {e}")