import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from clean_transcript import clean  # noqa: E402


class CleanTranscriptTests(unittest.TestCase):
    def test_clean_removes_timestamps_tags_and_duplicate_fragments(self):
        raw = """WEBVTT
Kind: captions
Language: en

00:00:01.000 --> 00:00:02.000
<c>Hello</c>

1
00:00:02,000 --> 00:00:03,000
Hello
World
World
"""
        cleaned = clean(raw)
        self.assertEqual(cleaned, "Hello\nWorld\n")


if __name__ == "__main__":
    unittest.main()
