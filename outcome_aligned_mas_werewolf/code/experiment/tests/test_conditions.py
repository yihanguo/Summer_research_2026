import unittest

from experiment.conditions import get_condition, primary_conditions


class ConditionTest(unittest.TestCase):
    def test_primary_conditions_are_open_and_exclude_agent_full(self):
        conditions = primary_conditions()
        self.assertEqual(
            [condition.condition_id for condition in conditions],
            ["++", "+-", "-+", "--"],
        )
        self.assertEqual(
            [condition.condition_slug for condition in conditions],
            ["pp", "pm", "mp", "mm"],
        )
        self.assertTrue(all(condition.public_broadcast for condition in conditions))
        self.assertNotIn("agent_full", {condition.evidence_mode for condition in conditions})

    def test_signs_match_intervention_flags_and_historical_aliases(self):
        expected = {"C3": "++", "C1": "+-", "C4": "-+", "C0": "--"}
        for legacy_id, signs in expected.items():
            condition = get_condition(legacy_id)
            self.assertEqual(condition.condition_id, signs)
            self.assertIs(get_condition(condition.condition_slug), condition)
            self.assertIs(get_condition(signs), condition)

    def test_evidence_nonorthogonality_is_explicit(self):
        self.assertFalse(get_condition("--").evidence_available)
        self.assertTrue(get_condition("-+").evidence_available)

    def test_deprecated_nonfactorial_c2_is_not_aliased_to_plus_minus(self):
        with self.assertRaises(KeyError):
            get_condition("C2")

    def test_truth_restricted_wolf_policy_is_condition_three(self):
        self.assertEqual(get_condition("C3").wolf_policy, "truth_restricted")

    def test_condition_four_is_baseline_good_agents_with_truth_restricted_wolves(self):
        condition = get_condition("C4")
        self.assertEqual(condition.good_policy, "baseline")
        self.assertEqual(condition.wolf_policy, "truth_restricted")
        self.assertEqual(condition.evidence_mode, "system_full_complementary")


if __name__ == "__main__":
    unittest.main()
