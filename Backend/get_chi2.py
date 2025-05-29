import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from Backend.database_methods import Database

def get_chi2(compare_method, lowest_round):
    # function returns the chi² value and probability
    # can also return a df with usefully data to display in frontend
    if compare_method not in ["full year", "same months"]:
        raise ValueError("compare_method must be either 'full year' or 'same months'")

    supported_rounds = ["Final_P1", "Final_P2", "Semi_final", "Quarter_final", "Round_of_16", "Group_phase"]

    if lowest_round not in supported_rounds: raise ValueError("round is not supported")

    column_name = "percentage_monthly" if compare_method == "full year" else "percentage_yearly"
    query = (f"select country, year, round_descr, {column_name} from soccerbirth_dataproducts.birth_stats_percentage "
             f"where {column_name} != 'NaN'")
    df = Database.get_df(query)

    df["BirthDeviation"] = df[column_name].apply(lambda x: "more births" if x > 0 else "less births")
    #voor het gemak, geen rekening gehouden met == 0 (heel onwaarschijnlijk dat dit zou voorkomen)

    round_index = supported_rounds.index(lowest_round) + 1
    rounds = supported_rounds[:round_index]
    round_text = f"did reach {lowest_round}?"
    df[round_text] = df["round_descr"].apply(lambda x: "yes" if x in rounds else "no")

    df_graph = round(pd.crosstab(index=df[round_text], columns=df["BirthDeviation"], normalize="index") * 100, 1)
    df_graph.reset_index(inplace=True)

    df_chi2 = pd.crosstab(index=df[round_text], columns=df["BirthDeviation"])
    chi2, probability, _, _ = chi2_contingency(df_chi2)

    observed = np.array([df_chi2["less births"], df_chi2["more births"]])
    chi2, probability, _, _ = chi2_contingency(observed)
    significant = True if probability < 0.05 else False

    counts = df[round_text].value_counts()
    countries_yes = counts.get("yes", 0)
    countries_no = counts.get("no", 0)

    return chi2, probability, significant, df_graph, countries_yes, countries_no


if __name__ == '__main__':
    try:
        print (get_chi2("full year", "Final_P1"))
        print (get_chi2("same months", "Final_P1"))
    except ValueError as e:
        print (e)
