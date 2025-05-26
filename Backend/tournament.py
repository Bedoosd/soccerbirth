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

    def set_tournament_date_and_target(self):
        tournament_name = self.tournament_name
        tournament_year = int(self.tournament_year)

        if tournament_name == "European Championship":
            query = "select date from euro_matches where year = %s and round = %s"
            parameters = [tournament_year, 'FINAL']
            date = self.db.get_date(query, parameters)

        elif tournament_name == "World Championship":
            #added like to query because for example 1950 had Final round instead of final
            query = "select date from world_cup_matches where year = %s and round like %s"
            parameters = [tournament_year, 'Final%']
            date = self.db.get_date(query, parameters)

        else:
            raise ValueError(f"Unsupported tournament: {tournament_name}")


        self.tournament_date = date
        self.target_date = date + timedelta(days=266)
        self.tournament_month = self.tournament_date.strftime('%B') #Gives the name of the month
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
        return self.db.get_df(query)

    def get_available_countries(self):

        selected_tournament = self.tournament_name
        selected_year = self.tournament_year
        if selected_tournament == "European Championship":
            query = """SELECT home_team AS country FROM euro_matches WHERE year = %s
                        UNION
                        SELECT away_team AS country FROM euro_matches WHERE year = %s"""

        elif selected_tournament == "World Championship":
            query = """SELECT home_team AS country FROM world_cup_matches WHERE year = %s
                        UNION
                        SELECT away_team AS country FROM world_cup_matches WHERE year = %s"""

        else:
            raise ValueError(f"Unsupported tournament: {selected_tournament}")
        parameters = [selected_year, selected_year]
        return self.db.get_df(query, parameters)
