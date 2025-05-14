class Country:
    def __init__(self, name):
        self.name = name

    def has_monthly_data(self, tournament_name, tournament_year):
        #code om te kijken of er maandelijkse data beschikbaar is voor Toernooi, jaar en land.
        #return True/False
        pass

    def has_yearly_data(self, tournament_name, tournament_year):
        #code om te kijken of er jaarlijkse data beschikbaar is.
        #return True/False
        pass

    def get_monthly_data(self, tournament_name, tournament_year):
        #code om de juiste data op te halen om in grafiek te steken
        #return dataframe
        pass

    def get_yearly_data(self, tournament_name, tournament_year):
        #code om de juiste data op te halen om in grafiek te steken
        #return dataframe
        pass
