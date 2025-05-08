#This code converts txt files from different countries containing birth rates per year to a usable csv file
#This data has goes further back in history then the data per month

from pathlib import Path
import os

def convert_births_txt_to_csv(input_dir, output_file):
    all_data = []
    txt_files = list(Path(input_dir).glob("*.txt"))

    if txt_files:
        for txt_file in txt_files:
            with open(txt_file, "r") as f:
                country_line = f.readline().split(",")
                f.readline()  # empty line
                f.readline()  # header line
                country = country_line[0]

                all_data.extend(f"{country},{','.join(line.split())}" for line in f if line.strip()) #append doesnt work in a oneliner
    else:
        print(f"No txt files found in {input_dir}")
        return

    with open(output_file, "w") as f:
        f.write("country,year,female,male,total\n")
        for row in all_data:
            f.write(row + "\n")

if __name__ == "__main__":
    cwd = os.getcwd()
    births_txt_path = Path(cwd).parent / "Data" / "births" / "Births_per_year"
    output_csv = Path(cwd).parent / "data" / "births" / "births_per_year.csv"
    convert_births_txt_to_csv(births_txt_path, output_csv)
