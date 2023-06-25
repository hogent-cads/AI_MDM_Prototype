import json

import pandas as pd
import src.backend.DomainController as dc
import src.shared.configs
import src.shared.enums


# Check that get_all_column_rules_from_df_and_config returns a
# valid response.
# We only check that the response is not None and that it is a string.
def test_get_all_column_rules_from_df_and_config_1():
    rule_finding_config = src.shared.configs.RuleFindingConfig(
        cols_to_use=['a', 'b'],
        rule_length=2,
        abs_min_support=1,
        confidence=0.95,
        speed=1.0,
        quality=0,
        g3_threshold=0.75,
        fi_threshold=0.75
    )
    domain_controller = dc.DomainController()
    df = pd.DataFrame({
        'a': [_ for _ in range(0, 10)],
        'b': [0, 2, 1, 1, 1, 2, 0, 2, 0, 0]
        })

    result = domain_controller.get_all_column_rules_from_df_and_config(
        dataframe_in_json=df.to_json(),
        rule_finding_config_in_json=rule_finding_config.to_json())

    assert result is not None
    assert type(result) == str

    result_dict = json.loads(result)

    assert type(result_dict) == dict

    assert "a => b" in result_dict.keys()
    assert "b => a" not in result_dict.keys()

    assert len(result_dict.keys()) == 1

    assert type(result_dict["a => b"]) == str

    rule_info = json.loads(result_dict["a => b"])
    assert type(rule_info) == dict


def test_fuzzy_match_dataprep_1():
    """
    Test that fuzzy_match_dataprep returns a valid response.
    In this case, no clusters should be found.
    """
    df = pd.DataFrame({
        'A': ['abc', 'aec', 'abd', 'def', 'def']
    })

    domain_controller = dc.DomainController()

    result = domain_controller.fuzzy_match_dataprep(
        dataframe_in_json=df.to_json(),
        col='A',
        cluster_method='levenshtein',
        df_name="test_df",
        ngram=None,
        radius=1,
        block_size=3)

    assert result is not None
    result = json.loads(result)
    assert len(result) == 0


def test_fuzzy_match_dataprep_2():
    """
    Test that fuzzy_match_dataprep returns a valid response.
    In this case, a single cluster should be found,
    namely abc and abc.
    """
    df = pd.DataFrame({
        'A': ['abc', 'aec', 'abd', 'def', 'def']
    })

    domain_controller = dc.DomainController()

    result = domain_controller.fuzzy_match_dataprep(
        dataframe_in_json=df.to_json(),
        col='A',
        cluster_method='levenshtein',
        df_name="test_df",
        ngram=None,
        radius=1,
        block_size=2)

    assert result is not None
    result = json.loads(result)
    assert len(result) == 1

    for cluster_id, values in result.items():
        assert type(cluster_id) == str
        assert type(values) == list
        assert len(values) == 2
        assert sorted(values) == ['abc', 'abd']


def test_fuzzy_match_dataprep_3():
    """
    Test that fuzzy_match_dataprep returns a valid response.
    In this case, three clusters should be found,
    namely [abc, abd], [abc, aec], [abc, abd]
    """
    df = pd.DataFrame({
        'A': ['abc', 'aec', 'abd', 'def', 'def']
    })

    domain_controller = dc.DomainController()

    result = domain_controller.fuzzy_match_dataprep(
        dataframe_in_json=df.to_json(),
        col='A',
        cluster_method='levenshtein',
        df_name="test_df",
        ngram=None,
        radius=1,
        block_size=1)

    assert result is not None
    result = json.loads(result)
    assert len(result) == 3

    all_values = result.values()
    sorted_values = [sorted(_) for _ in all_values]
    # Check the clusters
    assert ["abc", "abd", "aec"] in sorted_values
    assert ["abc", "aec"] in sorted_values
    assert ["abc", "abd"] in sorted_values


if __name__ == "__main__":
    test_get_all_column_rules_from_df_and_config_1()
