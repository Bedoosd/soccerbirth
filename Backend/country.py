from dateutil.relativedelta import relativedelta

from Backend.database_methods import Database
from Backend.tournament import Tournament
from datetime import date, timedelta

class Country:
    def __init__(self, name, tournament : Tournament):
        self.tournament = tournament
        self.country = name

    def has_monthly_data(self):
        self.tournament.set_tournament_date_and_target()
        selected_country = self.country
        target_year = self.tournament.target_year
        target_month = self.tournament.target_month
        query = """select exists (select 1 from soccerbirth_staging.births_per_yearmonth 
                    where country = %s 
                    and year = %s and month = %s
                    and value is not Null)
                     """
        parameters = [selected_country, target_year, target_month]
        return Database.get_bool(query, parameters)

    def has_yearly_data(self):
        selected_country = self.country
        target_year = self.tournament.target_year
        query = """select exists (select 1 from births_per_year 
                        where country = %s and year = %s and total is not Null)"""
        parameters = [selected_country, target_year]
        return Database.get_bool(query, parameters)

    def get_monthly_data(self):
        tournament_month = self.tournament.tournament_month
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(months=12)
        end_date = target + relativedelta(months=12)
        target_month = self.tournament.target_month
        target_month_year = f"{target_month} {self.tournament.target_year}"
        tournament_month_year = f"{tournament_month} {self.tournament.tournament_year}"
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
        df = Database.get_df(query, parameters)

        #index in df needed in shiny, doesn't work well with strings
        try:
            tournament_marker = df[df["month_year"] == tournament_month_year].index[0]
        except IndexError:
            tournament_marker = None

        try:
            target_marker = df[df["month_year"] == target_month_year].index[0]
        except IndexError:
            target_marker = None

        return df, tournament_marker, target_marker

    def get_data_same_months(self):
        tournament_month = self.tournament.tournament_month
        selected_country = self.country
        target = self.tournament.target_date

        target_month_start = date(self.tournament.target_date.year, self.tournament.target_date.month, 1)
        start_date = target_month_start - relativedelta(months=1)
        end_date = target_month_start + relativedelta(months=2) - timedelta(days=1)

        target1_month_start = target_month_start - relativedelta(years=1)
        start_date_1 = target1_month_start - relativedelta(months=1)
        end_date_1 = target1_month_start + relativedelta(months=2) - timedelta(days=1)

        target2_month_start = target_month_start + relativedelta(years=1)
        start_date_2 = target2_month_start - relativedelta(months=1)
        end_date_2 = target2_month_start + relativedelta(months=2) - timedelta(days=1)

        target_month = self.tournament.target_month
        target_month_year = f"{target_month} {self.tournament.target_year}"
        target_month_year1 = f"{target_month} {int(self.tournament.target_year) -1}"
        target_month_year2 = f"{target_month} {int(self.tournament.target_year) +1}"

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
        parameters1 = [selected_country, start_date_1, end_date_1]
        parameters2 = [selected_country, start_date_2, end_date_2]
        df = Database.get_df(query, parameters)
        df1 = Database.get_df(query, parameters1)
        df2 = Database.get_df(query, parameters2)

        # index in df needed in shiny, doesn't work well with strings
        try:
            print (df)
            print( target_month_year)
            target_marker = df[df["month_year"] == target_month_year].index[0]
        except IndexError:
            target_marker = None

        try:
            target_marker1 = df1[df1["month_year"] == target_month_year1].index[0]
            print (df1)
            print (target_month_year1)
        except IndexError:
            target_marker1 = None

        try:
            target_marker2 = df2[df2["month_year"] == target_month_year2].index[0]
            print(df2)
            print (target_month_year2)
        except IndexError:
            target_marker2 = None


        return df, df1, df2, target_marker, target_marker1, target_marker2


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
        df = Database.get_df(query, parameters)

        return df, int(tournament_year), target_year
