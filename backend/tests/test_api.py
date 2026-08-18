import re
import unittest
from unittest.mock import patch

import backend.app as api
from backend.src.helpers import prepare_user_input_search_regex


class ApiValidationTest(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()

    @patch("backend.app.db.connect")
    def test_bad_query_parameters_return_400(self, _connect):
        queries = (
            "limit=nope", "limit=0", "limit=101", "from=nope", "from=-1",
            "langMesh=maybe", "langWiki=maybe",
        )
        for query in queries:
            with self.subTest(query=query):
                response = self.client.get(f"/api/mesh?{query}")
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    @patch("backend.app._get_mesh", return_value={"count": 0, "data": []})
    @patch("backend.app.db.connect")
    def test_valid_query_is_normalized_and_forwarded(self, _connect, get_mesh):
        response = self.client.get(
            "/api/mesh?from=0&limit=100&search=%20foo%20bar%20"
            "&filterOnlyNonEmpty=true&langMatchSearch=no-english&ptsynMatchSearch=pt&langSearch=fr"
            "&langMesh=no&langWiki=yes&identifier=MeSH"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_mesh.call_args.kwargs, {
            "filter_non_empty": True,
            "start": 0,
            "n": 100,
            "search": "foo bar",
            "langMatchFilter": "no-english",
            "ptsynfilter": "pt",
            "langFilter": "fr",
            "langMesh": "no",
            "langWiki": "yes",
            "identifier": "MeSH",
        })

    @patch("backend.app._get_mesh", return_value={"count": 0, "data": []})
    @patch("backend.app.db.connect")
    def test_language_presence_filters_default_to_all(self, _connect, get_mesh):
        response = self.client.get("/api/mesh?langSearch=fr&limit=1")
        self.assertEqual(response.status_code, 200)
        args = get_mesh.call_args.kwargs
        self.assertEqual((args["langMesh"], args["langWiki"]), ("all", "all"))

    def test_search_input_is_safe_and_keeps_tokenization(self):
        regex = prepare_user_input_search_regex("foo (bar [baz]")
        re.compile(regex)  # Parentheses and punctuation must never break compilation.
        re.compile(prepare_user_input_search_regex("foo \\"))
        self.assertRegex("foo xxx (bar y baz", regex)

        # Ordinary punctuation remains a separator, as before.
        self.assertRegex("foo anything bar", prepare_user_input_search_regex("foo.bar"))
        self.assertIsNone(re.search(prepare_user_input_search_regex("!!!"), "ordinary text"))

    def test_cached_routes_register_cached_views(self):
        for endpoint, view in (
            ("bprnt.get_languages", api.get_languages),
            ("bprnt.get_identifiers", api.get_identifiers),
            ("bprnt.mesh_stats", api.mesh_stats),
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIs(api.app.view_functions[endpoint], view)

    def test_cache_clear_is_not_public_view(self):
        self.assertNotIn("bprnt.clear_cache", api.app.view_functions)


if __name__ == "__main__":
    unittest.main()
