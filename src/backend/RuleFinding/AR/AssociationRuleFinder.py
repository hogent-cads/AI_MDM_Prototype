import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth

import config as cfg


class AssociationRuleFinder:

    def __init__(self,
                 df_dummy: pd.DataFrame,
                 rule_length: int,
                 min_support_count: int, ):

        self.df_dummy = df_dummy
        self.rel_min_support = min_support_count / len(df_dummy)
        self.rule_length = rule_length

    def get_association_rules(self) -> pd.DataFrame:
        """
            df_dummy   : DataFrame consisting of one-hot-encoded-columns
            min_support: minimum_support for rule to be included
            max_len    : maximum length of item sets found by FP-growth

            returns: pandas DataFrame with columns "antecedents" and "consequents" that
            store itemsets, plus the scoring metric columns: "antecedent support",
            "consequent support", "support", "confidence", "lift", "leverage",
            "conviction" of all rules for which
            lift(rule) >= min_lift and  confidence(rule) >= min_confidence.
        """
        cfg.logger.debug("Shape of df in get_association_rules: %s", self.df_dummy.shape)
        frequent_itemsets = fpgrowth(self.df_dummy, min_support=self.rel_min_support,
                                     use_colnames=True, max_len=self.rule_length)
        cfg.logger.debug("Shape of frequent_itemsets: %s", frequent_itemsets.shape)
        cfg.logger.debug("%s", frequent_itemsets)

        # Oude code met lift.
        # ar = association_rules(frequent_itemsets, metric = 'lift', min_threshold=min_lift)
        # Filter out low confidence rules
        # return ar[ar['confidence'] > min_confidence]

        # Remove association rules with multiple consequents.
        # First use confidence, later filter on lift.
        # Reason to use confidence is that when a => b, c is present then also
        # a => b and a => c will be present
        ar = AssociationRuleFinder.association_rules(
            frequent_itemsets,
            'support',
            self.rel_min_support, support_only=False)

        # Only keep association rule with a confidence > 50%.
        # There can only be one such rule for each antecedent.
        # Plus, it also makes sense from the perspective of error correction.
        return ar[ar['confidence'] > 0.50]

    # Code originally from mlxtend
    @staticmethod
    def association_rules(df,
                          metric="confidence",
                          min_threshold=0.8,
                          support_only=False) -> pd.DataFrame:
        """Generates a DataFrame of association rules including the
        metrics 'score', 'confidence', and 'lift'

        Parameters
        -----------
        df : pandas DataFrame
        pandas DataFrame of frequent itemsets
        with columns ['support', 'itemsets']

        metric : string (default: 'confidence')
        Metric to evaluate if a rule is of interest.
        **Automatically set to 'support' if `support_only=True`.**
        Otherwise, supported metrics are 'support', 'confidence', 'lift',
        'leverage', and 'conviction'
        These metrics are computed as follows:

        - support(A->C) = support(A+C) [aka 'support'], range: [0, 1]\n
        - confidence(A->C) = support(A+C) / support(A), range: [0, 1]\n
        - lift(A->C) = confidence(A->C) / support(C), range: [0, inf]\n
        - leverage(A->C) = support(A->C) - support(A)*support(C),
            range: [-1, 1]\n
        - conviction = [1 - support(C)] / [1 - confidence(A->C)],
            range: [0, inf]\n

        min_threshold : float (default: 0.8)
        Minimal threshold for the evaluation metric,
        via the `metric` parameter,
        to decide whether a candidate rule is of interest.

        support_only : bool (default: False)
        Only computes the rule support and fills the other
        metric columns with NaNs. This is useful if:

        a) the input DataFrame is incomplete, e.g., does
        not contain support values for all rule antecedents
        and consequents

        b) you simply want to speed up the computation because
        you don't need the other metrics.

        Returns
        ----------
        pandas DataFrame with columns "antecedents" and "consequents"
        that store itemsets, plus the scoring metric columns:
        "antecedent support", "consequent support",
        "support", "confidence", "lift",
        "leverage", "conviction"
        of all rules for which
        metric(rule) >= min_threshold.
        Each entry in the "antecedents" and "consequents" columns are
        of type `frozenset`, which is a Python built-in type that
        behaves similarly to sets except that it is immutable
        (For more info, see
        https://docs.python.org/3.6/library/stdtypes.html#frozenset).

        Examples
        -----------
        For usage examples, please see
        http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/

        """

        columns_ordered = [
            "antecedent support",
            "consequent support",
            "support",
            "confidence",
        ]

        if not df.shape[0]:
            cfg.logger.debug(
                "The input DataFrame `df` containing the frequent itemsets is empty.")
            return pd.DataFrame(columns=["antecedents", "consequents"] + columns_ordered)

        # check for mandatory columns
        if not all(col in df.columns for col in ["support", "itemsets"]):
            raise ValueError(
                "Dataframe needs to contain the\
                            columns 'support' and 'itemsets'"
            )

        # metrics for association rules
        metric_dict = {
            "antecedent support": lambda _, s_a, __: s_a,
            "consequent support": lambda _, __, s_c: s_c,
            "support": lambda s_ac, _, __: s_ac,
            "confidence": lambda s_ac, s_a, _: s_ac / s_a,
        }

        # check for metric compliance
        if support_only:
            metric = "support"
        else:
            if metric not in metric_dict:
                raise ValueError(
                    f"Metric must be 'confidence' or 'lift', got '{metric}'"
                )

        # get dict of {frequent itemset} -> support
        keys = df["itemsets"].values
        values = df["support"].values
        frozenset_vect = np.vectorize(frozenset)
        frequent_items_dict = dict(zip(frozenset_vect(keys), values))

        # prepare buckets to collect frequent rules
        rule_antecedents = []
        rule_consequents = []
        rule_supports = []

        # iterate over all frequent itemsets
        for k, s_ac in frequent_items_dict.items():
            for con in k:
                consequent = frozenset([con])
                antecedent = k.difference(consequent)

                if support_only:
                    # support doesn't need these,
                    # hence, placeholders should suffice
                    s_a = None
                    s_c = None

                else:
                    try:
                        # support of empty antecedent is 1.0
                        s_a = 1.0 if len(antecedent) == 0 \
                                 else frequent_items_dict[antecedent]
                        s_c = frequent_items_dict[consequent]
                    except KeyError as key_error:
                        error_message = (
                            str(key_error) + "You are likely getting this error"
                            " because the DataFrame is missing "
                            " antecedent and/or consequent "
                            " information."
                            " You can try using the "
                            " `support_only=True` option"
                        )
                        raise KeyError(error_message) from key_error

                # check for the threshold
                score = metric_dict[metric](s_ac, s_a, s_c)
                if score >= min_threshold:
                    rule_antecedents.append(antecedent)
                    rule_consequents.append(consequent)
                    rule_supports.append([s_ac, s_a, s_c])

        # check if frequent rule was generated
        if not rule_supports:
            return pd.DataFrame(columns=["antecedents", "consequents"] + columns_ordered)

        # generate metrics
        rule_supports = np.array(rule_supports).T.astype(float)
        df_res = pd.DataFrame(
            data=list(zip(rule_antecedents, rule_consequents)),
            columns=["antecedents", "consequents"],
        )

        if support_only:
            s_ac = rule_supports[0]
            for met in columns_ordered:
                df_res[met] = np.nan
            df_res["support"] = s_ac

        else:
            s_ac = rule_supports[0]
            s_a = rule_supports[1]
            s_c = rule_supports[2]
            for met in columns_ordered:
                df_res[met] = metric_dict[met](s_ac, s_a, s_c)

        return df_res


