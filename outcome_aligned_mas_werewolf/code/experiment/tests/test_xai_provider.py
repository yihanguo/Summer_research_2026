import os
import unittest
from unittest.mock import Mock, patch

from werewolf import apis


class XaiProviderTest(unittest.TestCase):
    def test_grok_model_uses_xai_endpoint_and_key_variable(self):
        fake_client = Mock()
        fake_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content='{"ok": true}'))
        ]
        with patch.dict(os.environ, {"XAI_API_KEY": "dummy-test-key"}, clear=False):
            with patch.object(apis, "OpenAI", return_value=fake_client) as openai:
                result = apis.generate("grok-4.5", prompt="{}")

        self.assertEqual(result, '{"ok": true}')
        openai.assert_called_once_with(
            api_key="dummy-test-key", base_url="https://api.x.ai/v1"
        )
        fake_client.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
