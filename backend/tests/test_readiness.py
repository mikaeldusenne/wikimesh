import unittest
from unittest.mock import MagicMock, patch

from backend.app import app


class ReadinessTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("backend.app.db.connect")
    def test_status_never_touches_dependencies(self, connect):
        response = self.client.get("/wikimesh/status")
        self.assertEqual(response.status_code, 200)
        connect.assert_not_called()

    def test_ready_checks_mongo_and_redis(self):
        database = MagicMock()
        with patch("backend.app.db.connect", return_value=database), \
             patch("backend.app.redis_client.ping") as redis_ping:
            response = self.client.get("/wikimesh/ready")

        self.assertEqual(response.status_code, 200)
        database.command.assert_called_once_with("ping")
        redis_ping.assert_called_once_with()

    @patch("backend.app.db.connect", side_effect=RuntimeError("mongo down"))
    def test_ready_returns_503_on_dependency_failure(self, _connect):
        self.assertEqual(self.client.get("/wikimesh/ready").status_code, 503)


if __name__ == "__main__":
    unittest.main()
