from datetime import timedelta

from Backend.database_methods import Database


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

    def set_tournament_date_and_target(self, country):
        tournament_name = self.tournament_name
        tournament_year = int(self.tournament_year)
        print(tournament_name, tournament_year, country)
        query = ("select date_match from soccerbirth_dataproducts.dp_stats_round "
                 "where tournament = %s and year = %s and country_name = %s")
        parameters = (tournament_name, tournament_year, country)
        date = self.db.get_date(query, parameters)

        self.tournament_date = date
        self.target_date = date + timedelta(days=266)
        self.tournament_month = self.tournament_date.strftime('%B') #Gives the name of the month
        self.target_month = self.target_date.strftime('%B')
        self.target_year = self.target_date.strftime('%Y')
        return

    def get_available_years(self):
        selected_tournament = self.tournament_name
        query = "select year, host from soccerbirth_dwh.fact_tournaments_high_level where tournament = %s "
        parameters = [selected_tournament]
        return self.db.get_df(query, parameters)

    def get_available_countries(self):

        selected_tournament = self.tournament_name
        selected_year = self.tournament_year

        query = ("select country_name, iso_code  from soccerbirth_dataproducts.dp_stats_round "
                 "where tournament = %s and year = %s")
        parameters = [selected_tournament, selected_year]
        return self.db.get_df(query, parameters)
