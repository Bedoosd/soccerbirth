# merge multiple csv files to 1 csv file
from pathlib import Path

csv_files_map = Path.cwd().parent / "data" / "Euro" / "All_matches"
print(csv_files_map)
