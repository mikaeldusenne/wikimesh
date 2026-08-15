import unittest
from unittest.mock import Mock, patch

import requests

from backend.src import wiki_fetcher as wiki


class WikipediaFetcherTest(unittest.TestCase):
    def test_session_retries_transient_failures(self):
        self.assertEqual(wiki._session().get_adapter("https://").max_retries.total, 4)

    def test_request_failures_are_not_results(self):
        for error in (requests.Timeout(), requests.ConnectionError()):
            session = Mock()
            session.get.side_effect = error
            with self.assertRaises(type(error)):
                wiki._get_json(session, "https://example.test", {})

    def test_http_and_json_errors_propagate(self):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError()
        with self.assertRaises(requests.HTTPError):
            wiki._get_json(Mock(get=Mock(return_value=response)), "https://example.test", {})

        response.raise_for_status.side_effect = None
        response.json.side_effect = ValueError("bad json")
        with self.assertRaises(ValueError):
            wiki._get_json(Mock(get=Mock(return_value=response)), "https://example.test", {})

    @patch.object(wiki, "_get_json")
    def test_pagination_yields_all_links(self, get_json):
        get_json.side_effect = [
            {"query": {"pages": {"1": {"langlinks": [{"lang": "fr", "*": "Asthme"}]}}}, "continue": {"llcontinue": "x"}},
            {"query": {"pages": {"1": {"langlinks": [{"lang": "de", "*": "Asthma"}]}}}},
        ]
        result = list(wiki.paginated_query({}, wiki.extract_q, lang="en"))
        self.assertEqual([e["lang"] for e in result], ["fr", "de"])


if __name__ == "__main__":
    unittest.main()
