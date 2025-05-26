import math


from Backend.country import Country
from Backend.tournament import Tournament
from Backend.database_methods import Database


#de queries in country en tournament zijn nu wel nog afgestemd op de oude staging tabellen, met de nieuwe staging zal er niets werken.
#deze zullen eerst moeten aangepast worden naar de nieuwe tabellen om volgende functie te laten werken
#even getest met de data uit de staging en het werkt met een print :)
#resultaten zijn verassend voor de winnaars in dit geval maar ze kloppen wel

def calculate_averages(tournament_to_analyse):
    if tournament_to_analyse == "European Championship":
        query = "select year, winner as country from soccerbirth_staging.euro_high_level"
    elif tournament_to_analyse == "World Championship":
        query = "select year, champion as country from soccerbirth_staging.world_cup_high_level"
    else: raise ValueError("Invalid tournament name")

    df = Database.get_df(query)
    results = []
    for index, row in df.iterrows():
        #niet zeker of hier nog iets als 'if row' of dergelijke nodig gaat zijn voor lege lijnen
        country_to_analyse = row["country"]
        year_to_analyse = row["year"]
        tournament_ini = Tournament(tournament_to_analyse, year_to_analyse)
        test = Country(country_to_analyse, tournament_ini)

        if test.has_monthly_data():
            df_births, tournament_marker, target_marker = test.get_monthly_data(months_margin=12)
            # tournament_marker en target_marker geven de index positie van beiden terug in de df_births
            # zie country +/- lijn 56 - 67
            if target_marker is None:
                results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": None})
                continue #normaal is deze nooit None als er monthly_data is, maar ja..

            target_average = df_births["births"][int(target_marker) - 1: int(target_marker) + 1].mean()

            if math.isnan(target_average):
                results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": None})
                #kan voorkomen als target net de eerste of laatste in de lijst zou zijn, heel onwaarschijnlijk
                continue

            df_average = df_births["births"].mean()
            percentage = ((target_average / df_average) -1) * 100
            results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": percentage})

        else:
            results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": None})
            continue

    # voorbeeld van query:
    query_w = """ UPDATE birth_stats SET percentage_full_year = %s
                    WHERE country = %s AND year = %s
                """
    data = [(row["percentage"], row["country"], row["year"]) for row in results]
    Database.write_many(query_w, data)

if __name__ == "__main__":
    try:
        calculate_averages("European Championship")
    except ValueError as e:
        print(e)
    try:
        calculate_averages("World Championship")
    except ValueError as e:
        print(e)

#ter info: resultaat van de code, oude tabel veel dubbels:

# France 1984 -5.756919079445466
# Denmark 1992 -1.364874467077204
# Germany 1996 -3.2265439603824775
# France 2000 -5.443524704798186
# Spain 2008 -5.307752094589146
# Spain 2012 -7.912774737132889
# Portugal 2016 -2.670396302795486
# Italy 2020 -13.743751038064623
# France 1984 -5.756919079445466
# Denmark 1992 -1.364874467077204
# Germany 1996 -3.2265439603824775
# France 2000 -5.443524704798186
# Spain 2008 -5.307752094589146
# Spain 2012 -7.912774737132889
# Portugal 2016 -2.670396302795486
# Italy 2020 -13.743751038064623
# France 1984 -5.756919079445466
# Denmark 1992 -1.364874467077204
# Germany 1996 -3.2265439603824775
# France 2000 -5.443524704798186
# Spain 2008 -5.307752094589146
# Spain 2012 -7.912774737132889
# Portugal 2016 -2.670396302795486
# Italy 2020 -13.743751038064623
# France 1984 -5.756919079445466
# Denmark 1992 -1.364874467077204
# Germany 1996 -3.2265439603824775
# France 2000 -5.443524704798186
# Spain 2008 -5.307752094589146
# Spain 2012 -7.912774737132889
# Portugal 2016 -2.670396302795486
# Italy 2020 -13.743751038064623
# Germany 2014 -6.3353403989636075
# Spain 2010 -2.272317802088042
# Italy 2006 -8.098980703205072
# France 1998 -1.2100076058769171
# Italy 1982 -3.936594687181316
# Germany 2014 -6.3353403989636075
# Spain 2010 -2.272317802088042
# Italy 2006 -8.098980703205072
# France 1998 -1.2100076058769171
# Italy 1982 -3.936594687181316
# Germany 2014 -6.3353403989636075
# Spain 2010 -2.272317802088042
# Italy 2006 -8.098980703205072
# France 1998 -1.2100076058769171
# Italy 1982 -3.936594687181316

