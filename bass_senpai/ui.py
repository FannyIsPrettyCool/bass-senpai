"""Terminal UI for bass-senpai."""
import sys
import os
import re
import unicodedata
from typing import Optional, Dict, Any, List

# Constants
ARTWORK_BORDER_HEIGHT = 2  # Total height for top and bottom borders combined


class TerminalUI:
    """Handles terminal display and formatting."""
    
    def __init__(self):
        self.term_width = self._get_terminal_width()
        self.term_height = self._get_terminal_height()
        self.last_output = None
        # Calculate initial artwork size
        self._calculate_artwork_size()
    
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
        self._calculate_artwork_size()
    
    def _calculate_artwork_size(self):
        """Calculate artwork dimensions based on current terminal size."""
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
    
    def _center_content_vertically(self, content_lines: List[str]) -> str:
        """Center content vertically to match artwork height.
        
        Args:
            content_lines: List of content lines to center
            
        Returns:
            Vertically centered content as a single string
        """
        # Calculate vertical centering to match artwork height
        # Artwork has artwork_height + ARTWORK_BORDER_HEIGHT total lines
        target_height = self.artwork_height + ARTWORK_BORDER_HEIGHT
        content_height = len(content_lines)
        
        # Calculate padding needed to center content
        total_padding = max(0, target_height - content_height)
        top_padding = total_padding // 2
        bottom_padding = total_padding - top_padding
        
        # Build final lines with vertical centering
        lines = []
        for _ in range(top_padding):
            lines.append('')
        lines.extend(content_lines)
        for _ in range(bottom_padding):
            lines.append('')
        
        return '\n'.join(lines)
    
    def render_track_info(self, metadata: Optional[Dict[str, Any]], artwork_width: int = 42) -> str:
        """Render track information panel."""
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
        
        # Build content lines (without vertical padding)
        content_lines = []
        
        # Title (bold and colored) with decorative elements
        title_text = self._truncate(title, left_width - 8)
        content_lines.append(f"  ♪ \x1b[1m\x1b[35m{title_text}\x1b[0m")
        content_lines.append('')
        
        # Artist with icon
        artist_text = self._truncate(artist, left_width - 8)
        content_lines.append(f"  👤 \x1b[36m{artist_text}\x1b[0m")
        content_lines.append('')
        
        # Album with icon
        album_text = self._truncate(album, left_width - 8)
        content_lines.append(f"  💿 \x1b[90m{album_text}\x1b[0m")
        content_lines.append('')
        content_lines.append('')
        
        # Status with icon
        status_icon = self._get_status_icon(status)
        status_color = self._get_status_color(status)
        content_lines.append(f"  {status_color}{status_icon} {status}\x1b[0m")
        content_lines.append('')
        content_lines.append('')
        
        # Progress bar
        bar_width = min(50, left_width - 4)
        progress_bar = self.create_progress_bar(position, length, bar_width)
        content_lines.append(f"  {progress_bar}")
        content_lines.append('')
        
        # Time stamps
        current_time = self.format_time(position)
        total_time = self.format_time(length)
        time_str = f"{current_time} / {total_time}"
        content_lines.append(f"  \x1b[90m{time_str}\x1b[0m")
        
        # Center content vertically to match artwork height
        return self._center_content_vertically(content_lines)
    
    def _render_no_player(self, artwork_width: int) -> str:
        """Render message when no player is active."""
        left_width = self.term_width - artwork_width - 4
        
        # Build content lines
        content_lines = []
        content_lines.append(f"  \x1b[90mNo active media player found\x1b[0m")
        content_lines.append('')
        content_lines.append(f"  \x1b[90mStart playing music and run bass-senpai again\x1b[0m")
        
        # Center content vertically to match artwork height
        return self._center_content_vertically(content_lines)
    
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
            # Calculate actual display width (accounting for wide characters like emojis)
            left_visible_width = self._display_width(left)
            
            # Pad left to fill width
            left_padding = left_width - left_visible_width
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
    
    def _display_width(self, text: str) -> int:
        """Calculate the actual display width of text, accounting for wide characters.
        
        Wide characters (like emojis) take 2 terminal columns.
        """
        # First strip ANSI codes
        clean_text = self._strip_ansi(text)
        
        width = 0
        for char in clean_text:
            # Check if character is wide (emoji, CJK characters, etc.)
            # East Asian Width property: 'F' (Fullwidth), 'W' (Wide)
            ea_width = unicodedata.east_asian_width(char)
            if ea_width in ('F', 'W'):
                width += 2
            # Emoji modifier and variation selectors are often zero-width
            elif unicodedata.category(char) in ('Mn', 'Me', 'Cf'):
                # Mark, Nonspacing; Mark, Enclosing; Other, Format
                width += 0
            else:
                width += 1
        
        return width
    
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
