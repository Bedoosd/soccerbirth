from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

from Backend.tournament import Tournament, get_data


class Country:
    def __init__(self, name, tournament : Tournament):
        self.tournament = tournament
        self.country = name


    def has_monthly_data(self):
        self.tournament.set_tournament_date_and_target()
        selected_country = self.country
        target = self.tournament.target_date
        query = """ """ # query om te kijken of er maandelijkse data is voor het land rond de target
        result = get_data(query)
        check = bool #niet zeker hoe dit moet gebeuren met resultaat van query
        return check

    def has_yearly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        query = """ """ #query om te kijken of er jaarlijkse data is
        result = get_data(query)
        check = bool
        return check

    def get_monthly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(months=6)  #als nodig, hier de maand en jaar uit halen
        end_date = target + relativedelta(months=6)
        query = """ """ #om geboortedata op te halen tussen start en eind
        df = get_data(query)
        return pd.DataFrame({
            "month": ["Jan", "Feb", "Mar", "Apr"],
            "births": [100, 120, 90, 110]
            })

    def get_yearly_data(self):
        selected_country = self.country
        target = self.tournament.target_date
        start_date = target - relativedelta(years=3)  # als nodig, hier het jaar uithalen
        end_date = target + relativedelta(years=3)
        query = """ """  # om geboortedata op te halen tussen start en eind
        df = get_data(query)
        return pd.DataFrame({
            "years": ["2020", "2021", "2022"],
            "births": [1200, 1300, 1250]
            })
