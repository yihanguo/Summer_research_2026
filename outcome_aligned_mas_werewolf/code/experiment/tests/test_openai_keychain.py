import os
import unittest
from unittest.mock import patch

import openai_keychain


class OpenAIKeychainTests(unittest.TestCase):
    @patch.dict(os.environ, {"USER": "test-user", "OPENAI_API_KEY": "env-key"}, clear=True)
    def test_environment_key_takes_precedence(self):
        self.assertEqual(openai_keychain.load_key(), "env-key")

    @patch.dict(os.environ, {"USER": "test-user"}, clear=True)
    @patch("openai_keychain.subprocess.run")
    def test_loads_keychain_value_without_printing_it(self, run):
        run.return_value.stdout = "keychain-key\n"
        self.assertEqual(openai_keychain.load_key(), "keychain-key")
        run.assert_called_once_with(
            [
                "security",
                "find-generic-password",
                "-a",
                "test-user",
                "-s",
                openai_keychain.KEYCHAIN_SERVICE,
                "-w",
            ],
            check=False,
            stdout=openai_keychain.subprocess.PIPE,
            stderr=openai_keychain.subprocess.DEVNULL,
            text=True,
        )

    @patch.dict(os.environ, {"USER": "test-user"}, clear=True)
    @patch("openai_keychain.subprocess.run")
    def test_saves_key_without_shell(self, run):
        openai_keychain.save_key("new-key")
        run.assert_called_once_with(
            [
                "security",
                "add-generic-password",
                "-U",
                "-a",
                "test-user",
                "-s",
                openai_keychain.KEYCHAIN_SERVICE,
                "-w",
                "new-key",
            ],
            check=True,
            stdout=openai_keychain.subprocess.DEVNULL,
            stderr=openai_keychain.subprocess.PIPE,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
