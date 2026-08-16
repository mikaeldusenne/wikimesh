import runpy
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from backend.src import db


MONGO_ENV = {
    "MONGO_HOST": "mongo",
    "MONGO_INITDB_DATABASE": "wikimesh",
    "MONGO_INITDB_ROOT_USERNAME": "root",
    "MONGO_INITDB_ROOT_PASSWORD": "secret",
}


class LazyMongoTest(unittest.TestCase):
    def setUp(self):
        self.state = db.client, db.db, db._credentials
        db.client = db.db = db._credentials = None

    def tearDown(self):
        db.client, db.db, db._credentials = self.state

    @patch.dict(db.environ, MONGO_ENV, clear=False)
    @patch("backend.src.db.MongoClient")
    def test_default_connection_is_reused(self, mongo_client):
        database = MagicMock()
        mongo_client.return_value.__getitem__.return_value = database

        self.assertIs(db.connect(), database)
        self.assertIs(db.connect(), database)
        mongo_client.assert_called_once()

    @patch.dict(db.environ, MONGO_ENV, clear=False)
    @patch("backend.src.db.MongoClient")
    def test_explicit_credential_change_reconnects(self, mongo_client):
        mongo_client.return_value.__getitem__.return_value = MagicMock()
        db.connect("alice", "one")
        db.connect("bob", "two")
        self.assertEqual(mongo_client.call_count, 2)


class DataToolCompatibilityTest(unittest.TestCase):
    @patch("backend.src.db.connect")
    def test_mesh_parser_import_has_no_db_side_effect(self, connect):
        runpy.run_module("backend.src.mesh_parser", run_name="mesh_parser_import_test")
        connect.assert_not_called()

    def test_mesh_parser_keeps_existing_cli(self):
        csv = "id,lang,label,type_label\nD1,en,Heart,pt\nD1,en,Cardiac,syn\n"
        database = MagicMock()
        database.mesh.count_documents.return_value = 1

        with tempfile.NamedTemporaryFile("w", suffix=".csv") as source:
            source.write(csv)
            source.flush()
            argv = ["mesh_parser", "-f", "-i", "MeSH", source.name]
            with patch.object(sys, "argv", argv), \
                 patch("backend.src.db.connect") as connect, \
                 patch.object(db, "db", database):
                runpy.run_module("backend.src.mesh_parser", run_name="__main__")

        connect.assert_called_once_with()
        database.mesh.insert_one.assert_called_once()


if __name__ == "__main__":
    unittest.main()
