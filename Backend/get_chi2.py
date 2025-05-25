import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from Backend.database_methods import Database
def get_chi2(compare_method, highest_round):
    if compare_method not in ["full year", "same_months"]:
        raise ValueError("compare_method must be either full year or same_months")

    supported_rounds = ["winner", "runner_up", "semi_final", "quarter_final", "round_of_16"]
    #check names with final database
    if highest_round not in supported_rounds: raise ValueError("round is not supported")
    #function returns the chi² value and probability
    #can also return a df with usefully data to display in frontend

    column_name = ("name_column_full_year_percentage" if compare_method == "full year"
                   else "name_column_month_percentage") #to adjust to the right names

    query = """select country, year, high_round, %s from soccerbirth_dwh.fact_euro_stats where %s is not Null
                union
                select country, year, high_round, %s from soccerbirth_dwh.fact_world_cup_stats where %s is not Null"""

    parameters = [column_name] * 4

    df = Database.get_df(query, parameters)
    df["BirthDeviation"] = df[column_name].apply(lambda x: "more births" if x > 0 else "less births")
    #voor het gemak, geen rekening gehouden met == 0 (heel onwaarschijnlijk dat dit zou voorkomen)

    round_index = supported_rounds.index(highest_round)
    rounds = supported_rounds[round_index:]
    round_text = f"did reach {highest_round}?"
    df[round_text] = df["high_round"].apply(lambda x: "yes" if x in rounds else "no")

    df_graph = round(pd.crosstab(index=df[round_text], columns=df["BirthDeviation"], normalize="columns") * 100, 1)
    df_graph.reset_index(inplace=True)

    df_chi2 = df.copy()
    df_chi2 = pd.crosstab(index=df_chi2[round_text], columns=df_chi2["BirthDeviation"])
    df_chi2.reset_index(inplace=True)

    observed = np.array([df_chi2["less births"], df_chi2["more births"]])
    #aangezien ik nog niet kan testen, keurt gpt de code wel goed maar past observed aan naar volgende:
    #observed = df_chi2[["less births", "more births"]].values
    chi2, probability, _, _ = chi2_contingency(observed)
    significant = True if probability < 0.05 else False

    return chi2, probability, significant, df_graph


if __name__ == '__main__':
    try:
        get_chi2("full year", "winner")
        get_chi2("same_months", "runner_up")
    except ValueError as e:
        print (e)
