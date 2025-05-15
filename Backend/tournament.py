from datetime import datetime, timedelta
import pandas as pd

def get_dataframe(query):
    #even toegevoegd om rode lijn weg te krijgen
    pass
def get_date(query):
    #same
    pass

class Tournament:
    def __init__(self, tournament_name, tournament_year=None):
        self.tournament_name = tournament_name
        self.tournament_year = tournament_year
        self.tournament_date = None
        self.target_date = None

    def set_tournament_date_and_target(self):
        tournament_name = self.tournament_name
        tournament_year = self.tournament_year
        query = """ """ #Welke datum?
        date = get_date(query)  # get_data stelt de geinporteerde functie (uit backend/database) voor
        self.tournament_date = datetime.strptime(date, '%m/%d/%Y')
        self.target_date = datetime.strptime(date, '%m/%d/%Y') + timedelta(days=266)
        return

    def get_available_years(self):
        selected_tournament = self.tournament_name
        query = """ """ #query om juiste jaren binnen te halen (jaar, organiserend land?)
        df = get_dataframe(query) #get_data stelt de geinporteerde functie (uit backend/database) voor die een df teruggeeft
        return df

    def get_available_countries(self):
        selected_tournament = self.tournament_name
        selected_year = self.tournament_year
        query = """ """ #query om landen binnen te halen  (land, iso, ronde gehaald)
        df = get_dataframe(query)
        return df
