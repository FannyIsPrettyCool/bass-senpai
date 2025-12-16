"""Main application for bass-senpai."""
import sys
import time
import signal
from typing import Optional
from .mpris import MPRISClient
from .artwork import ArtworkHandler
from .ui import TerminalUI


class BassSenpai:
    """Main application class for bass-senpai."""
    
    def __init__(self, update_interval: float = 1.0):
        """Initialize bass-senpai.
        
        Args:
            update_interval: Time in seconds between updates
        """
        self.update_interval = update_interval
        self.mpris = MPRISClient()
        self.artwork = ArtworkHandler()
        self.ui = TerminalUI()
        self.running = False
        self.last_track_id = None
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.running = False
    
    def _get_track_id(self, metadata: Optional[dict]) -> Optional[str]:
        """Generate unique ID for current track."""
        if not metadata:
            return None
        
        artist = metadata.get('artist', '')
        title = metadata.get('title', '')
        album = metadata.get('album', '')
        
        return f"{artist}|{title}|{album}"
    
    def run(self):
        """Run the main application loop."""
        if not self.mpris.playerctl_available:
            print("Error: playerctl is not available.")
            print("Please install playerctl to use bass-senpai.")
            print("\nOn Ubuntu/Debian: sudo apt install playerctl")
            print("On Arch Linux: sudo pacman -S playerctl")
            print("On macOS: brew install playerctl")
            return 1
        
        # Initialize terminal
        self.ui.clear_screen()
        self.ui.hide_cursor()
        
        self.running = True
        
        try:
            while self.running:
                self._update()
                time.sleep(self.update_interval)
        
        except KeyboardInterrupt:
            pass
        
        finally:
            # Cleanup
            self.ui.show_cursor()
            self.ui.clear_screen()
            print("\nBass-senpai stopped.")
        
        return 0
    
    def _update(self):
        """Update display with current track information."""
        # Get current metadata
        metadata = self.mpris.get_metadata()
        
        # Determine if track changed
        track_id = self._get_track_id(metadata)
        track_changed = track_id != self.last_track_id
        
        if track_changed:
            self.last_track_id = track_id
        
        # Render left panel (track info)
        left_panel = self.ui.render_track_info(metadata)
        
        # Render right panel (artwork)
        art_url = metadata.get('art_url') if metadata else None
        artwork_height = 20
        artwork_width = 40
        
        # Only update artwork if track changed or no artwork cached
        right_panel = self.artwork.render(art_url, artwork_width, artwork_height)
        
        # Combine panels
        combined = self.ui.render_split_layout(left_panel, right_panel)
        
        # Add header
        header = self._render_header()
        full_output = header + '\n\n' + combined
        
        # Display
        self.ui.display(full_output)
    
    def _render_header(self) -> str:
        """Render application header."""
        title = "bass-senpai"
        # Stylized title with colors
        styled_title = f"\x1b[1m\x1b[35m{title}\x1b[0m"
        
        separator = '─' * self.ui.term_width
        
        return f"\n  {styled_title}\n  \x1b[90m{separator}\x1b[0m"


def main():
    """Entry point for bass-senpai command."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='bass-senpai - Terminal music status viewer with album artwork',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bass-senpai              Start with default 1 second update interval
  bass-senpai --interval 2  Update every 2 seconds

Requirements:
  - playerctl must be installed for MPRIS support
  - Kitty terminal recommended for pixel-perfect album artwork
  - Falls back to colored text-art in other terminals
        """
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Update interval in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='bass-senpai 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate interval
    if args.interval < 0.1:
        print("Error: Update interval must be at least 0.1 seconds")
        return 1
    
    # Create and run application
    app = BassSenpai(update_interval=args.interval)
    return app.run()


if __name__ == '__main__':
    sys.exit(main())
