import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT version();"))
    for row in result:
        print(f"Verbinding geslaagd: {row[0]}")


# Voorbeeld: tabel 'wk_teams'
# df = pd.read_sql("SELECT * FROM soccerbirth_staging.euro_high_level", con=engine)


# print(df.head())
