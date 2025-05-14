class Tournament:
    def __init__(self, tournament_name, tournament_year=None):
        self.tournament_name = tournament_name
        self.tournament_year = tournament_year

    def get_available_years(self):
        #code om een lijst met alle jaartallen door te geven voor het EK of WK
        pass

    def get_available_countries(self):
        #tournament_year moet worden ingesteld in de shiny code als attribuut
        #code om een lijst met landen mee te geven, year wordt meegegeven vanuit shiny
        pass
