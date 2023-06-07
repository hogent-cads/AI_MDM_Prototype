import src.backend.RuleFinding.VR.ValueRuleRepo as vrr


def test_empty_value_rule_repo():
    vr_repo = vrr.ValueRuleRepo({}) # Create with empty dict
    assert len(vr_repo.filter_column_rule_strings(
        min_support=0.0, confidence=0.0
    )) == 0
