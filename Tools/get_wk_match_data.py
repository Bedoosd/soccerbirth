import pandas as pd

df = pd.read_csv("../Data/World/WK_matches.csv")

cols = ['home_team', 'away_team', 'home_score', 'away_score', 'home_penalty', 'away_penalty', 'Attendance', 'Round', 'Date', 'Host', 'Year']
df_filtered = df[cols].copy()