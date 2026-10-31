"""Bot tests"""

import os
import sys
import tempfile
import unittest

from ruamel import yaml

sys.path.append("..")  # Adds higher directory to python modules path.
from module.bot import DownloadBot


class DownloadBotConfigTestCase(unittest.TestCase):
    """Bot config is saved where it is loaded from"""

    def test_update_config_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            bot = DownloadBot()
            bot.config_path = os.path.join(tmp, "bot.yaml")
            bot.download_filter = ["message_date >= 2026-01-01"]
            bot.update_config()

            self.assertTrue(os.path.exists(bot.config_path))

            loaded = DownloadBot()
            with open(bot.config_path, encoding="utf-8") as f:
                loaded.assign_config(yaml.YAML().load(f.read()))
            self.assertEqual(
                list(loaded.download_filter), ["message_date >= 2026-01-01"]
            )
