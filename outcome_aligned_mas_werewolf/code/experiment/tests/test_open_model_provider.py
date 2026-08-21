import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from werewolf import apis
from werewolf import lm
from werewolf.prompts import BIDDING_SCHEMA


class _Handler(BaseHTTPRequestHandler):
    requests = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        self.__class__.requests.append(payload)
        body = json.dumps({
            "choices": [{"message": {"content": '{"ok": true}'}}],
            "usage": {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7},
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class OpenModelProviderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _Handler.requests = []
        try:
            cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        except PermissionError as exc:
            if os.environ.get("REQUIRE_LOOPBACK_TEST") == "1":
                raise
            raise unittest.SkipTest(
                "Loopback sockets are disabled in this execution sandbox; "
                "the server-side verification gate must run this test."
            ) from exc
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)

    def test_openai_compatible_request_is_seeded_and_logged(self):
        base_url = f"http://127.0.0.1:{self.server.server_port}/v1"
        environment = {
            "LOCAL_LLM_BACKEND": "test",
            "LOCAL_LLM_BASE_URL": base_url,
            "EXPERIMENT_SEED": "1001",
        }
        with patch.dict(os.environ, environment, clear=False):
            first = apis.generate(
                "local:llama31_8b",
                prompt="Return JSON",
                response_schema={
                    "type": "object",
                    "properties": {"ok": {"type": "boolean"}},
                    "required": ["ok"],
                },
                temperature=0.5,
            )
            second = apis.generate(
                "local:llama31_8b",
                prompt="Return JSON",
                response_schema={
                    "type": "object",
                    "properties": {"ok": {"type": "boolean"}},
                    "required": ["ok"],
                },
                temperature=0.5,
            )

        self.assertEqual(first, '{"ok": true}')
        self.assertEqual(first.usage["total_tokens"], 7)
        self.assertEqual(first.provider_metadata["provider"], "openai_compatible_local")
        request_one, request_two = _Handler.requests[-2:]
        self.assertEqual(request_one["seed"], request_two["seed"])
        self.assertEqual(request_one["temperature"], 0.5)
        self.assertEqual(request_one["max_tokens"], 512)
        self.assertEqual(request_one["response_format"]["type"], "json_schema")
        self.assertTrue(request_one["response_format"]["json_schema"]["strict"])
        self.assertEqual(
            request_one["response_format"]["json_schema"]["schema"]["required"],
            ["ok"],
        )
        self.assertEqual(first.provider_metadata["structured_output"], "json_schema")

    def test_belief_snapshot_schema_reaches_openai_compatible_endpoint(self):
        base_url = f"http://127.0.0.1:{self.server.server_port}/v1"
        with patch.dict(os.environ, {
            "LOCAL_LLM_BACKEND": "test",
            "LOCAL_LLM_BASE_URL": base_url,
            "EXPERIMENT_SEED": "1001",
        }, clear=False):
            apis.generate(
                "local:llama31_8b",
                prompt="Return the complete belief panel as JSON.",
                response_schema=BIDDING_SCHEMA,
                temperature=0.5,
            )
        transmitted = _Handler.requests[-1]["response_format"]["json_schema"]["schema"]
        self.assertEqual(transmitted["required"], BIDDING_SCHEMA["required"])
        self.assertIn("suspect_levels", transmitted["properties"])
        self.assertIn("evidence_state", transmitted["properties"])

    def test_exhausted_validation_retains_last_structured_response_for_repair(self):
        with patch(
            "werewolf.lm.apis.generate",
            return_value='{"top_suspect": "None yet"}',
        ):
            result, log = lm.generate(
                "Return JSON.",
                {
                    "type": "object",
                    "properties": {"top_suspect": {"type": "string"}},
                    "required": ["top_suspect"],
                },
                {},
                model="local:llama31_8b",
                result_validator=lambda payload: (
                    "top_suspect must be a living player"
                    if payload.get("top_suspect") == "None yet"
                    else None
                ),
            )

        self.assertIsNone(result)
        self.assertEqual(
            log.metadata["last_invalid_result"],
            {"top_suspect": "None yet"},
        )
        self.assertTrue(log.metadata["validation_failures"])
