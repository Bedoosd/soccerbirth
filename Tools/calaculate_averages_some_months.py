
from Backend.country import Country
from Backend.tournament import Tournament
from Backend.database_methods import Database

def calculate_averages_same_months(tournament_to_analyse):
    #compare the birth numbers from the target (+/-1month) with the previous and next year
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
        if test.has_monthly_data():
            df_target, df_minus1, df_plus1 = test.get_data_same_months()
            target_average = (df_minus1["births"].mean() + df_plus1["births"].mean())/2

            if len(df_minus1) < 3 or len(df_plus1) < 3 or len(df_target) < 3:
                #if there is no monthly data available for the previous or next year, target should be oke
                print(f"Not enough data available for {country_to_analyse} {year_to_analyse}, one of the dataframes contains less then 3 values.\n "
                      f"target: {len(df_target)}months, target plus 1 year: {len(df_minus1)}months, target minus 1 year: {len(df_plus1)}months\n ")
                continue

            df_average = df_target["births"].mean()
            percentage = ((target_average / df_average) -1) * 100
            print (f"{country_to_analyse}, {year_to_analyse}: {percentage} %")
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
