import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from Backend.database_methods import Database

def get_chi2_full_tournament():
    pass
    #get a chi2 to figure out if there is an overall rise in birth numbers around the target for all tournaments
    #compared with the previous and next year
    #volgende is een voorstel van gpt omdat chi2 niet gaat om dit te bewijzen:

    # from scipy.stats import binom_test
    #
    # # Aantal landen totaal (voorbeeld)
    # n = 30
    #
    # # Aantal landen met 'meer geboortes' (66.7% van 30)
    # successes = int(round(0.667 * n))
    #
    # # Binomiale test: H0: p=0.5
    # p_value = binom_test(successes, n, p=0.5, alternative='two-sided')
    #
    # print(f"Aantal landen: {n}")
    # print(f"Meer geboortes: {successes}")
    # print(f"P-waarde binomiale test: {p_value:.4f}")
    #
    # if p_value < 0.05:
    #     print("Resultaat is statistisch significant (afwijking van 50%).")
    # else:
    #     print("Resultaat is niet statistisch significant (geen afwijking van 50%).")



def get_chi2(compare_method, lowest_round):
    # function returns the chi² value and probability
    # can also return a df with usefully data to display in frontend
    if lowest_round == "Final": lowest_round = "Final_P2" #easiest way to get shiny to display Final when selecting P1+P2
    if compare_method not in ["full year", "same months"]:
        raise ValueError("compare_method must be either 'full year' or 'same months'")

    supported_rounds = ["Final_P1", "Final_P2", "Semi_final", "Quarter_final", "Round_of_16", "Group_phase"]

    if lowest_round not in supported_rounds: raise ValueError("round is not supported")

    column_name = "percentage_monthly" if compare_method == "full year" else "percentage_yearly"
    query = (f"select country_name, year, round_descr, {column_name} from soccerbirth_dataproducts.dp_stats_round "
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
        print (get_chi2("full year", "Group_phase"))
        print (get_chi2("same months", "Group_phase"))
    except ValueError as e:
        print (e)
