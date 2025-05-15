from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

from Backend.tournament import Tournament, get_dataframe

def get_bool(query):
    #enkel tijdelijk tot functie is gemaakt in database backend
    pass

class Country:
    def __init__(self, name, tournament : Tournament):
        self.tournament = tournament
        self.country = name


    def has_monthly_data(self):
        self.tournament.set_tournament_date_and_target()
        selected_country = self.country
        target = self.tournament.target_date
        query = """ """ # query om te kijken of er maandelijkse data is voor het land rond de target
        result = get_bool(query)
        check = bool #niet zeker hoe dit moet gebeuren met resultaat van query
        return check

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
        return df

    def get_yearly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(years=3)  # als nodig, hier het jaar uithalen
        end_date = target + relativedelta(years=3)
        query = """ """  # om geboortedata op te halen tussen start en eind
        df = get_dataframe(query)
        return df
