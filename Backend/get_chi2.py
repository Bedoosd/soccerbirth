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

    df_chi2 = df.copy()
    df_chi2 = pd.crosstab(index=df_chi2[round_text], columns=df_chi2["BirthDeviation"])
    df_chi2.reset_index(inplace=True)

    observed = np.array([df_chi2["less births"], df_chi2["more births"]])
    chi2, probability, _, _ = chi2_contingency(observed)
    significant = True if probability < 0.05 else False
    return chi2, probability, significant, df_graph


if __name__ == '__main__':
    try:
        print (get_chi2("full year", "Final_P2"))
        get_chi2("same months", "Final_P2")
    except ValueError as e:
        print (e)
