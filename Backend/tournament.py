from datetime import datetime, timedelta
import pandas as pd

from Backend.database.database_methods import Database


class Tournament:
    def __init__(self, tournament_name, tournament_year=None):
        self.tournament_name = tournament_name
        self.tournament_year = tournament_year
        self.tournament_date = None
        self.target_date = None
        self.tournament_month = None
        self.target_month = None

    def set_tournament_date_and_target(self):
        tournament_name = self.tournament_name
        tournament_year = self.tournament_year
        query = """ """ #finale datum
        data = Database()
        date = data.get_date(query)
        self.tournament_date = datetime.strptime(date, '%m/%d/%Y')
        self.target_date = datetime.strptime(date, '%m/%d/%Y') + timedelta(days=266)
        self.tournament_month = self.tournament_date.strftime('%B') #geeft meteen de benaming van de maand door
        self.target_month = self.target_date.strftime('%B')
        return

    def get_available_years(self):
        selected_tournament = self.tournament_name
        if selected_tournament == "European Championship":
            query = "select year from euro_high_level"
        elif selected_tournament == "World Championship":
            query = "select year from world_cup_high_level"
        data =  Database()
        df = data.get_df(query)
        return df

    def get_available_countries(self):
        selected_tournament = self.tournament_name
        selected_year = self.tournament_year
        query = """ """ #query om landen binnen te halen  (land, iso, ronde gehaald)
        df = get_dataframe(query)
        return df
