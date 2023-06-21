import pandas as pd

from src.frontend.pages.rule_learning.rule_learning_suggestions import (
    _apply_suggestions, _compute_affected_columns
)

def test_apply_suggestions_1():
    df = pd.DataFrame({
        'a' : ['1'] * 10 + ['2'] * 10,
        'b' : ['1'] * 8 + ['900', '1000'] + ['2'] * 8 + ['1900', '2000']
    })

    predictions_df = pd.DataFrame(
        {
            "__BEST_RULE" : ["a => b", "a => b", "a => b", "a => b"],
            "__BEST_PREDICTION" : ["1", "1", "2", "2"]
        }
    )

    predictions_df.index = pd.Index([8,9,18,19])

    # Only apply the last suggestion
    new_df = _apply_suggestions(df, predictions_df, [3])

    # Test that the new dataframe has the same shape as the original dataframe
    assert new_df.shape == df.shape

    # Test that 2000 has been changed into a 2 and all the other values
    # are still the same
    assert (new_df['b'] == pd.Series(
        ['1'] * 8 + ['900', '1000'] + ['2'] * 8 + ['1900'] + ['2'])).all()

    # Test that the column 'a' didn't change
    assert (new_df['a'] == df['a']).all()


def test_apply_suggestions_2():
    """
    Test multiple replacements.
    """
    df = pd.DataFrame({
        'a' : ['1'] * 10 + ['2'] * 10,
        'b' : ['1'] * 8 + ['900', '1000'] + ['2'] * 8 + ['1900', '2000']
    })

    predictions_df = pd.DataFrame(
        {
            "__BEST_RULE" : ["a => b", "a => b", "a => b", "a => b"],
            "__BEST_PREDICTION" : ["1", "1", "2", "2"]
        }
    )

    predictions_df.index = pd.Index([8,9,18,19])

    # Apply the first and last suggestion
    new_df = _apply_suggestions(df, predictions_df, [0, 3])

    # Test that the new dataframe has the same shape as the original dataframe
    assert new_df.shape == df.shape

    # Test that 900 has changes to a 1,
    # 2000 has been changed into a 2 and all the other values
    # are still the same
    assert (new_df['b'] == pd.Series(
        ['1'] * 8 + ['1'] + ['1000'] + ['2'] * 8 + ['1900'] + ['2'])).all()

    # Test that the column 'a' didn't change
    assert (new_df['a'] == df['a']).all()


def test_compute_affected_columns():
    predictions_df = pd.DataFrame(
        {
            "__BEST_RULE": ["a => b", "b,c => d", "e => f", "g => h"],
            "__BEST_PREDICTION": ["1", "1", "2", "2"]
        }
    )

    predictions_df.index = pd.Index([8, 9, 18, 19])

    # Only apply the last suggestion
    affected_cols = _compute_affected_columns(
        predictions_df=predictions_df,
        indices_in_index=[2,1,0]
    )

    # Only consequent columns should be present
    assert sorted(affected_cols) == ['b', 'd', 'f']
