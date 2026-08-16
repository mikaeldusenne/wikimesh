import unittest
from unittest.mock import patch

from backend.src import db_exporter


class MatchReportTest(unittest.TestCase):
    @patch.object(db_exporter, "list_match_mesh_wiki", return_value=iter(()))
    def test_empty_identifier_has_empty_overall_summary(self, _):
        self.assertEqual(
            db_exporter.report_match_mesh_wiki("EMPTY"),
            {"overall": {}},
        )


if __name__ == "__main__":
    unittest.main()
