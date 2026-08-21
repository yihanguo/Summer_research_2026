import tempfile
import unittest
import json
from pathlib import Path

from experiment.conditions import get_condition
from experiment.experiment_runner import OneDayExperiment, run_episode


class PipelineTest(unittest.TestCase):
    def test_all_agents_receive_every_message_and_extract_privately(self):
        result = OneDayExperiment(get_condition("C1"), 7, turns=4)
        output = result.run()
        self.assertEqual(len(output["messages"]), 4)
        self.assertEqual({tuple(message.recipients) for message in output["messages"]}, {tuple(result.player_names)})
        self.assertEqual(len(output["extractions"]), len(result.player_names))
        self.assertTrue(all(event.visible_to == [event.player] for event in output["extractions"]))

    def test_episode_writes_analysis_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = run_episode("C1", 1001, Path(directory) / "episode", turns=3)
            self.assertTrue((path / "manifest.json").exists())
            self.assertTrue((path / "events.jsonl").exists())
            self.assertTrue((path / "metrics.json").exists())
            manifest = json.loads((path / "manifest.json").read_text())
            public_events = [
                json.loads(line)
                for line in (path / "events.jsonl").read_text().splitlines()
                if '"event_type": "public_message"' in line
            ]
            self.assertEqual(manifest["max_debate_turns"], 3)
            self.assertEqual(len(public_events), manifest["max_debate_turns"])

    def test_minus_minus_has_no_hidden_evidence_fixture(self):
        output = OneDayExperiment(get_condition("--"), 1, turns=2).run()
        self.assertEqual(output["evidence"], [])
        self.assertFalse(output["manifest"]["evidence_available"])


if __name__ == "__main__":
    unittest.main()
