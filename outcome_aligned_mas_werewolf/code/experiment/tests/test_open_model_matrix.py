import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from run_open_model_matrix import (
    configure_vllm_client,
    main,
    require_expected_server_model,
)


class _Response:
    def __init__(self, model_ids):
        self._body = json.dumps({
            "object": "list",
            "data": [{"id": model_id} for model_id in model_ids],
        }).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


class OpenModelMatrixRoutingTest(unittest.TestCase):
    def test_stale_model_override_is_rebound_to_requested_family(self):
        with patch.dict(
            os.environ,
            {"LOCAL_LLM_MODEL_ID": "mistralai/Mistral-Nemo-Instruct-2407"},
            clear=False,
        ):
            model = configure_vllm_client(
                "phi3_medium_14b", "http://127.0.0.1:18080/v1"
            )
            self.assertEqual(
                model["endpoint_model"], "microsoft/Phi-3-medium-128k-instruct"
            )
            self.assertEqual(
                os.environ["LOCAL_LLM_MODEL_ID"],
                "microsoft/Phi-3-medium-128k-instruct",
            )
            self.assertEqual(
                os.environ["LOCAL_LLM_BASE_URL"],
                "http://127.0.0.1:18080/v1",
            )

    def test_live_preflight_accepts_exact_served_model(self):
        model = {"endpoint_model": "expected/model"}
        with patch(
            "run_open_model_matrix.urlopen",
            return_value=_Response(["expected/model"]),
        ):
            served = require_expected_server_model(
                model, "http://127.0.0.1:18080/v1"
            )
        self.assertEqual(served, ("expected/model",))

    def test_live_preflight_rejects_cross_family_model(self):
        model = {"endpoint_model": "microsoft/Phi-3-medium-128k-instruct"}
        with patch(
            "run_open_model_matrix.urlopen",
            return_value=_Response(["mistralai/Mistral-Nemo-Instruct-2407"]),
        ):
            with self.assertRaisesRegex(RuntimeError, "routing mismatch"):
                require_expected_server_model(
                    model, "http://127.0.0.1:18080/v1"
                )

    def test_parallel_shard_control_files_do_not_touch_episode_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "episodes"
            control = root / "control" / "llama31_8b" / "pp" / "seed_1"
            argv = [
                "run_open_model_matrix.py",
                "--model",
                "llama31_8b",
                "--conditions",
                "pp",
                "--seeds",
                "1",
                "--output-dir",
                str(output),
                "--control-dir",
                str(control),
                "--preflight-only",
            ]
            with patch.object(sys, "argv", argv):
                self.assertEqual(main(), 0)
            self.assertTrue((control / "matrix_spec.json").exists())
            self.assertFalse((output / "llama31_8b" / "matrix_spec.json").exists())


if __name__ == "__main__":
    unittest.main()
