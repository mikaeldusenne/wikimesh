import unittest
from unittest.mock import Mock, patch

import requests

from backend.src import wiki_fetcher as wiki


class WikipediaFetcherTest(unittest.TestCase):
    def test_session_identifies_client(self):
        with wiki._session() as session:
            self.assertEqual(session.headers["User-Agent"], wiki.USER_AGENT)

    def test_retry_policy_is_bounded(self):
        retry = wiki._retry()
        self.assertEqual(retry.total, 4)
        self.assertTrue(retry.respect_retry_after_header)
        self.assertTrue(retry.is_retry("GET", 503))
        self.assertFalse(retry.is_retry("POST", 503))

    def test_get_json_uses_timeout_and_checks_status(self):
        response = Mock()
        response.json.return_value = {"query": {"pages": {}}}
        session = Mock()
        session.get.return_value = response

        wiki._get_json(session, "https://example.test", {"q": "x"})

        session.get.assert_called_once_with(
            "https://example.test",
            params={"q": "x"},
            timeout=wiki.TIMEOUT,
        )
        response.raise_for_status.assert_called_once_with()

    def test_network_failures_propagate(self):
        for error in (requests.Timeout(), requests.ConnectionError()):
            session = Mock()
            session.get.side_effect = error
            with self.assertRaises(type(error)):
                wiki._get_json(session, "https://example.test", {})

    def test_http_5xx_and_bad_json_propagate(self):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("503")
        session = Mock(get=Mock(return_value=response))
        with self.assertRaises(requests.HTTPError):
            wiki._get_json(session, "https://example.test", {})

        response.raise_for_status.side_effect = None
        response.json.side_effect = ValueError("bad json")
        with self.assertRaises(ValueError):
            wiki._get_json(session, "https://example.test", {})

    def test_api_errors_propagate(self):
        response = Mock()
        response.json.return_value = {"error": {"code": "ratelimited"}}
        session = Mock(get=Mock(return_value=response))
        with self.assertRaisesRegex(RuntimeError, "ratelimited"):
            wiki._get_json(session, "https://example.test", {})

    def test_malformed_schema_is_not_a_no_result(self):
        with self.assertRaises(KeyError):
            wiki.extract_q({"query": {}})

    @patch.object(wiki, "_get_json")
    def test_pagination_yields_all_links(self, get_json):
        get_json.side_effect = [
            {
                "query": {
                    "pages": {
                        "1": {"langlinks": [{"lang": "fr", "*": "Asthme"}]}
                    }
                },
                "continue": {"llcontinue": "x"},
            },
            {
                "query": {
                    "pages": {
                        "1": {"langlinks": [{"lang": "de", "*": "Asthma"}]}
                    }
                }
            },
        ]

        result = list(wiki.paginated_query({}, wiki.extract_q, lang="en"))

        self.assertEqual([entry["lang"] for entry in result], ["fr", "de"])
        self.assertEqual(get_json.call_args_list[1].args[2]["llcontinue"], "x")


if __name__ == "__main__":
    unittest.main()
