import math


from Backend.country import Country
from Backend.tournament import Tournament
from Backend.database_methods import Database

def calculate_averages(tournament_to_analyse):
    query = (f"select year, country_name from soccerbirth_dataproducts.dp_stats_round where tournament = %s")
    parameters = (tournament_to_analyse,)
    df = Database.get_df(query, parameters)
    results = []
    for index, row in df.iterrows():
        print (f"progress: {index}/{df.shape[0]}")

        #niet zeker of hier nog iets als 'if row' of dergelijke nodig gaat zijn voor lege lijnen
        country_to_analyse = row["country_name"]
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
            percentage = round(((target_average / df_average) - 1) * 100, 2)
            results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": percentage})

        else:
            results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": None})
            continue

    # with open (f"percentage{tournament_to_analyse}.csv", "w") as f:
    #     for line in results:
    #         f.write(f"{line['country']},{line['year']},{line['percentage']}")
    #         f.write("\n")



    print (results)
    # voorbeeld van query:
    # query_w = """ UPDATE birth_stats SET percentage_full_year = %s
    #                 WHERE country = %s AND year = %s
    #             """
    # data = [(row["percentage"], row["country"], row["year"]) for row in results]
    # Database.write_many(query_w, data)

if __name__ == "__main__":
    try:
        calculate_averages('European Championship')
    except ValueError as e:
        print(e)
    try:
        calculate_averages('World Championship')
    except ValueError as e:
        print(e)
