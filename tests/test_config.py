import importlib
import os
import sys
import unittest
from pathlib import Path


class ConfigEnvTests(unittest.TestCase):
    def test_loads_supabase_values_from_dotenv(self):
        sys.modules.pop("config", None)
        os.environ.pop("SUPABASE_URL", None)
        os.environ.pop("SUPABASE_ANON_KEY", None)

        import config

        config_module = importlib.reload(config)
        env_path = Path(__file__).resolve().parents[1] / ".env"
        expected_values = {}

        for line in env_path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            expected_values[key.strip()] = value.strip()

        self.assertEqual(config_module.Config().SUPABASE_URL, expected_values["SUPABASE_URL"])
        self.assertEqual(config_module.Config().SUPABASE_ANON_KEY, expected_values["SUPABASE_ANON_KEY"])


if __name__ == "__main__":
    unittest.main()
