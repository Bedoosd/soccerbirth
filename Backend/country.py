from dateutil.relativedelta import relativedelta

from Backend.database_methods import Database
from Backend.tournament import Tournament

class Country:
    def __init__(self, name, tournament : Tournament):
        self.db = Database()
        self.tournament = tournament
        self.country = name

    def has_monthly_data(self):
        self.tournament.set_tournament_date_and_target()
        selected_country = self.country
        target_year = self.tournament.target_year
        target_month = self.tournament.target_month
        query = """select exists (select 1 from births_per_yearmonth 
                    where country = %s 
                    and year = %s and month = %s
                    and value is not Null)
                     """
        parameters = [selected_country, target_year, target_month]
        return self.db.get_bool(query, parameters)

    def has_yearly_data(self):
        selected_country = self.country
        target_year = self.tournament.target_year
        query = """select exists (select 1 from births_per_year 
                        where country = %s and year = %s and total is not Null)"""
        parameters = [selected_country, target_year]
        return self.db.get_bool(query, parameters)

    def get_monthly_data(self):
        tournament_month = self.tournament.tournament_month
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(months=6)
        end_date = target + relativedelta(months=6)
        target_month = self.tournament.target_month
        query = """select distinct year, month, value as births,
        to_date(concat(year, '-', month), 'YYYY-Month') as sort_datum,
        concat(month, ' ', year) as month_year
        from births_per_yearmonth
        where country = %s
        and month in ('January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December')
        and to_date(concat(year, '-', month), 'YYYY-Month')
        between %s and %s
        and value is not Null
        order by sort_datum;
                    """
        parameters = [selected_country, start_date, end_date]
        df = self.db.get_df(query, parameters)

        #index in df needed in shiny, doesnt work wel with strings
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
        target_date = self.tournament.target_date
        start_date = target_date - relativedelta(years=4)
        end_date = target_date + relativedelta(years=4)
        tournament_year = self.tournament.tournament_year
        target_year = int(tournament_year) + 1
        query = """select country, year, total as births
                    from births_per_year
                    where year between %s and %s
                    and country = %s
                    order by year"""
        parameters = [start_date.year, end_date.year, selected_country]
        df = self.db.get_df(query, parameters)

        return df, tournament_year, target_year
