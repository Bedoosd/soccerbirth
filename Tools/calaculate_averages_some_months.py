import pandas as pd

from Backend.country import Country
from Backend.tournament import Tournament
from Backend.database_methods import Database

def calculate_averages_same_months(tournament_to_analyse):
    #compare the birth numbers from the target (+/-1month) with the previous and next year
    query = (f"select year, country_name from soccerbirth_dataproducts.dp_stats_round where tournament = %s")
    parameters = (tournament_to_analyse,)
    df = Database.get_df(query, parameters)
    results = []
    for index, row in df.iterrows():
        print (f"progress: {index}/{df.shape[0]}") if index % 10 == 0 else None
        country_to_analyse = row["country_name"]
        year_to_analyse = row["year"]
        tournament_ini = Tournament(tournament_to_analyse, year_to_analyse)
        test = Country(country_to_analyse, tournament_ini)
        if test.has_monthly_data():
            df_target, df_minus1, df_plus1 = test.get_data_same_months()

            if len(df_minus1) < 3 or len(df_plus1) < 3 or len(df_target) < 3:
                #if there is no monthly data available for the previous or next year, target should be oke
                # print(f"Not enough data available for {country_to_analyse} {year_to_analyse}, one of the dataframes contains less then 3 values.\n "
                #       f"target: {len(df_target)}months, target plus 1 year: {len(df_minus1)}months, target minus 1 year: {len(df_plus1)}months\n ")
                results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": None})
                continue
            target_average = (df_minus1["births"].mean() + df_plus1["births"].mean()) / 2
            df_average = df_target["births"].mean()
            percentage = round(((target_average / df_average) -1) * 100,2)
            results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": percentage})

        else:
            results.append({"country": country_to_analyse, "year": year_to_analyse, "percentage": None})
            continue
    #als test om te kijken of alles goed verwerkt wordt
    # with open (f"percentage2{tournament_to_analyse}.csv", "w") as f:
    #     for line in results:
    #         f.write(f"{line['country']},{line['year']},{line['percentage']}")
    #         f.write("\n")

    # voorbeeld van query:
    # query_w = """ UPDATE birth_stats SET percentage_monthly = %s
    #                 WHERE country = %s AND year = %s
    #             """
    # data = [(row["percentage"], row["country"], row["year"]) for row in results]
    # Database.write_many(query_w, data)

if __name__ == "__main__":
    try:
        calculate_averages_same_months("European Championship")
    except ValueError as e:
        print(e)
    try:
        calculate_averages_same_months("World Championship")
    except ValueError as e:
        print(e)
