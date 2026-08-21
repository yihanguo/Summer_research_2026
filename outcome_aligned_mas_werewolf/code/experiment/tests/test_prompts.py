import unittest

from werewolf.lm import format_prompt
from werewolf.prompts import BIDDING, DEBATE


class PromptTest(unittest.TestCase):
    def test_truth_restricted_wolf_prompt_excludes_fabrication_branch(self):
        worldstate = {
            "name": "Wolf",
            "role": "Werewolf",
            "round": 1,
            "werewolf_context": "",
            "personality": "",
            "remaining_players": "Wolf, Alex",
            "remaining_player_names": ["Wolf", "Alex"],
            "observations": [],
            "private_evidence": [],
            "private_round_memory": [],
            "coordination_policy_name": "truth_restricted",
            "coordination_policy": "Do not fabricate evidence.",
            "debate": [],
            "bidding_rationale": "",
            "debate_turns_left": 8,
            "num_players": 8,
            "num_villagers": 4,
            "current_belief": {
                "top_suspect": "Alex",
                "suspect_confidence_bin": 3,
                "intended_vote": "Alex",
                "evidence_state": "public_only",
            },
        }
        rendered = format_prompt(DEBATE, worldstate)
        self.assertNotIn("Deception is your greatest weapon", rendered)
        self.assertNotIn("fabricate inconsistencies", rendered)
        self.assertIn("clearly help the Villagers identify a Werewolf", rendered)

    def test_bid_prompt_requests_complete_suspicion_vector(self):
        worldstate = {
            "name": "Alex",
            "role": "Villager",
            "round": 1,
            "werewolf_context": "",
            "personality": "",
            "remaining_players": "Alex, Blair, Casey",
            "remaining_player_names": ["Alex", "Blair", "Casey"],
            "observations": [],
            "private_evidence": [],
            "private_round_memory": [],
            "coordination_policy_name": "baseline",
            "coordination_policy": "",
            "debate": [],
            "bidding_rationale": "",
            "debate_turns_left": 8,
            "num_players": 8,
            "num_villagers": 4,
            "current_belief": {},
        }
        rendered = format_prompt(BIDDING, worldstate)
        self.assertIn('"player": "Blair"', rendered)
        self.assertIn('"player": "Casey"', rendered)
        self.assertNotIn('"player": "Alex"', rendered)
        for field in (
            "top_suspect", "suspect_confidence_bin", "intended_vote",
            "evidence_state", "suspect_levels",
        ):
            self.assertIn(field, rendered)
        self.assertIn("Never return none, N/A, unknown", rendered)


if __name__ == "__main__":
    unittest.main()
