# merge multiple csv files to 1 csv file
from pathlib import Path
import pandas as pd

def merge_csv_files(input_dir, output_file):
    if not Path(input_dir).is_dir():
        raise NotADirectoryError(f"input_directory does not exist: {input_dir}")
    if not Path(output_file.parent).is_dir():
        output_path.parent.mkdir(exist_ok=True)

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

