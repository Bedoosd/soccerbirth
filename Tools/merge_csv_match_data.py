# merge multiple csv files to 1 csv file
from pathlib import Path
import pandas as pd

csv_files_map = Path.cwd().parent / "data" / "Euro" / "All_matches"
output_path = csv_files_map / "output" / "merged_ek.csv"
#If output directory doesn't exist --> create
output_path.parent.mkdir(exist_ok=True)

columns_needed = [
    "id_match", "home_team", "away_team", "home_score", "away_score",
    "year", "date", "round", "match_attendance"
]

valid_csv = []

for f in csv_files_map.glob("*.csv"):
    if f.stem.isdigit() and len(f.stem) == 4:
        try:
            valid_csv.append(pd.read_csv(f, usecols=columns_needed))
        except ValueError as e:
            print(f"file skipped (wrong columns): {f.name} – {e}")
    else:
        print(f"file skipped (invalid filename): {f.name} – not a 4-digit year")

print(columns_needed)
