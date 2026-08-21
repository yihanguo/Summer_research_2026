import unittest
from unittest.mock import patch

from experiment.arena_adapter import ExperimentEventSink
from experiment.conditions import get_condition
from werewolf.game import GameMaster
from werewolf.lm import LmLog
from werewolf.model import Doctor, Round, RoundLog, Seer, State, Villager, Werewolf


class GameInvariantTest(unittest.TestCase):
    def _state(self):
        villagers = [Villager("VillagerA"), Villager("VillagerB")]
        wolves = [Werewolf("WolfA"), Werewolf("WolfB")]
        doctor = Doctor("Doctor")
        seer = Seer("Seer")
        state = State("test", seer, doctor, villagers, wolves)
        names = list(state.players)
        for player in state.players.values():
            other_wolf = "WolfB" if player.name == "WolfA" else "WolfA" if player.name == "WolfB" else None
            player.initialize_game_view(0, names.copy(), other_wolf=other_wolf)
        return state

    def test_protected_player_remains_in_authoritative_and_private_states(self):
        state = self._state()
        game = GameMaster(state, max_debate_turns=3)
        round_state = Round()
        round_state.players = list(state.players)
        round_state.eliminated = "VillagerA"
        round_state.protected = "VillagerA"
        state.rounds.append(round_state)
        game.logs.append(RoundLog())

        game.resolve_night_phase()

        self.assertIn("VillagerA", game.this_round.players)
        for player in state.players.values():
            self.assertIn("VillagerA", player.gamestate.current_players)

    def test_debate_turn_budget_is_propagated_to_every_player(self):
        state = self._state()
        game = GameMaster(state, max_debate_turns=3)
        self.assertEqual(game.max_debate_turns, 3)
        self.assertEqual({player.max_debate_turns for player in state.players.values()}, {3})

    def test_every_living_player_reports_a_complete_belief_each_turn(self):
        state = self._state()
        sink = ExperimentEventSink(get_condition("++"))
        game = GameMaster(state, event_sink=sink, max_debate_turns=3)
        round_state = Round()
        round_state.players = list(state.players)
        state.rounds.append(round_state)
        game.logs.append(RoundLog())

        def fake_generate(*args, **kwargs):
            world = args[2]
            others = [name for name in world["remaining_player_names"] if name != world["name"]]
            payload = {
                "reasoning": "I have a measured belief.",
                "bid": "2",
                "top_suspect": others[0],
                "suspect_confidence_bin": 2,
                "intended_vote": others[0],
                "evidence_state": "none",
                "suspect_levels": [
                    {"player": name, "level": 2} for name in others
                ],
            }
            return "2", LmLog("prompt", "raw", payload)

        with patch("werewolf.model.generate", side_effect=fake_generate):
            first = game.get_next_speaker(1)
            game.this_round.debate.append([first, "My public statement."])
            game.get_next_speaker(2)

        belief_events = [event for event in sink.events if event.event_type == "belief_snapshot"]
        self.assertEqual(len(belief_events), 2 * len(state.players))
        for turn in (1, 2):
            panel = [event for event in belief_events if event.turn == turn]
            self.assertEqual({event.player for event in panel}, set(state.players))
            for event in panel:
                self.assertEqual(
                    {item["player"] for item in event.suspect_levels},
                    set(state.players) - {event.player},
                )
        previous_event = next(
            event for event in belief_events if event.turn == 2 and event.player == first
        )
        self.assertFalse(previous_event.speaker_eligible)

    def test_public_debate_vector_must_match_bid_vector(self):
        state = self._state()
        player = state.players["VillagerA"]
        player.current_belief = {
            "top_suspect": "WolfA",
            "suspect_confidence_bin": 3,
            "intended_vote": "WolfA",
            "evidence_state": "public_only",
            "suspect_levels": [
                {"player": name, "level": 3 if name == "WolfA" else 2}
                for name in state.players
                if name != player.name
            ],
        }
        levels = list(player.current_belief["suspect_levels"])
        say = ", ".join(f"{item['player']}={item['level']}" for item in levels)
        self.assertIsNone(player._validate_debate_response({
            "say": say,
            "public_suspect_levels": levels,
        }))
        broken = levels[:-1]
        self.assertIsNotNone(player._validate_debate_response({
            "say": say,
            "public_suspect_levels": broken,
        }))

    def test_invalid_none_bid_is_repaired_into_complete_snapshot(self):
        state = self._state()
        player = state.players["VillagerA"]
        others = [name for name in state.players if name != player.name]
        invalid = {
            "reasoning": "I am unsure but want to speak.",
            "bid": "3",
            "top_suspect": "None yet",
            "suspect_confidence_bin": 7,
            "intended_vote": "N/A",
            "evidence_state": "unknown",
            "suspect_levels": [
                {"player": name, "level": 4 if index == 2 else 2}
                for index, name in enumerate(others)
            ],
        }
        exhausted = LmLog(
            "prompt",
            "raw",
            None,
            metadata={"last_invalid_result": invalid},
        )
        with patch("werewolf.model.generate", return_value=(None, exhausted)):
            bid, log = player.bid()

        self.assertEqual(bid, 3)
        self.assertTrue(log.metadata["structured_repair"])
        self.assertEqual(player.current_belief["top_suspect"], others[2])
        self.assertEqual(player.current_belief["intended_vote"], others[2])
        self.assertEqual(player.current_belief["suspect_confidence_bin"], 4)
        self.assertEqual(player.current_belief["evidence_state"], "none")
        self.assertEqual(
            {item["player"] for item in player.current_belief["suspect_levels"]},
            set(others),
        )

    def test_empty_bid_failure_gets_neutral_deterministic_snapshot(self):
        state = self._state()
        player = state.players["VillagerA"]
        others = [name for name in state.players if name != player.name]
        exhausted = LmLog("prompt", "raw", None)
        with patch("werewolf.model.generate", return_value=(None, exhausted)):
            bid, log = player.bid()

        self.assertEqual(bid, 0)
        self.assertEqual(player.current_belief["top_suspect"], others[0])
        self.assertEqual(player.current_belief["intended_vote"], others[0])
        self.assertEqual(player.current_belief["suspect_confidence_bin"], 0)
        self.assertTrue(log.metadata["structured_repair"])
        self.assertTrue(all(
            item["level"] == 2
            for item in player.current_belief["suspect_levels"]
        ))

    def test_game_accepts_repaired_snapshots_from_every_living_player(self):
        state = self._state()
        sink = ExperimentEventSink(get_condition("++"))
        game = GameMaster(state, event_sink=sink, max_debate_turns=3)
        round_state = Round()
        round_state.players = list(state.players)
        state.rounds.append(round_state)
        game.logs.append(RoundLog())

        def exhausted_generate(*args, **kwargs):
            world = args[2]
            return None, LmLog(
                "prompt",
                "raw",
                None,
                metadata={
                    "last_invalid_result": {
                        "reasoning": "No clear suspect yet.",
                        "bid": "1",
                        "top_suspect": "None yet",
                        "suspect_confidence_bin": 0,
                        "intended_vote": "N/A",
                        "evidence_state": "none",
                        "suspect_levels": [
                            {"player": name, "level": 2}
                            for name in world["remaining_player_names"]
                            if name != world["name"]
                        ],
                    }
                },
            )

        with patch("werewolf.model.generate", side_effect=exhausted_generate):
            speaker = game.get_next_speaker(1)

        self.assertIn(speaker, state.players)
        belief_events = [
            event for event in sink.events if event.event_type == "belief_snapshot"
        ]
        self.assertEqual(len(belief_events), len(state.players))
        self.assertTrue(all(event.structured_repair for event in belief_events))
        self.assertTrue(all(event.structured_repair_reason for event in belief_events))

    def test_invalid_debate_response_publishes_exact_measured_vector(self):
        state = self._state()
        player = state.players["VillagerA"]
        others = [name for name in state.players if name != player.name]
        player.current_belief = {
            "top_suspect": others[1],
            "suspect_confidence_bin": 3,
            "intended_vote": others[1],
            "evidence_state": "public_only",
            "suspect_levels": [
                {"player": name, "level": index % 5}
                for index, name in enumerate(others)
            ],
        }
        invalid = {
            "reasoning": "A partial declaration.",
            "say": "I am still considering the evidence.",
            "public_suspect_levels": [],
        }
        exhausted = LmLog(
            "prompt",
            "raw",
            None,
            metadata={"last_invalid_result": invalid},
        )
        with patch("werewolf.model.generate", return_value=(None, exhausted)):
            statement, log = player.debate()

        self.assertTrue(log.metadata["structured_repair"])
        self.assertEqual(
            log.result["public_suspect_levels"],
            player.current_belief["suspect_levels"],
        )
        for item in player.current_belief["suspect_levels"]:
            self.assertIn(f"{item['player']}={item['level']}", statement)
