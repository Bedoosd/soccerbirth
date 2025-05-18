# merge multiple csv files to 1 csv file
from pathlib import Path
import pandas as pd

def merge_csv_files(input_dir, output_file):
    if not Path(input_dir).is_dir():
        raise NotADirectoryError(f"input_directory does not exist: {input_dir}")
    if not Path(output_file.parent).is_dir():
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

    if valid_csv:
        pd.concat(valid_csv, ignore_index=True).to_csv(output_path, index=False)
        print(f"merged csv saved in: {output_path}")
    else:
        print("No valid CSV files to merge.")

if __name__ == "__main__":
    csv_files_map = Path.cwd().parent / "data" / "Euro" / "All_matches"
    output_path = csv_files_map.parent / "merged_euro_matches.csv"

    try:
        merge_csv_files(csv_files_map, output_path)
    except NotADirectoryError as e:
        print(e)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Unexpected error : {e}")

