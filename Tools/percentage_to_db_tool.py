import math
import pandas as pd

from Backend.country import Country
from Backend.tournament import Tournament
from Backend.database_methods import Database

def calculate_averages_same_months(tournament, df, results):
    #compare the birth numbers from the target (+/-1month) with the previous and next year
    for index, row in df.iterrows():
        print (f"progress at {tournament}, yearly: {index}/{df.shape[0]}") if index % 25 == 0 else None
        country_to_analyse = row["country_name"]
        year_to_analyse = row["year"]
        tournament_ini = Tournament(tournament, year_to_analyse)
        test = Country(country_to_analyse, tournament_ini)

        key = (country_to_analyse, year_to_analyse)
        if key not in results:
            results[key] = {"country": country_to_analyse, "year": year_to_analyse}

        if test.has_monthly_data():
            df_target, df_minus1, df_plus1 = test.get_data_same_months()

            if len(df_minus1) < 3 or len(df_plus1) < 3 or len(df_target) < 3:
                results[key]["percentage_yearly"] = None
                continue
            target_average = (df_minus1["births"].mean() + df_plus1["births"].mean()) / 2
            df_average = df_target["births"].mean()
            percentage = round(((target_average / df_average) -1) * 100,2)
            results[key]["percentage_yearly"] = percentage

        else:
            results[key]["percentage_yearly"] = None
            continue
    return results

def calculate_averages(tournament, df, results):
    #compares the average of the target (+/-1month) to a set amount of months before/after the target (months_margin)
    for index, row in df.iterrows():
        print (f"progress at {tournament}, monthly: {index}/{df.shape[0]}") if index % 25 == 0 else None
        country_to_analyse = row["country_name"]
        year_to_analyse = row["year"]
        tournament_ini = Tournament(tournament, year_to_analyse)
        test = Country(country_to_analyse, tournament_ini)

        key = (country_to_analyse, year_to_analyse)
        if key not in results:
            results[key] = {"country": country_to_analyse,"year": year_to_analyse}

        if test.has_monthly_data():
            df_births, tournament_marker, target_marker = test.get_monthly_data(months_margin=12)
            if target_marker is None:
                results[key]["percentage_monthly"] = None
                continue

            target_average = df_births["births"][int(target_marker) - 1: int(target_marker) + 1].mean()

            if math.isnan(target_average):
                results[key]["percentage_monthly"] = None
                continue

            df_average = df_births["births"].mean()
            percentage = round(((target_average / df_average) - 1) * 100, 2)
            results[key]["percentage_monthly"] = percentage
        else:
            results[key]["percentage_monthly"] = None
            continue
    return results


def percentage_to_db_tool():
    #makes a single dataframe from both tournaments and both methods
    tournaments = ["European Championship", "World Championship"]
    results = {}
    for tournament in tournaments:
        query = (f"select year, country_name from soccerbirth_dataproducts.dp_stats_round where tournament = %s")
        parameters = (tournament,)
        df = Database.get_df(query, parameters)
        results = calculate_averages_same_months(tournament, df, results)
        results = calculate_averages(tournament, df, results)

    df = pd.DataFrame(results.values())

    #year = 2024
    #country = 'England'
    #percentage_monthly = 12.5
    #percentage_yearly = 805.0
    query_write = """MERGE INTO soccerbirth_dataproducts.birth_stats_percentage AS target
                    USING (VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)) AS source (year, country, Percentage_monthly, Percentage_yearly, insert_date)
                    ON target.year = source.year AND target.country = source.country
                    WHEN MATCHED THEN
                        UPDATE SET 
                            Percentage_monthly = source.Percentage_monthly,
                            Percentage_yearly = source.Percentage_yearly,
                            insert_date = source.insert_date
                    WHEN NOT MATCHED THEN
                        INSERT (year, country, Percentage_monthly, Percentage_yearly, insert_date)
                        VALUES (source.year, source.country, source.Percentage_monthly, source.Percentage_yearly, source.insert_date)"""

    #chat gpt stelde volgende voor om waardes mee te geven
    #geeft een waarschuwing omdat de dict waarden nog niet gekend zijn denk ik
    data = [(row.year, row.country, row.percentage_monthly, row.percentage_yearly)
            for row in df.itertuples(index=False)]
    #data = [[year, country, percentage_monthly, percentage_yearly]]

    Database.write_many(query_write, data)

    #df.to_csv("complete_percentages.csv", index=False)
    #deze maakt meteen csc file, staat al in data/percentages

if __name__ == "__main__":
    try:
        percentage_to_db_tool()
    except Exception as e:
        print(e)
