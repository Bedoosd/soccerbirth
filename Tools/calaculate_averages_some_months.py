import math

from Backend.country import Country
from Backend.tournament import Tournament
from Backend.database_methods import Database

def calculate_averages_same_months(tournament_to_analyse):
    if tournament_to_analyse == "European Championship":
        query = "select year, winner as country from soccerbirth_staging.euro_high_level"
    elif tournament_to_analyse == "World Championship":
        query = "select year, champion as country from soccerbirth_staging.world_cup_high_level"
    else: raise ValueError("Invalid tournament name")

    df = Database.get_df(query)

    for index, row in df.iterrows():
        country_to_analyse = row["country"]
        year_to_analyse = row["year"]
        tournament_ini = Tournament(tournament_to_analyse, year_to_analyse)
        test = Country(country_to_analyse, tournament_ini)
        print (test.has_monthly_data())
        if test.has_monthly_data():
            df, df_births1, df_births2, target_marker, target_marker1, target_marker2 = test.get_data_same_months()
            if target_marker is None or target_marker1 is None or target_marker2 is None:
                print (f"target_marker1: {target_marker1}, target_marker2: {target_marker2}, target_marker: {target_marker}")
                continue

            target_average = ((df_births1["births"][int(target_marker1) - 1: int(target_marker1) + 1].mean()) +
                              (df_births2["births"][int(target_marker2) - 1: int(target_marker2) + 1].mean())) /2

            if math.isnan(target_average):
                continue
            df_average = df["births"].mean()
            percentage = ((target_average / df_average) -1) * 100
            print (country_to_analyse, year_to_analyse, percentage)
            # query_write = "query om date naar de db terug te schrijven, index zou kunnen gebruikt worden"
            # parameters = "parameters hier meegeven ipv mee in de query te steken"
            # Database.write_value(query_write, parameters)

        else: continue

if __name__ == "__main__":
    try:
        calculate_averages_same_months("European Championship")
    except ValueError as e:
        print(e)
    try:
        calculate_averages_same_months("World Championship")
    except ValueError as e:
        print(e)
