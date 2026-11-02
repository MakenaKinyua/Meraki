import pandas as pd
from src.db.preprocess import clean_ingredients

def make_df(rows):
    return pd.DataFrame(rows, columns=["ingredient", "description"])

def test_drops_null_rows():
    df = make_df([("Glycerin", "humectant"), (None, "x"), ("Aqua", None)])
    result = clean_ingredients(df)
    assert len(result) == 1

def test_drops_empty_string_rows():
    df = make_df([("Glycerin", "humectant"), ("   ", "x"), ("Aqua", "")])
    result = clean_ingredients(df)
    assert len(result) == 1

def test_normalises_case_and_whitespace():
    df = make_df([("  Sodium   LAURYL  Sulfate ", "detergent")])
    result = clean_ingredients(df)
    assert result["normalised_name"].iloc[0] == "sodium lauryl sulfate"

def test_removes_punctuation_keeps_hyphens():
    df = make_df([("Aqua (Water)", "solvent"), ("Cetyl-Alcohol!", "emollient")])
    result = clean_ingredients(df)
    assert set(result["normalised_name"]) == {"aqua water", "cetyl-alcohol"}

def test_drops_rows_empty_after_normalising():
    df = make_df([("Glycerin", "humectant"), ("!!!", "junk")])
    result = clean_ingredients(df)
    assert len(result) == 1

def test_dedupes_on_normalised_name():
    df = make_df([("Glycerin", "a"), (" glycerin! ", "b")])
    result = clean_ingredients(df)
    assert len(result) == 1

def test_keeps_longest_description_when_deduping():
    df = make_df([("Glycerin", "short"), ("glycerin", "a much longer description")])
    result = clean_ingredients(df)
    assert result["description"].iloc[0] == "a much longer description"

def test_index_is_reset():
    df = make_df([("Glycerin", "a"), ("Aqua", "b"), ("aqua", "bb")])
    result = clean_ingredients(df)
    assert list(result.index) == list(range(len(result)))

def test_does_not_modify_input_dataframe():
    df = make_df([("Glycerin", "a"), ("glycerin", "b")])
    before = df.copy()
    clean_ingredients(df)
    pd.testing.assert_frame_equal(df, before)