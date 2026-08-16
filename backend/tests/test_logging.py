import importlib
import logging
import os
import unittest
from unittest.mock import patch

import backend.app as app_module


class LoggingLevelTest(unittest.TestCase):
    def _reload(self, prod):
        with patch.dict(os.environ, {"PROD": prod}, clear=False):
            return importlib.reload(app_module)

    def test_development_defaults_to_debug(self):
        module = self._reload("")
        self.assertEqual(logging.getLogger("wikimesh").level, logging.DEBUG)
        self.assertEqual(module.app.logger.level, logging.DEBUG)

    def test_production_defaults_to_warning(self):
        module = self._reload("1")
        self.assertEqual(logging.getLogger("wikimesh").level, logging.WARNING)
        self.assertEqual(module.app.logger.level, logging.WARNING)


if __name__ == "__main__":
    unittest.main()
