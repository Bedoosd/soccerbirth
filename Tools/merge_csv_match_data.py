# merge multiple csv files to 1 csv file
from pathlib import Path

csv_files_map = Path.cwd().parent / "data" / "Euro" / "All_matches"
output_path = csv_files_map / "output" / "merged_ek.csv"
#If output directory doesn't exist --> create
output_path.parent.mkdir(exist_ok=True)

columns_needed = [
    "id_match", "home_team", "away_team", "home_score", "away_score",
    "year", "date", "round", "match_attendance"
]

print(columns_needed)
