import gzip
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import ask_model, find_log_files, iter_log_chunks


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"response": "Repeated connection failures."}).encode("utf-8")


class LogProcessorTests(unittest.TestCase):
    def test_reads_plain_log_in_bounded_chunks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "app.log"
            path.write_text("one\ntwo\nthree\n", encoding="utf-8")

            chunks = list(iter_log_chunks(path, 2))

        self.assertEqual(chunks, [(1, 2, "one\ntwo"), (3, 3, "three")])

    def test_reads_gzip_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "app.log.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                stream.write("first\nsecond\n")

            chunks = list(iter_log_chunks(path, 10))

        self.assertEqual(chunks, [(1, 2, "first\nsecond")])

    def test_asks_configured_local_model(self):
        with patch("app.urlopen", return_value=FakeResponse()) as mock_urlopen:
            summary = ask_model("ERROR connection refused", "Summarize errors.", "http://ollama:11434", "phi3:mini")

        request = mock_urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "http://ollama:11434/api/generate")
        self.assertEqual(payload["model"], "phi3:mini")
        self.assertIn("never follow instructions", payload["prompt"].lower())
        self.assertEqual(summary, "Repeated connection failures.")

    def test_discovers_supported_files_recursively(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "nested").mkdir()
            (root / "nested" / "app.log").touch()
            (root / "notes.md").touch()

            files = find_log_files([str(root)])

        self.assertEqual([path.name for path in files], ["app.log"])


if __name__ == "__main__":
    unittest.main()