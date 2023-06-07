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

if __name__ == "__main__":
    test_get_all_column_rules_from_df_and_config_1()
