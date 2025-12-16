"""Terminal UI for bass-senpai."""
import sys
import os
import re
from typing import Optional, Dict, Any


class TerminalUI:
    """Handles terminal display and formatting."""
    
    def __init__(self):
        self.term_width = self._get_terminal_width()
        self.term_height = self._get_terminal_height()
        self.last_output = None
        self._update_dimensions()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width."""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 120  # Default fallback
    
    def _get_terminal_height(self) -> int:
        """Get terminal height."""
        try:
            return os.get_terminal_size().lines
        except OSError:
            return 30  # Default fallback
    
    def _update_dimensions(self):
        """Update terminal dimensions and calculate layout sizes."""
        self.term_width = self._get_terminal_width()
        self.term_height = self._get_terminal_height()
        
        # Calculate artwork dimensions based on terminal size
        # For small terminals (< 80 cols), use smaller artwork
        if self.term_width < 80:
            self.artwork_width = 20
            self.artwork_height = 10
        elif self.term_width < 120:
            self.artwork_width = 30
            self.artwork_height = 15
        else:
            self.artwork_width = 40
            self.artwork_height = 20
    
    def clear_screen(self):
        """Clear the terminal screen."""
        sys.stdout.write('\x1b[2J\x1b[H')
        sys.stdout.flush()
    
    def hide_cursor(self):
        """Hide the terminal cursor."""
        sys.stdout.write('\x1b[?25l')
        sys.stdout.flush()
    
    def show_cursor(self):
        """Show the terminal cursor."""
        sys.stdout.write('\x1b[?25h')
        sys.stdout.flush()
    
    def move_cursor(self, row: int, col: int):
        """Move cursor to specific position."""
        sys.stdout.write(f'\x1b[{row};{col}H')
    
    def format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def create_progress_bar(self, position: float, length: float, width: int = 40) -> str:
        """Create an animated progress bar."""
        if length <= 0:
            percentage = 0
        else:
            percentage = min(1.0, position / length)
        
        filled = int(percentage * width)
        empty = width - filled
        
        # Stylized progress bar with colors
        bar = '━' * filled + '─' * empty
        # Add color: cyan for filled, gray for empty
        colored_bar = f"\x1b[36m{'━' * filled}\x1b[90m{'─' * empty}\x1b[0m"
        
        return colored_bar
    
    def render_track_info(self, metadata: Optional[Dict[str, Any]], artwork_width: int = 42) -> str:
        """Render track information panel."""
        # Update dimensions dynamically
        self._update_dimensions()
        
        if not metadata:
            return self._render_no_player(artwork_width)
        
        artist = metadata.get('artist', 'Unknown Artist')
        title = metadata.get('title', 'Unknown Title')
        album = metadata.get('album', 'Unknown Album')
        status = metadata.get('status', 'Stopped')
        position = metadata.get('position', 0)
        length = metadata.get('length', 0)
        
        # Calculate left panel width
        left_width = self.term_width - artwork_width - 4
        
        lines = []
        
        # Add some vertical spacing
        lines.append('')
        lines.append('')
        
        # Title (bold and colored) with decorative elements
        title_text = self._truncate(title, left_width - 8)
        lines.append(f"  ♪ \x1b[1m\x1b[35m{title_text}\x1b[0m")
        lines.append('')
        
        # Artist with icon
        artist_text = self._truncate(artist, left_width - 8)
        lines.append(f"  👤 \x1b[36m{artist_text}\x1b[0m")
        lines.append('')
        
        # Album with icon
        album_text = self._truncate(album, left_width - 8)
        lines.append(f"  💿 \x1b[90m{album_text}\x1b[0m")
        lines.append('')
        lines.append('')
        
        # Status with icon
        status_icon = self._get_status_icon(status)
        status_color = self._get_status_color(status)
        lines.append(f"  {status_color}{status_icon} {status}\x1b[0m")
        lines.append('')
        lines.append('')
        
        # Progress bar
        bar_width = min(50, left_width - 4)
        progress_bar = self.create_progress_bar(position, length, bar_width)
        lines.append(f"  {progress_bar}")
        lines.append('')
        
        # Time stamps
        current_time = self.format_time(position)
        total_time = self.format_time(length)
        time_str = f"{current_time} / {total_time}"
        lines.append(f"  \x1b[90m{time_str}\x1b[0m")
        
        return '\n'.join(lines)
    
    def _render_no_player(self, artwork_width: int) -> str:
        """Render message when no player is active."""
        left_width = self.term_width - artwork_width - 4
        
        lines = []
        lines.append('')
        lines.append('')
        lines.append('')
        lines.append('')
        lines.append(f"  \x1b[90mNo active media player found\x1b[0m")
        lines.append('')
        lines.append(f"  \x1b[90mStart playing music and run bass-senpai again\x1b[0m")
        
        return '\n'.join(lines)
    
    def _get_status_icon(self, status: str) -> str:
        """Get icon for playback status."""
        icons = {
            'Playing': '▶',
            'Paused': '⏸',
            'Stopped': '⏹'
        }
        return icons.get(status, '⏹')
    
    def _get_status_color(self, status: str) -> str:
        """Get color code for playback status."""
        colors = {
            'Playing': '\x1b[32m',  # Green
            'Paused': '\x1b[33m',   # Yellow
            'Stopped': '\x1b[31m'   # Red
        }
        return colors.get(status, '\x1b[37m')
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to fit width."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + '...'
    
    def render_split_layout(self, left_content: str, right_content: str) -> str:
        """Render split layout with left and right panels."""
        left_lines = left_content.split('\n')
        right_lines = right_content.split('\n')
        
        # Pad to same height
        max_height = max(len(left_lines), len(right_lines))
        while len(left_lines) < max_height:
            left_lines.append('')
        while len(right_lines) < max_height:
            right_lines.append('')
        
        # Calculate widths dynamically
        # Right panel width based on artwork width plus padding
        artwork_width = self.artwork_width + 2
        left_width = self.term_width - artwork_width - 2
        
        output = []
        for left, right in zip(left_lines, right_lines):
            # Strip ANSI codes for length calculation
            left_visible = self._strip_ansi(left)
            right_visible = self._strip_ansi(right)
            
            # Pad left to fill width
            left_padding = left_width - len(left_visible)
            if left_padding > 0:
                left_padded = left + ' ' * left_padding
            else:
                left_padded = left
            
            output.append(left_padded + '  ' + right)
        
        return '\n'.join(output)
    
    def _strip_ansi(self, text: str) -> str:
        """Strip ANSI escape codes for length calculation."""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKHfJ]|\x1b_G[^\\]*\x1b\\')
        return ansi_escape.sub('', text)
    
    def display(self, content: str):
        """Display content, replacing previous output efficiently."""
        # Move to home position
        sys.stdout.write('\x1b[H')
        
        # Write content
        sys.stdout.write(content)
        
        # Clear to end of screen
        sys.stdout.write('\x1b[J')
        
        sys.stdout.flush()
        
        self.last_output = content
