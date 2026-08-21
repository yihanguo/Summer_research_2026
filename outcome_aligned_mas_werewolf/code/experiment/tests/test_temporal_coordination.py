import unittest
import tempfile
from pathlib import Path

from experiment.temporal_coordination import (
    _episode_transitions,
    _macro_criterion,
    agent_state,
    macro_state,
    validate_panel,
    williams_beer_pid,
    write_results,
)


class WilliamsBeerPidTest(unittest.TestCase):
    def test_xor_is_one_bit_of_synergy(self):
        rows = [(x1, x2, x1 ^ x2) for x1 in (0, 1) for x2 in (0, 1)]
        result = williams_beer_pid(rows)
        self.assertAlmostEqual(result["synergy_bits"], 1.0)
        self.assertAlmostEqual(result["redundancy_bits"], 0.0)

    def test_duplicate_sources_are_one_bit_redundant(self):
        rows = [(value, value, value) for value in (0, 1)] * 8
        result = williams_beer_pid(rows)
        self.assertAlmostEqual(result["redundancy_bits"], 1.0)
        self.assertAlmostEqual(result["synergy_bits"], 0.0)
        self.assertAlmostEqual(result["unique_i_bits"], 0.0)

    def test_unique_copy_assigns_one_bit_to_first_source(self):
        rows = [(x1, x2, x1) for x1 in (0, 1) for x2 in (0, 1)]
        result = williams_beer_pid(rows)
        self.assertAlmostEqual(result["unique_i_bits"], 1.0)
        self.assertAlmostEqual(result["unique_j_bits"], 0.0)
        self.assertAlmostEqual(result["synergy_bits"], 0.0)

    def test_independent_target_has_no_pid_information(self):
        rows = [
            (x1, x2, target)
            for x1 in (0, 1)
            for x2 in (0, 1)
            for target in (0, 1)
        ]
        result = williams_beer_pid(rows)
        self.assertAlmostEqual(result["joint_information_bits"], 0.0)
        self.assertAlmostEqual(result["synergy_bits"], 0.0)
        self.assertAlmostEqual(result["redundancy_bits"], 0.0)


class StateContractTest(unittest.TestCase):
    def event(self, player, top, levels):
        return {
            "player": player,
            "living_players": ["A", "B", "C"],
            "bid": 2,
            "top_suspect": top,
            "suspect_confidence_bin": 3,
            "intended_vote": top,
            "evidence_state": "public_only",
            "suspect_levels": [
                {"player": name, "level": level} for name, level in levels.items()
            ],
        }

    def test_complete_panel_and_macro_exclude_hidden_roles(self):
        panel = {
            "A": self.event("A", "C", {"B": 1, "C": 4}),
            "B": self.event("B", "C", {"A": 1, "C": 3}),
            "C": self.event("C", "A", {"A": 3, "B": 2}),
        }
        validate_panel(panel)
        self.assertEqual(
            macro_state(panel, ["A", "B"]),
            (
                ("A", "B", "C"),
                (("A", 1), ("B", 1), ("C", 3.5)),
                "C",
                1,
            ),
        )
        self.assertNotIn("Werewolf", repr(agent_state(panel["A"])))

    def test_missing_suspicion_entry_is_rejected(self):
        panel = {
            "A": self.event("A", "C", {"B": 1}),
            "B": self.event("B", "C", {"A": 1, "C": 3}),
            "C": self.event("C", "A", {"A": 3, "B": 2}),
        }
        with self.assertRaises(ValueError):
            validate_panel(panel)

    def test_macro_criterion_uses_sum_not_best_agent(self):
        transitions = [
            {
                "coalition": ["A", "B"],
                "current": {"A": 0, "B": value},
                "macro_current": value,
                "macro_future": value,
            }
            for value in (0, 1)
        ]
        result = _macro_criterion(transitions)
        self.assertAlmostEqual(result["macro_predictive_information_bits"], 1.0)
        self.assertAlmostEqual(result["individual_information_bits"]["A"], 0.0)
        self.assertAlmostEqual(result["individual_information_bits"]["B"], 1.0)
        self.assertAlmostEqual(result["s_macro_bits"], 0.0)

    def test_repaired_source_state_is_excluded_from_primary_transitions(self):
        events = []
        for turn in (1, 2):
            for player, top, levels in (
                ("A", "C", {"B": 1, "C": 4}),
                ("B", "C", {"A": 1, "C": 3}),
                ("C", "A", {"A": 3, "B": 2}),
            ):
                event = self.event(player, top, levels)
                event.update({
                    "event_type": "belief_snapshot",
                    "round": 1,
                    "turn": turn,
                    "structured_repair": player == "A" and turn == 1,
                })
                events.append(event)
        roles = {"A": "Villager", "B": "Villager", "C": "Werewolf"}

        self.assertEqual(
            _episode_transitions(events, roles, 1, "good"),
            [],
        )
        self.assertEqual(
            len(_episode_transitions(
                events, roles, 1, "good", include_repaired=True
            )),
            1,
        )

    def test_zero_valid_transitions_render_as_na_instead_of_crashing(self):
        payload = {
            "complete_episodes_with_belief_panels": 1,
            "lag": 1,
            "permutations": 5,
            "cells": [{
                "model_alias": "test",
                "model_family": "test",
                "condition_id": "++",
                "coalition": "good",
                "episodes": 1,
                "transitions": 0,
                "repair_excluded_transitions": 1,
                "pairwise_pid": {
                    "pair_count": 0,
                    "median_synergy_bits": 0.0,
                },
                "macro_criterion": {"s_macro_bits": 0.0},
                "temporal_null": {},
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_results(payload, output)
            markdown = (output / "temporal_coordination.md").read_text(
                encoding="utf-8"
            )
        self.assertIn("NA", markdown)


if __name__ == "__main__":
    unittest.main()
