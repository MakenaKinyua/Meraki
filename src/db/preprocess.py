import pandas as pd
from pathlib import Path
from src.btc.config import RAW_DIR, PROCESSED_DIR
from src.db.normalise import normalise_name

#paths
def load_raw():
    df = pd.read_csv(RAW_DIR / "ingredients.csv")
    df.columns = df.columns.str.strip()
    return df

def clean_ingredients(df,name: str = "ingredient", description: str = "description"):

    initial_count=len(df)

    #check for null
    null_count = df[[name,description]].isnull().sum()
    print(f"Null values:{name}: {null_count[name]}, {description}: {null_count[description]} \n")
    
    #check for empty strings
    empty_name  = (df[name].str.strip() == "").sum()
    empty_desc  = (df[description].str.strip() == "").sum()
    print(f"Empty strings found:{name}:{empty_name},{description}:{empty_desc}\n")

    #drop nulls and empty str
    df = df.dropna(subset=[name, description]).copy()
    df = df[df[name].str.strip() != ""]
    df = df[df[description].str.strip() != ""]

    after_null_drop = len(df)
    print(f"Rows dropped nulls and empty:{initial_count - after_null_drop}\n")

    #normalise
    df["normalised_name"] = df[name].map(normalise_name)

    #drop rows that became empty after normalising
    df = df[df["normalised_name"] != ""]
    after_normalise = len(df)
    print(f"Rows dropped after normalising: {after_null_drop - after_normalise}\n")

    #check for duplicates
    check_col = "normalised_name" if "normalised_name" in df.columns else name
    duplicate = df.duplicated(subset=[check_col], keep=False)
    duplicate_count = duplicate.sum()
    print(f"Duplicate rows with the same {check_col}:{duplicate_count}\n")

    if duplicate_count > 0:
        print(f"Sample duplicates:")
        sample_dupes = (
            df[duplicate]
            .sort_values(check_col)
            .tail(10)[[check_col, description]]
        )
        print(sample_dupes.to_string(index=False))

    #keep longest description
    df["_desc_length"] = df[description].str.len()
    df = (
        df.sort_values("_desc_length", ascending=False)
          .drop_duplicates(subset=[check_col], keep="first")
          .drop(columns=["_desc_length"])
    )

    after_dedup = len(df)
    print(f"Rows dropped:{after_null_drop - after_dedup}")
    print(f"Final rows:   {after_dedup}")
    print(f"Total dropped: {initial_count - after_dedup}")

    return df.reset_index(drop=True)

if __name__ == "__main__":
    df = clean_ingredients(load_raw())
    df.to_csv(PROCESSED_DIR / "ingredients_clean.csv", index=False)