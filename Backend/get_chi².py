import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from Backend.database_methods import Database
def get_chisquare(compare_method):
    if compare_method not in ["full year", "same_months"]:
        raise ValueError("compare_method must be either full year or same_months")
    #function returns the chi² value and probability
    #can also return a df with usefully data to display in frontend

    query = """select country, year, high_round, %s from soccerbirth_dwh.fact_euro_stats where %s is not Null
                union
                select country, year, high_round, %s from soccerbirth_dwh.fact_world_cup_stats where %s is not Null"""
    parameters = (["name_column_full_year_percentage"] * 4 if (compare_method == "full year")
                  else ["name_column_month_percentage"] * 4)
    df = Database.get_df(query, parameters)
    #in principe zou ik van de dataframe volgende zeker moeten krijgen:
    # Country, year, More births (yes/no) -> variabel met method,


if __name__ == '__main__':
    try:
        get_chisquare("full year")
        get_chisquare("same_months")
    except ValueError as e:
        print (e)