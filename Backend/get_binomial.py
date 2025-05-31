from scipy.stats import binomtest

from Backend.database_methods import Database


def get_binomial():
    query = ("select country_name, percentage_yearly from soccerbirth_dataproducts.dp_stats_round where percentage_yearly != 'NaN'")
    df = Database.get_df(query)
    total = len(df)
    less_than_zero = len(df[df["percentage_yearly"] < 0])
    more_than_zero = len(df[df["percentage_yearly"] > 0])

    result = binomtest(
        less_than_zero,
        total,
        p=0.5,
        alternative='two-sided'
    )
    p_value = result.pvalue
    print (f"{p_value:.10f}")

    if result.pvalue < 0.05:
        return (True, p_value)
    else:
        return (False, p_value)

