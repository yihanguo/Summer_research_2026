import unittest

from experiment.evidence import (
    assign_complementary_evidence,
    evidence_sufficiency,
    generate_positive_evidence,
    validate_evidence,
)


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.holders = ["Derek", "Scott", "Jacob"]
        self.evidence = generate_positive_evidence("Tyler", self.holders)

    def test_primary_fixture_is_truthful_and_positive(self):
        validate_evidence(self.evidence, "Tyler")
        self.assertTrue(evidence_sufficiency(self.evidence, "Tyler"))

    def test_prompt_dict_hides_gold_fields(self):
        prompt_item = self.evidence[0].to_prompt_dict()
        self.assertNotIn("truth_value", prompt_item)
        self.assertNotIn("direction", prompt_item)
        self.assertNotIn("strength", prompt_item)

    def test_complementary_union_is_preserved(self):
        assignments = assign_complementary_evidence(self.evidence, self.holders)
        union = [item for items in assignments.values() for item in items]
        self.assertTrue(evidence_sufficiency(self.evidence, "Tyler", [item.evidence_id for item in union]))
        self.assertTrue(all(items for items in assignments.values()))


if __name__ == "__main__":
    unittest.main()
