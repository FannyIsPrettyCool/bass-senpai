"""Unit tests for bass-senpai components."""
import unittest
import tempfile
from pathlib import Path
from bass_senpai.mpris import MPRISClient
from bass_senpai.artwork import ArtworkHandler
from bass_senpai.ui import TerminalUI


class TestMPRISClient(unittest.TestCase):
    """Test MPRIS client functionality."""
    
    def test_client_initialization(self):
        """Test that MPRIS client can be initialized."""
        client = MPRISClient()
        self.assertIsInstance(client, MPRISClient)
        # playerctl_available may be True or False depending on system
        self.assertIsInstance(client.playerctl_available, bool)
    
    def test_get_metadata_returns_dict_or_none(self):
        """Test that get_metadata returns dict or None."""
        client = MPRISClient()
        metadata = client.get_metadata()
        # Should return None when no player is active, or dict when player is active
        self.assertTrue(metadata is None or isinstance(metadata, dict))
    
    def test_get_playback_status_returns_string(self):
        """Test that get_playback_status returns a string."""
        client = MPRISClient()
        status = client.get_playback_status()
        self.assertIsInstance(status, str)


class TestArtworkHandler(unittest.TestCase):
    """Test artwork handler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "cache"
        self.handler = ArtworkHandler(cache_dir=self.cache_dir)
    
    def test_handler_initialization(self):
        """Test that artwork handler can be initialized."""
        self.assertIsInstance(self.handler, ArtworkHandler)
        self.assertTrue(self.cache_dir.exists())
    
    def test_get_artwork_none_url(self):
        """Test that get_artwork handles None URL."""
        result = self.handler.get_artwork(None)
        self.assertIsNone(result)
    
    def test_placeholder_rendering(self):
        """Test that placeholder can be rendered."""
        placeholder = self.handler._render_placeholder(40, 20)
        self.assertIsInstance(placeholder, str)
        self.assertIn("No Artwork", placeholder)
    
    def test_kitty_detection(self):
        """Test Kitty terminal detection."""
        # Should return boolean
        self.assertIsInstance(self.handler.is_kitty, bool)


class TestTerminalUI(unittest.TestCase):
    """Test terminal UI functionality."""
    
    def test_ui_initialization(self):
        """Test that terminal UI can be initialized."""
        ui = TerminalUI()
        self.assertIsInstance(ui, TerminalUI)
        self.assertGreater(ui.term_width, 0)
        self.assertGreater(ui.term_height, 0)
    
    def test_format_time(self):
        """Test time formatting."""
        ui = TerminalUI()
        self.assertEqual(ui.format_time(0), "00:00")
        self.assertEqual(ui.format_time(61), "01:01")
        self.assertEqual(ui.format_time(125), "02:05")
        self.assertEqual(ui.format_time(3661), "61:01")
    
    def test_create_progress_bar(self):
        """Test progress bar creation."""
        ui = TerminalUI()
        bar = ui.create_progress_bar(30, 100, 40)
        self.assertIsInstance(bar, str)
        # Progress bar should contain characters
        self.assertGreater(len(bar), 0)
    
    def test_render_track_info_none(self):
        """Test rendering with no metadata."""
        ui = TerminalUI()
        result = ui.render_track_info(None, 42)
        self.assertIsInstance(result, str)
        self.assertIn("No active media player", result)
    
    def test_render_track_info_with_metadata(self):
        """Test rendering with metadata."""
        ui = TerminalUI()
        metadata = {
            'artist': 'Test Artist',
            'title': 'Test Title',
            'album': 'Test Album',
            'status': 'Playing',
            'position': 30.0,
            'length': 200.0
        }
        result = ui.render_track_info(metadata, 42)
        self.assertIsInstance(result, str)
        self.assertIn('Test Artist', result)
        self.assertIn('Test Title', result)


if __name__ == '__main__':
    unittest.main()
