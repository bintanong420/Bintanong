"""Production loader integration tests using disposable PostgreSQL databases."""

import json
from pathlib import Path
import unittest

from backend.bintanong_storage.client import StorageError
from backend.bintanong_storage.loader import BatchKnowledgeLoader
from backend.bintanong_storage.release import ReleaseManager
from backend.bintanong_contracts.source import compute_content_hash
from tests.storage_database import DatabaseStorageClient, FIXTURE, StorageDatabase


class TestBatchKnowledgeLoaderIdempotency(unittest.TestCase):
    def setUp(self):
        self.db = StorageDatabase()
        self.addCleanup(self.db.close)
        self.db.execute(FIXTURE + "commit;")
        self.client = DatabaseStorageClient(self.db)
        self.loader = BatchKnowledgeLoader(self.client)
        self.chunks = self.client.select("chunks", role="admin")
        for chunk in self.chunks:
            chunk["spans"] = self.client.select("source_spans", filters={"chunk_id": "eq." + chunk["chunk_id"]}, role="admin")
        cfg = self.client.select("embedding_sets", role="admin")[0]
        self.manifest = {**cfg, "total_embedded_records": 2}
        self.embeddings = [{"chunk_id": row["chunk_id"], "chunk_content_hash": row["chunk_content_hash"],
                            "vector": json.loads(row["embedding"]), "token_count": row["token_count"]}
                           for row in self.client.select("chunk_embeddings", role="admin")]

    def test_idempotent_import_preserves_counts_and_span_identities(self):
        original_ids = {s["span_id"] for s in self.client.select("source_spans", role="admin")}
        for _ in range(2):
            self.assertEqual(self.loader.load_embedding_manifest(self.manifest), "set-test")
            self.assertEqual(self.loader.load_chunks(self.chunks), 2)
            self.assertEqual(self.loader.load_embeddings(self.embeddings, "set-test"), 2)
        self.assertEqual(len(self.client.select("chunks", role="admin")), 2)
        self.assertEqual(len(self.client.select("chunk_embeddings", role="admin")), 2)
        self.assertEqual({s["span_id"] for s in self.client.select("source_spans", role="admin")}, original_ids)

    def test_published_reimport_is_unchanged_and_conflicts_fail(self):
        ReleaseManager(self.client).activate_release("release-test1")
        original_spans = self.client.select("source_spans", role="admin")
        self.loader.load_embedding_manifest(self.manifest)
        self.loader.load_chunks(self.chunks)
        self.loader.load_embeddings(self.embeddings, "set-test")
        self.assertEqual(self.client.select("source_spans", role="admin"), original_spans)
        bad = {**self.chunks[0], "text": "Changed content under an existing identity"}
        bad["content_hash"] = compute_content_hash(bad["source_text"], bad["text"])
        with self.assertRaisesRegex(StorageError, "identity conflicts"):
            self.loader.load_chunks([bad])
        self.assertNotEqual(self.client.select("chunks", role="runtime")[0]["text"], bad["text"])

    def test_failed_span_replacement_rolls_back_every_change(self):
        prior = self.client.select("source_spans", role="admin")
        records, spans = self.loader._chunk_records(self.chunks)
        spans[0]["page"] = "not-an-integer"
        with self.assertRaisesRegex(StorageError, "invalid input syntax"):
            self.client.rpc("load_chunk_batch", {"p_chunks": records, "p_spans": spans}, role="admin")
        self.assertEqual(self.client.select("source_spans", role="admin"), prior)

    def test_manifest_binds_all_configuration_fields(self):
        first = BatchKnowledgeLoader._manifest_record({k: v for k, v in self.manifest.items() if k != "embedding_set_id"}, self.embeddings)
        second = BatchKnowledgeLoader._manifest_record({k: v for k, v in {**self.manifest, "model_revision": "f" * 64}.items() if k != "embedding_set_id"}, self.embeddings)
        self.assertNotEqual(first["embedding_set_id"], second["embedding_set_id"])
        with self.assertRaises(StorageError):
            self.loader.load_embedding_manifest({**self.manifest, "model_revision": "f" * 64})

    def test_vector_and_configuration_validation_precede_writes(self):
        for bad in ([0.0] * 1024, [float("nan")] + [0.0] * 1023, [1.0], [True] + [0.0] * 1023):
            with self.subTest(vector=repr(bad[:1])), self.assertRaises(ValueError):
                self.loader.load_embeddings([{**self.embeddings[0], "vector": bad}], "set-test")
        with self.assertRaises(ValueError):
            self.loader.load_embeddings([{**self.embeddings[0], "model_revision": "f" * 64}], "set-test")
        self.assertEqual(len(self.client.select("chunk_embeddings", role="admin")), 2)

    def test_dictionary_content_and_source_locations_are_validated(self):
        malformed = [
            {**self.chunks[0], "text": "stale content"},
            {**self.chunks[0], "schema_version": "unknown-chunk-v9"},
            {**self.chunks[0], "spans": [{**self.chunks[0]["spans"][0], "page": None}]},
            {**self.chunks[0], "spans": [{**self.chunks[0]["spans"][0], "locator": {"kind": "table_cells"}}]},
            {**self.chunks[0], "spans": [{**self.chunks[0]["spans"][0], "text": "Different source"}]},
            {k: v for k, v in {**self.chunks[0], "spans": [{**self.chunks[0]["spans"][0], "text": "Different source"}]}.items() if k != "source_text"},
        ]
        for chunk in malformed:
            with self.subTest(chunk=chunk["text"]), self.assertRaises(ValueError):
                self.loader.load_chunks([chunk])
        self.assertEqual(len(self.client.select("chunks", role="admin")), 2)

    def test_textless_table_spans_remain_valid(self):
        table = {**self.chunks[0], "chunk_id": "e" * 64, "chunk_type": "curriculum_table", "source_text": None,
                 "spans": [{**self.chunks[0]["spans"][0], "text": None}]}
        table["content_hash"] = compute_content_hash(None, table["text"])
        self.loader.load_chunks([table])
        self.loader.load_embedding_manifest({**self.manifest, "total_embedded_records": 3})
        self.loader.load_embeddings([{**self.embeddings[0], "chunk_id": table["chunk_id"]}], "set-test")
        manager = ReleaseManager(self.client)
        manager.create_release("table-release", "table", "Synthetic", "set-test", [table["chunk_id"]], [table["version_id"]])
        manager.activate_release("table-release")

    def test_existing_identity_cannot_change_source_text_nullability(self):
        textless = {**self.chunks[0], "source_text": None,
                    "spans": [{**self.chunks[0]["spans"][0], "text": None}]}
        with self.assertRaisesRegex(StorageError, "identity conflicts"):
            self.loader.load_chunks([textless])

    def test_automatic_set_identity_supports_changed_corpus_after_publication(self):
        manifest = {k: v for k, v in self.manifest.items() if k != "embedding_set_id"}
        manifest_path, records_path = self.db.evidence / "auto-manifest.json", self.db.evidence / "auto-records.jsonl"
        def load(records, chunks):
            manifest_path.write_text(json.dumps({**manifest, "total_embedded_records": len(records)}), encoding="utf-8")
            records_path.write_text("\n".join(json.dumps(row) for row in records), encoding="utf-8")
            return self.loader.load_artifacts(manifest_path, records_path, chunks).embedding_set_id
        first = load(self.embeddings[:1], self.chunks[:1])
        manager = ReleaseManager(self.client)
        manager.create_release("auto-first", "auto-first", "Synthetic", first, [self.chunks[0]["chunk_id"]], [self.chunks[0]["version_id"]])
        manager.activate_release("auto-first")
        second = load(self.embeddings, self.chunks)
        self.assertNotEqual(first, second)
        self.assertEqual(load(list(reversed(self.embeddings)), list(reversed(self.chunks))), second)
        self.assertEqual(load(self.embeddings[:1], self.chunks[:1]), first)
        with self.assertRaisesRegex(ValueError, "full embedding artifact"):
            self.loader.load_embedding_manifest(manifest)

    def test_artifact_import_reports_actual_duplicates_and_is_atomic(self):
        manifest_path = self.db.evidence / "manifest.json"
        records_path = self.db.evidence / "embeddings.jsonl"
        manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        records_path.write_text("\n".join(json.dumps(row) for row in self.embeddings), encoding="utf-8")
        result = self.loader.load_artifacts(manifest_path, records_path, self.chunks)
        self.assertEqual((result.total_chunks_loaded, result.total_embeddings_loaded, result.total_spans_loaded,
                          result.duplicate_avoided_count), (2, 2, 2, 2))
        bad_manifest = {**self.manifest, "embedding_set_id": "set-must-not-persist"}
        manifest_path.write_text(json.dumps(bad_manifest), encoding="utf-8")
        # Pass Python validation, then fail the SQL hash binding: the new set must roll back too.
        bad_records = [{**row, "chunk_content_hash": "f" * 64} for row in self.embeddings]
        records_path.write_text("\n".join(json.dumps(row) for row in bad_records), encoding="utf-8")
        with self.assertRaises(StorageError):
            self.loader.load_artifacts(manifest_path, records_path)
        self.assertEqual(self.client.select("embedding_sets", filters={"embedding_set_id": "eq.set-must-not-persist"}, role="admin"), [])


if __name__ == "__main__":
    unittest.main()
