import unittest

from experiment.information_analysis import (
    LABEL_MISLEADING,
    LABEL_NEUTRAL,
    LABEL_POSITIVE,
    LABEL_UNRESOLVED,
    parse_public_message,
)
from experiment.information_metrics import (
    conditional_mutual_information,
    joint_source,
    mmi_pid_synergy,
    roundwise_rjig,
)


class InformationMetricsTest(unittest.TestCase):
    def test_xor_has_joint_information_but_no_single_source_information(self):
        rows = []
        for x1 in (0, 1):
            for x2 in (0, 1):
                rows.append({"x1": x1, "x2": x2, "y": x1 ^ x2})
        self.assertAlmostEqual(conditional_mutual_information(rows, "x1", "y"), 0.0)
        self.assertAlmostEqual(conditional_mutual_information(rows, "x2", "y"), 0.0)
        joint_rows = joint_source(rows, ("x1", "x2"), output="x_joint")
        result = roundwise_rjig(joint_rows, "x_joint", ("x1", "x2"), "y")
        self.assertAlmostEqual(result["group_information_bits"], 1.0)
        self.assertAlmostEqual(result["rjig_bits"], 1.0)

    def test_mmi_pid_proxy_recovers_xor_synergy(self):
        rows = []
        for x1 in (0, 1):
            for x2 in (0, 1):
                rows.append({"x1": x1, "x2": x2, "y": x1 ^ x2})
        result = mmi_pid_synergy(rows, "x1", "x2", "y")
        self.assertAlmostEqual(result["synergy_bits"], 1.0)


class ClaimParserTest(unittest.TestCase):
    manifest = {
        "condition_id": "C1_test",
        "seed": 1,
        "player_names": ["Alice", "Bob", "Cara"],
        "role_assignment": {
            "Alice": "Villager",
            "Bob": "Werewolf",
            "Cara": "Seer",
        },
    }

    def parse(self, dialogue, speaker="Cara"):
        return parse_public_message(
            {
                "event_id": "r1_t1",
                "round": 1,
                "speaker": speaker,
                "dialogue": dialogue,
                "evidence_refs": [],
            },
            manifest=self.manifest,
            evidence_by_id={},
            provider="test",
            episode_id="test/C1/seed_1",
        )

    def test_true_wolf_accusation_is_positive(self):
        claims = self.parse("Bob is a Werewolf and we should vote him out.")
        self.assertIn(LABEL_POSITIVE, {claim.label for claim in claims})

    def test_good_accusation_is_misleading(self):
        claims = self.parse("Alice is suspicious and we should remove her.")
        self.assertIn(LABEL_MISLEADING, {claim.label for claim in claims})

    def test_true_clearance_is_neutral(self):
        claims = self.parse("Alice is a Villager and should be trusted.")
        self.assertIn(LABEL_NEUTRAL, {claim.label for claim in claims})

    def test_role_concealment_is_not_automatically_misleading(self):
        claims = self.parse("I am the Doctor.", speaker="Alice")
        role_claims = [claim for claim in claims if claim.claim_type == "role_identity"]
        self.assertTrue(role_claims)
        self.assertTrue(role_claims[0].role_concealment)
        self.assertEqual(role_claims[0].label, LABEL_UNRESOLVED)


if __name__ == "__main__":
    unittest.main()
