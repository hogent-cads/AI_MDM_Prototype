import pandas as pd
import numpy as np
from backend.RuleFinding.CR.ColumnRule import ColumnRule


def test_columnrule_creation():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2",
    }

    df = pd.DataFrame(
        {'A' : ["a1", "a1", "a2"],
         'B' : ["x", "y", "z"],
         'C' : ["c", "c", "c"]
        }
    )

    cr = ColumnRule(rule_string = rule_string, value_mapping = value_mapping, original_df = df)

    df_to_be_corrected = cr.df_to_correct

    assert df_to_be_corrected.shape == (3,6)
    assert "SUGGEST_CON" in df_to_be_corrected.columns
    assert "FOUND_CON" in df_to_be_corrected.columns
    assert "RULESTRING" in df_to_be_corrected.columns

    assert df_to_be_corrected['FOUND_CON'].equals(pd.Series(["x", "y", "z"]))
    assert df_to_be_corrected['SUGGEST_CON'].equals(pd.Series(["b1", "b1", "b2"]))
    assert df_to_be_corrected['RULESTRING'].equals(pd.Series([rule_string, rule_string, rule_string]))

    # Check confidence
    assert cr.confidence == 0.0


def test_columnrule_creation_bis():
    # Test that correct rows do not appear in the dataframe to correct    
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2",
    }

    df = pd.DataFrame(
        {'A' : ["a1", "a1", "a1","a1", "a1", "a2", "a2"],
         'B' : ["b1", "b1", "b1", "x", "y", "z", "b2"],
         'C' : ["c", "c", "c","c", "c", "c", "c"]
        }
    )

    cr = ColumnRule(rule_string =rule_string, original_df = df, value_mapping=value_mapping)
    df_to_be_corrected = cr.df_to_correct

    assert df_to_be_corrected.shape == (3,6)

    assert (df_to_be_corrected['FOUND_CON'].reset_index(drop=True).
        equals(pd.Series(["x", "y", "z"])))
    assert (df_to_be_corrected['SUGGEST_CON'].reset_index(drop=True).
        equals(pd.Series(["b1", "b1", "b2"])))
    assert (df_to_be_corrected['RULESTRING'].reset_index(drop=True).
        equals(pd.Series([rule_string, rule_string, rule_string])))


def test_predict():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2",
    }

    df = pd.DataFrame(
        {'A' : ["a1", "a1", "a2"],
         'B' : ["x", "y", "z"],
         'C' : ["c", "c", "c"]
        }
    )

    cr = ColumnRule(rule_string = rule_string, value_mapping = value_mapping, original_df = df)

    predicted_values = cr.predict(df)

    assert predicted_values.shape == (df.shape[0], 2)
    assert (predicted_values['A'].reset_index(drop=True).
        equals(pd.Series(["a1", "a1", "a2"])))
    assert (predicted_values['B'].reset_index(drop=True).
        equals(pd.Series(["b1", "b1", "b2"])))

def test_status():
    rule_string = "A => B"

    value_mapping = {
        frozenset(["A_a1"]) : "B_b1",
        frozenset(["A_a2"]) : "B_b2",
    }

    df = pd.DataFrame(
        {'A' : ["a1", "a1", "a2"],
         'B' : ["x", "y", "z"],
         'C' : ["c", "c", "c"]
        }
    )

    cr = ColumnRule(rule_string = rule_string, value_mapping = value_mapping, original_df = df)

    df_for_status =  pd.DataFrame(
        {'A' : ["a1", "a1", "a2", "a2"],
         'B' : ["x", "b1", "b2", "y"],
         'C' : ["c", "c", "c", "c"]
        }
    )

    status = cr.status(df_for_status)

    assert np.array_equal(status, np.array([-1,1,1,-1]))

