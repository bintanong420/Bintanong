import subprocess
import unittest
from tests.storage_database import StorageDatabase, FIXTURE


class TestStoragePublicationConcurrency(unittest.TestCase):
    def test_waiting_writer_rechecks_publication_after_commit(self):
        db = StorageDatabase()
        self.addCleanup(db.close)
        db.execute(FIXTURE + 'commit;')
        publisher = subprocess.Popen(
            ['docker', 'exec', '-i', db.container, 'psql', '-U', 'postgres', '-d', db.name,
             '-X', '-A', '-t', '-q', '-v', 'ON_ERROR_STOP=1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        def stop():
            if publisher.poll() is None:
                publisher.kill()
            publisher.communicate(timeout=15)
        self.addCleanup(stop)
        publisher.stdin.write("begin; set local role service_role; select public.activate_knowledge_release('release-test1');\n\\echo publication_uncommitted\n")
        publisher.stdin.flush()
        # The barrier proves activation completed while the transaction remains open.
        for line in publisher.stdout:
            if line.strip() == 'publication_uncommitted':
                break
        writer = subprocess.Popen(
            ['docker', 'exec', '-i', db.container, 'psql', '-U', 'postgres', '-d', db.name,
             '-X', '-A', '-t', '-q', '-v', 'ON_ERROR_STOP=1'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(writer.stdout.close)
        self.addCleanup(writer.stderr.close)
        writer.stdin.write("set application_name='bintanong_waiting_writer'; set role service_role; update public.chunks set text='corrupted' where chunk_id=repeat('a',64);\n")
        writer.stdin.close()
        # Wait on an observed advisory-lock wait, never infer it from a sleep.
        import time
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if db.json("select to_json(exists(select 1 from pg_stat_activity where datname=current_database() and application_name='bintanong_waiting_writer' and wait_event='advisory'));"):
                break
        else:
            writer.kill()
            self.fail('writer did not wait on the publication lock')
        publisher.stdin.write('commit;\n\\q\n')
        publisher.stdin.flush()
        publisher.stdin.close()
        writer.wait(timeout=15)
        output = writer.stdout.read() + writer.stderr.read()
        (db.evidence / 'concurrent-writer.out').write_text(output, encoding='utf-8')
        self.assertNotEqual(writer.returncode, 0)
        self.assertIn('Published chunks is immutable', output)
        publisher.wait(timeout=15)
        self.assertEqual(publisher.returncode, 0, publisher.stderr.read())
        publisher.stdin = None
        self.assertNotEqual(db.json("select to_json(text) from public.chunks where chunk_id=repeat('a',64);"), 'corrupted')


if __name__ == '__main__':
    unittest.main()
