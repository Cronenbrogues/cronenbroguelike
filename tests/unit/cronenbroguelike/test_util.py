import json
import os
import tempfile
import unittest
from unittest.mock import patch

from cronenbroguelike import util


_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class UtilTest(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        default_config = {
            "skulduggery": "chicanery",
            "wangling": "flimflam",
        }
        override_config = {
            "skulduggery": "guile",
            "artifice": "craft",
        }

        def _write(config, file_name):
            with open(file_name, "w") as outp:
                json.dump(config, outp)

        self._default_file = os.path.join(self._temp_dir.name, "config.default.json")
        self._override_file = os.path.join(self._temp_dir.name, "config.json")
        self._whos_that_file = os.path.join(self._temp_dir.name, "whosthatitspat.json")
        _write(default_config, self._default_file)
        _write(override_config, self._override_file)
        _write(override_config, self._whos_that_file)

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_read_configs_default_default_default(self):
        config = util.read_configs(self._default_file)
        self.assertEqual(
            {
                "wangling": "flimflam",
                "skulduggery": "guile",
                "artifice": "craft",
            },
            config,
        )

    def test_read_configs_default_is_not_the_default(self):
        config = util.read_configs(self._default_file, self._whos_that_file)
        self.assertEqual(
            {
                "wangling": "flimflam",
                "skulduggery": "guile",
                "artifice": "craft",
            },
            config,
        )

    def test_read_configs_how_i_learned_to_stop_defaulting(self):
        spankx = os.path.join(self._temp_dir.name, "spankx")
        self.assertFalse(os.path.exists(spankx))
        config = util.read_configs(self._default_file, spankx)
        self.assertEqual(
            {
                "wangling": "flimflam",
                "skulduggery": "chicanery",
            },
            config,
        )

    def test_read_configs_need_that_first_one_though(self):
        mendicant = os.path.join(self._temp_dir.name, "mendicant")
        self.assertFalse(os.path.exists(mendicant))
        with self.assertRaises(FileNotFoundError):
            config = util.read_configs(mendicant)

    @patch("cronenbroguelike.util.read_configs")
    def test_read_overridable_config_logging(self, mock_read):
        _ = util.read_overridable_config(util.ConfigType.LOGGING)
        mock_read.assert_called_once_with(
            os.path.join(_ROOT, "config/logging_config.default.json"),
            os.path.join(_ROOT, "config/logging_config.json"),
        )

    @patch("cronenbroguelike.util.read_configs")
    def test_read_overridable_config_game(self, mock_read):
        _ = util.read_overridable_config(util.ConfigType.GAME)
        mock_read.assert_called_once_with(
            os.path.join(_ROOT, "config/game_config.default.json"),
            os.path.join(_ROOT, "config/game_config.json"),
        )
