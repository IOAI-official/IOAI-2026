import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class ConfigContractTests(unittest.TestCase):
    def test_leaderboard_a_is_a_single_config(self):
        config_dir = DATA / "leaderboard_a_config"
        config = json.loads((config_dir / "field_config.json").read_text())
        self.assertIsInstance(config, dict)
        self.assertTrue((config_dir / "eval_config.json").is_file())

    def test_leaderboard_b_is_a_multi_config_split(self):
        config_dir = DATA / "leaderboard_b_config"
        self.assertFalse((config_dir / "field_config.json").exists())
        configs = json.loads((config_dir / "field_configs.json").read_text())
        self.assertIsInstance(configs, list)
        self.assertGreater(len(configs), 0)
        self.assertTrue(all(isinstance(config, dict) for config in configs))
        self.assertTrue((config_dir / "eval_config.json").is_file())


if __name__ == "__main__":
    unittest.main()
