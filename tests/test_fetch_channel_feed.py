import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_channel_feed import parse_feed, positive_int  # noqa: E402


class FetchChannelFeedTests(unittest.TestCase):
    def test_parse_feed_extracts_channel_and_video_fields(self):
        xml = b"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'
      xmlns:yt='http://www.youtube.com/xml/schemas/2015'
      xmlns:media='http://search.yahoo.com/mrss/'>
  <title>Example Channel</title>
  <entry>
    <yt:videoId>abc123</yt:videoId>
    <title>Video A</title>
    <published>2026-01-01T00:00:00+00:00</published>
    <updated>2026-01-01T00:00:00+00:00</updated>
    <link rel='alternate' href='https://www.youtube.com/watch?v=abc123'/>
    <media:group>
      <media:description>Desc A</media:description>
    </media:group>
  </entry>
</feed>
"""
        parsed = parse_feed(xml, limit=10)
        self.assertEqual(parsed["channel_title"], "Example Channel")
        self.assertEqual(len(parsed["videos"]), 1)
        self.assertEqual(parsed["videos"][0]["video_id"], "abc123")
        self.assertEqual(parsed["videos"][0]["title"], "Video A")
        self.assertEqual(parsed["videos"][0]["description"], "Desc A")

    def test_positive_int_rejects_zero_or_negative(self):
        with self.assertRaises(Exception):
            positive_int("0")
        with self.assertRaises(Exception):
            positive_int("-1")
        self.assertEqual(positive_int("3"), 3)


if __name__ == "__main__":
    unittest.main()
