import pandas as pd
import src.backend.DomainController as dc
import src.shared.Configs.RuleFindingConfig as rfc
import src.shared.Enums.FiltererEnum as fe


# Check that get_all_column_rules_from_df_and_config returns a
# valid response.
# We only check that the response is not None and that it is a string.
def test_get_all_column_rules_from_df_and_config_1():
    rule_finding_config = rfc.RuleFindingConfig(
        rule_length=2,
        min_support=10**-9,  # essentially zero
        lift=1.0,
        confidence=0.95,
        filtering_string=fe.FiltererEnum.C_METRIC.value,
        binning_option={},
        dropping_options={}
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


if __name__ == "__main__":
    test_get_all_column_rules_from_df_and_config_1()
