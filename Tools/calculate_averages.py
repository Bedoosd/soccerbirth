import math

from Backend.country import Country
from Backend.database_methods import Database


#de queries in country en tournament zijn nu wel nog afgestemd op de oude staging tabellen.
#deze zullen eerst moeten aangepast worden naar de nieuwe tabellen om volgende functie te laten werken

def calculate_averages(tournament_to_analyse):
    if tournament_to_analyse == "European Championship":
        query = "select table with country and tournament year - Euro"
    elif tournament_to_analyse == "World Championship":
        query = "select table with country and tournament year - World"
    else: raise ValueError("Invalid tournament name")

    df = Database.get_df(query)

    for index, row in df.iterrows():
        #niet zeker of hier nog iets als 'if row' of dergelijke nodig gaat zijn voor lege lijnen
        country_to_analyse = row["country"]
        year_to_analyse = row["year"]
        test = Country(country_to_analyse, tournament_to_analyse)
        test.tournament_year = year_to_analyse
        if test.has_monthly_data():
            #normaalgezien zou has_monthly_data en get_monthly_data alles in gang moeten zetten om alle parameters in te vullen
            #als er iets zou ontbreken, eventueel hierboven nog de juiste test.? bijvoegen als mogelijk
            df_births, tournament_marker, target_marker = test.get_monthly_data()
            # tournament_marker en target_marker geven de index positie van beiden terug in de df_births
            # zie country +/- lijn 56 - 67
            if target_marker is None:
                continue #normaal is deze nooit None als er monthly_data is, maar ja..

            target_average = df_births["births"][int(target_marker) - 1: int(target_marker) + 1].mean()

            if math.isnan(target_average):
                #kan voorkomen als target net de eerste of laatste in de lijst zou zijn, heel onwaarschijnlijk
                continue

            df_average = df_births["births"].mean()
            #aantal maanden voor en na target in df_births worden bepaald in country.get_monthly_data lijn 36-37
            #Ik had er nog aan gedacht om dit dynamisch te maken, om ook in shiny te kunnen kiezen, misschien als er nog tijd over is.
            percentage = ((target_average / df_average) -1) * 100
            query_write = "query om date naar de db terug te schrijven, index zou kunnen gebruikt worden"
            parameters = "parameters hier meegeven ipv mee in de query te steken"
            Database.write_value(query_write, parameters)
        else: continue

#momenteel niets voorzien om naar de database te schrijven indien er geen gegevens zijn
if __name__ == "__main__":
    try:
        calculate_averages("European Championship")
    except ValueError as e:
        print(e)
    try:
        calculate_averages("World Championship")
    except ValueError as e:
        print(e)
