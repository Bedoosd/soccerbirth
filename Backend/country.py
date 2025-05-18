from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

from Backend.database.database_methods import Database
from Backend.tournament import Tournament


def get_bool(query):
    #enkel tijdelijk tot functie is gemaakt in database backend
    pass

class Country:
    def __init__(self, name, tournament : Tournament):
        self.db = Database()
        self.tournament = tournament
        self.country = name

    def has_monthly_data(self):
        print("check")
        self.tournament.set_tournament_date_and_target()
        selected_country = self.country
        target = self.tournament.target_date
        query = f"""select exists (select 1 from births_per_yearmonth 
                    where country = '{selected_country}' 
                    and year = '{self.tournament.target_year}' 
                    and month = '{self.tournament.target_month}')"""
        return self.db.get_bool(query)

    def has_yearly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        query = """ """ #query om te kijken of er jaarlijkse data is
        result = get_bool(query)
        check = bool
        return check

    def get_monthly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(months=6)  #als nodig, hier de maand en jaar uit halen
        end_date = target + relativedelta(months=6)
        query = """ """ #om geboortedata op te halen tussen start en eind
        df = get_dataframe(query)
        tournament_month = self.tournament.tournament_month
        target_month = self.tournament.target_month
        #markers needed to get the index for the shiny app, doesnt work well with strings
        try:
            tournament_marker = df[df["month"] == tournament_month].index[0]
        except IndexError:
            tournament_marker = None

        try:
            target_marker = df[df["month"] == target_month].index[0]
        except IndexError:
            target_marker = None

        return df, tournament_marker, target_marker


    def get_yearly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(years=3)  # als nodig, hier het jaar uithalen
        end_date = target + relativedelta(years=3)
        query = """ """  # om geboortedata op te halen tussen start en eind
        df = get_dataframe(query)
        tournament_year = self.tournament.tournament_date.year
        target_year = tournament_year + 1

        return df, tournament_year, target_year
