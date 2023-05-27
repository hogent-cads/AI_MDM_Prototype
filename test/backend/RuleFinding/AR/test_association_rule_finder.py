import pandas as pd
import src.backend.RuleFinding.AR.AssociationRuleFinder as arf


def test_get_association_rules_empty_antecedent():
    # Test that a rule with an empty antecedent is returned.
    df = pd.DataFrame({'A': ['1'] * 9 + ['2']})
    df_one_hot = pd.get_dummies(df)
    ar_finder = arf.AssociationRuleFinder(
        df_dummy=df_one_hot,
        rule_length=1,
        min_support_count=1
    )
    ar_df = ar_finder.get_association_rules()

    assert ar_df.shape[0] == 2
    assert ar_df[ar_df["consequents"] == frozenset(["A_1"])].shape[0] == 1
    assert ar_df[ar_df["consequents"] == frozenset(["A_2"])].shape[0] == 1
    assert (ar_df[ar_df["consequents"] == frozenset(["A_1"])]
            ["antecedents"].values[0] == frozenset())
    assert (ar_df[ar_df["consequents"] == frozenset(["A_2"])]
            ["antecedents"].values[0] == frozenset())
    assert (ar_df[ar_df["consequents"] == frozenset(["A_1"])]
            ["antecedent support"].values[0] == 1.0)
    assert (ar_df[ar_df["consequents"] == frozenset(["A_2"])]
            ["antecedent support"].values[0] == 1.0)
    assert (ar_df[ar_df["consequents"] == frozenset(["A_1"])]
            ["confidence"].values[0] == 0.9)
    assert (ar_df[ar_df["consequents"] == frozenset(["A_2"])]
            ["confidence"].values[0] == 0.1)


def test_get_association_rules():
    # Test association rules without filtering on values.
    df = pd.DataFrame({
        'A': ['1'] * 9 + ['2'],
        'B': ['1'] * 9 + ['2']})
    df_one_hot = pd.get_dummies(df)
    ar_finder = arf.AssociationRuleFinder(
        df_dummy=df_one_hot,
        rule_length=2,
        min_support_count=1
    )
    ar_df = ar_finder.get_association_rules()

    # Rules are:
    # => A_1
    # => A_2
    # => B_1
    # => B_2
    # A_1 => B_1
    # A_2 => B_2
    # B_1 => A_1
    # B_2 => A_2
    assert ar_df.shape[0] == 8
    assert ar_df[ar_df["antecedents"] == frozenset([])].shape[0] == 4
    assert ar_df[ar_df["antecedents"] == frozenset(["A_1"])].shape[0] == 1
    assert ar_df[ar_df["antecedents"] == frozenset(["A_2"])].shape[0] == 1
    assert ar_df[ar_df["antecedents"] == frozenset(["B_1"])].shape[0] == 1
    assert ar_df[ar_df["antecedents"] == frozenset(["B_2"])].shape[0] == 1


def test_association_rules_empty_df():
    # Test the method `association_rules` with an empty dataframe.
    df = pd.DataFrame({
        'support': [],
        'itemsets': []})
    result_df = arf.AssociationRuleFinder.association_rules(df)
    assert result_df.shape[0] == 0
