import os
import unittest
from unittest.mock import Mock, patch

from werewolf import apis


class DeepSeekProviderTest(unittest.TestCase):
    def test_deepseek_model_uses_deepseek_endpoint_and_key_variable(self):
        fake_client = Mock()
        fake_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content='{"ok": true}'))
        ]
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "dummy-test-key",
                "DEEPSEEK_THINKING": "disabled",
            },
            clear=False,
        ):
            with patch.object(apis, "OpenAI", return_value=fake_client) as openai:
                result = apis.generate("deepseek-v4-flash", prompt="{}")

        self.assertEqual(result, '{"ok": true}')
        openai.assert_called_once_with(
            api_key="dummy-test-key", base_url="https://api.deepseek.com"
        )
        request = fake_client.chat.completions.create.call_args.kwargs
        self.assertEqual(request["model"], "deepseek-v4-flash")
        self.assertEqual(request["response_format"], {"type": "json_object"})
        self.assertEqual(
            request["extra_body"], {"thinking": {"type": "disabled"}}
        )


if __name__ == "__main__":
    unittest.main()
