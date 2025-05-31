from dateutil.relativedelta import relativedelta

from Backend.database_methods import Database
from Backend.tournament import Tournament
from datetime import date, timedelta

class Country:
    def __init__(self, name, tournament : Tournament):
        self.tournament = tournament
        self.country = name

    def has_monthly_data(self):

        selected_country = self.country
        self.tournament.set_tournament_date_and_target(selected_country)
        target_year = self.tournament.target_year
        target_month = self.tournament.target_month
        query = ("select exists (select 1 from soccerbirth_dataproducts.dp_births_figures "
                 "where country = %s and month = %s and year = %s)")

        parameters = [selected_country, target_month, target_year]
        return Database.get_bool(query, parameters)

    def has_yearly_data(self):
        selected_country = self.country
        target_year = self.tournament.target_year
        query = (" select exists (select 1 from soccerbirth_dataproducts.dp_births_figures "
                 "where country = %s and year = %s and source = 'births_per_year')")
        parameters = [selected_country, target_year]
        return Database.get_bool(query, parameters)

    def get_monthly_data(self, months_margin):
        tournament_month = self.tournament.tournament_month
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(months=months_margin)
        end_date = target + relativedelta(months=months_margin)
        target_month = self.tournament.target_month
        target_month_year = f"{target_month} {self.tournament.target_year}"
        tournament_month_year = f"{tournament_month} {self.tournament.tournament_year}"
        query = ("select year_month_txt, year, month, value as births from soccerbirth_dataproducts.dp_births_figures "
                 "where country = %s and source = 'births_year_month'"
                 "and date_month between %s and %s")

        parameters = [selected_country, start_date, end_date]
        df = Database.get_df(query, parameters)

        #index in df needed in shiny, doesn't work well with strings
        try:
            tournament_marker = df[df["year_month_txt"] == tournament_month_year].index[0]
        except IndexError:
            tournament_marker = None

        try:
            target_marker = df[df["year_month_txt"] == target_month_year].index[0]
        except IndexError:
            target_marker = None

        return df, tournament_marker, target_marker

    def get_data_same_months(self):
        #this returns 3 dataframes. Months + births from: target, target plus 1year, target minus 1year
        #each dataframe contains 3months (target +/- 1 month)
        selected_country = self.country

        target_month_base = date(self.tournament.target_date.year, self.tournament.target_date.month, 1)
        start_date = target_month_base - relativedelta(months=1)
        end_date = target_month_base + relativedelta(months=1)
        #check
        #print (f"target: {target_month_base}, start_date: {start_date}, end_date: {end_date} ")

        target_month_minus1year_base = target_month_base - relativedelta(years=1)
        start_date_minus_1 = target_month_minus1year_base - relativedelta(months=1)
        end_date_minus_1 = target_month_minus1year_base + relativedelta(months=1)
        #check
        #print (f"target_minus1: {target_month_minus1year_base}, start_date: {start_date_minus_1}, end_date: {end_date_minus_1}")

        target_month_plus1year_base = target_month_base + relativedelta(years=1)
        start_date_plus_1 = target_month_plus1year_base - relativedelta(months=1)
        end_date_plus_1 = target_month_plus1year_base + relativedelta(months=1)
        #check
        #print (f"target_plus1: {target_month_plus1year_base}, start_date: {start_date_plus_1}, end_date: {end_date_plus_1}")

        query = ("select year, month, value as births from soccerbirth_dataproducts.dp_births_figures "
                 "where country = %s and source = 'births_year_month'"
                 "and date_month between %s and %s")
        parameters = [selected_country, start_date, end_date]
        parameters1 = [selected_country, start_date_minus_1, end_date_minus_1]
        parameters2 = [selected_country, start_date_plus_1, end_date_plus_1]
        df = Database.get_df(query, parameters)
        df_minus1 = Database.get_df(query, parameters1)
        df_plus1 = Database.get_df(query, parameters2)

        return df, df_minus1, df_plus1


    def get_yearly_data(self, years_margin):
        selected_country = self.country
        target_date = self.tournament.target_date
        start_date = target_date - relativedelta(years=years_margin)
        end_date = target_date + relativedelta(years=years_margin)
        tournament_year = self.tournament.tournament_year
        target_year = int(tournament_year) + 1
        query = ("select country, year, value as births from soccerbirth_dataproducts.dp_births_figures "
                 "where country = %s and source = 'births_per_year' and year between %s and %s order by year")

        parameters = [selected_country, start_date.year, end_date.year]
        df = Database.get_df(query, parameters)

        return df, int(tournament_year), target_year
