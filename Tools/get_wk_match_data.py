# get all the wanted match data from original file
import pandas as pd
from pathlib import Path

def process_wk_matches(input_file: Path, output_file: Path):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Fout: Bestand niet gevonden – {input_file}")
        return
    except Exception as e:
        print(f"Fout bij inlezen CSV: {e}")
        return

    required_columns = [
        'home_team', 'away_team', 'home_score', 'away_score',
        'home_penalty', 'away_penalty', 'Attendance', 'Round',
        'Date', 'Host', 'Year'
    ]

    df_filtered = df[required_columns].copy()

    def winner(row):
        if row.home_score != row.away_score:
            return row.home_team if row.home_score > row.away_score else row.away_team
        if pd.notna(row.home_penalty) and pd.notna(row.away_penalty):
            if row.home_penalty != row.away_penalty:
                return row.home_team if row.home_penalty > row.away_penalty else row.away_team
        return 'Draw'


    df_filtered['Winner'] = df_filtered.apply(winner, axis=1)

    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df_filtered.to_csv(output_file, index=False)
        print(f"CSV opgeslagen in: {output_file}")
    except Exception as e:
        print(f"Fout bij opslaan: {e}")


if __name__ == "__main__":
    input_path = Path.cwd().parent / "data" / "World" / "WK_matches.csv"
    output_path = input_path.parent / "wk_match_data.csv"

    try:
        process_wk_matches(input_path, output_path)
    except NotADirectoryError as e:
        print(e)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Unexpected error : {e}")
