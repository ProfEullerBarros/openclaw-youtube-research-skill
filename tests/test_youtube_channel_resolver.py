import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from youtube_channel_resolver import resolve_channel_id, validate_youtube_target  # noqa: E402


class YouTubeChannelResolverTests(unittest.TestCase):
    def test_validate_rejects_non_youtube_url(self):
        ok, reason = validate_youtube_target("https://example.com/channel")
        self.assertFalse(ok)
        self.assertIn("only YouTube URLs", reason)

    @patch("youtube_channel_resolver.yt_dlp_path", return_value="/home/test/.local/bin/yt-dlp")
    @patch("youtube_channel_resolver.subprocess.run")
    def test_resolve_channel_id_success(self, mock_run, _mock_yt_dlp):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="UC123\tExample Channel\thttps://www.youtube.com/channel/UC123\n",
            stderr="",
        )
        resolved = resolve_channel_id("@Example")
        self.assertTrue(resolved["ok"])
        self.assertEqual(resolved["channel_id"], "UC123")

    @patch("youtube_channel_resolver.yt_dlp_path", return_value="/home/test/.local/bin/yt-dlp")
    @patch("youtube_channel_resolver.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["yt-dlp"], timeout=45))
    def test_resolve_channel_id_timeout(self, _mock_run, _mock_yt_dlp):
        resolved = resolve_channel_id("@Example")
        self.assertFalse(resolved["ok"])
        self.assertGreaterEqual(len(resolved["attempts"]), 1)
        self.assertIn("timeout", resolved["attempts"][0]["stderr"])


if __name__ == "__main__":
    unittest.main()
