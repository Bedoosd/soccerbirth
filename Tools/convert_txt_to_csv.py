#This code converts txt files from different countries containing birth rates per year to a usable csv file
#This data has goes further back in history then the data per month

from pathlib import Path
import os

def convert_births_txt_to_csv(input_dir, output_file):
    if not Path(input_dir).is_dir():
        raise NotADirectoryError(f"input_directory does not exist: {input_dir}")
    if not Path(output_file.parent).is_dir():
        raise NotADirectoryError(f"output_dir does not exist: {output_file.parent}")

    all_data = ["country,year,female,male,total"]
    txt_files = list(Path(input_dir).glob("*.txt"))

    if txt_files:
        for txt_file in txt_files:
            with open(txt_file, "r") as f:
                country = f.readline().split(",")[0] #country is always the first text in the first line in these files
                next(f)  # empty line
                next(f)  # header line
                all_data.extend(f"{country},{','.join(line.split())}" for line in f if line.strip()) #append doesnt work in a oneliner
    else:
        raise FileNotFoundError(f"There are no txt files in {input_dir}")

    with open(output_file, "w", encoding="utf-8", newline='') as f:
        f.write("\n".join(all_data))

if __name__ == "__main__":
    cwd = os.getcwd()
    births_txt_path = Path(cwd).parent / "data" / "births" / "births_per_year"
    output_csv = Path(cwd).parent / "data" / "births" / "births_per_year.csv"

    try:
        convert_births_txt_to_csv(births_txt_path, output_csv)
    except NotADirectoryError as e:
        print(e)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Unexpected error : {e}")
