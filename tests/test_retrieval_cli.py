from contextlib import redirect_stdout, redirect_stderr
import io
import json
import unittest
from unittest.mock import patch

from backend.bintanong_retrieval.cli import main
from tests.test_retrieval_engine import Client, Encoder


class CliTests(unittest.TestCase):
    def test_debug_command_emits_json_using_runtime_client(self):
        output=io.StringIO()
        with patch('backend.bintanong_retrieval.cli.SupabaseStorageClient',return_value=Client()), \
             patch('backend.bintanong_retrieval.cli.QueryEncoder',return_value=Encoder()), redirect_stdout(output):
            code=main(['--query','hello','--release-id','release-test','--context-budget','1000'])
        result=json.loads(output.getvalue())
        self.assertEqual(code,2)
        self.assertEqual(result['status'],'uncalibrated')
        self.assertTrue(result['evidence'])

    def test_invalid_top_k_rejected_before_connecting(self):
        with patch('backend.bintanong_retrieval.cli.SupabaseStorageClient') as client:
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(['--query','hello','--release-id','release-test','--top-k','4'])
            client.assert_not_called()
