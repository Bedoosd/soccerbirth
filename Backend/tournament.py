from datetime import datetime, timedelta
import pandas as pd
from psycopg2.extras import wait_select

from Backend.database.database_methods import Database


class Tournament:
    def __init__(self, tournament_name, tournament_year=None):
        self.tournament_name = tournament_name
        self.tournament_year = tournament_year
        self.tournament_date = None
        self.target_date = None
        self.tournament_month = None
        self.target_month = None
        self.target_year = None   #target year is not necessarily the same as tournament_year
        self.db = Database()

    def set_tournament_date_and_target(self):
        tournament_name = self.tournament_name
        tournament_year = int(self.tournament_year)

        if tournament_name == "European Championship":
            #data van finale nog niet beschikbaar in databank
            date = datetime(tournament_year, 6, 15)

        elif tournament_name == "World Championship":
            query = f"select date from soccerbirth_staging.world_cup_matches where year = {tournament_year} and round = 'Final'"
            date = self.db.get_date(query)

        else:
            raise ValueError(f"Unsupported tournament: {tournament_name}")


        self.tournament_date = date
        self.target_date = date + timedelta(days=266)
        self.tournament_month = self.tournament_date.strftime('%B') #geeft meteen de benaming van de maand door
        self.target_month = self.target_date.strftime('%B')
        self.target_year = self.target_date.strftime('%Y')
        return

    def get_available_years(self):
        selected_tournament = self.tournament_name
        if selected_tournament == "European Championship":
            query = "select year from euro_high_level"
        elif selected_tournament == "World Championship":
            query = "select year, host from world_cup_high_level"
        else:
            raise ValueError(f"Unsupported tournament: {selected_tournament}")
        df = self.db.get_df(query)
        return df

    def get_available_countries(self):

        selected_tournament = self.tournament_name
        selected_year = self.tournament_year
        if selected_tournament == "European Championship":
            query = f"""SELECT home_team AS country
                        FROM euro_matches WHERE year = '{selected_year}'
                        UNION
                        SELECT away_team AS country
                        FROM euro_matches WHERE year = '{selected_year}';
                        """
        elif selected_tournament == "World Championship":
            query = f"""SELECT home_team AS country
                        FROM world_cup_matches WHERE year = '{selected_year}'
                        UNION
                        SELECT away_team AS country
                        FROM world_cup_matches WHERE year = '{selected_year}';
                        """
        else:
            raise ValueError(f"Unsupported tournament: {selected_tournament}")

        return self.db.get_df(query)
