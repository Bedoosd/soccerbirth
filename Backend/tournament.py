def get_data(query):
    #even toegevoegd om rode lijn weg te krijgen
    pass

class Tournament:
    def __init__(self, tournament_name, tournament_year=None):
        self.tournament_name = tournament_name
        self.tournament_year = tournament_year

    def get_available_years(self):
        selected_tounament = self.tournament_name
        query = """ """ #query om juiste jaren binnen te halen (jaar, organiserend land?)
        df = get_data(query) #get_data stelt de geinporteerde functie (uit backend/database) voor die een df teruggeeft
        return df

    def get_available_countries(self):
        selected_tournament = self.tournament_name
        selected_year = self.tournament_year
        query = """ """ #query om landen binnen te halen  (land, iso, ronde gehaald)
        df = get_data(query)
        return df
