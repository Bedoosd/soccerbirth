import pandas as pd

df = pd.read_csv("../Data/World/WK_matches.csv")

cols = ['home_team', 'away_team', 'home_score', 'away_score', 'home_penalty', 'away_penalty', 'Attendance', 'Round', 'Date', 'Host', 'Year']
df_filtered = df[cols].copy()

def winner(row):
    if row.home_score != row.away_score:
        return row.home_team if row.home_score > row.away_score else row.away_team
    if pd.notna(row.home_penalty) and pd.notna(row.away_penalty):
        if row.home_penalty != row.away_penalty:
            return row.home_team if row.home_penalty > row.away_penalty else row.away_team
    return 'Draw'

df_filtered['Winner'] = df_filtered.apply(winner, axis=1)

df_filtered.to_csv("../Data/World/wk_match_data.csv", index=False)
