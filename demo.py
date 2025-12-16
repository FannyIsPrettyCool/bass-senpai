#!/usr/bin/env python3
"""Demo script to show bass-senpai UI with mock data."""
import sys
from bass_senpai.ui import TerminalUI
from bass_senpai.artwork import ArtworkHandler


def main():
    """Run demo with mock track data."""
    ui = TerminalUI()
    artwork = ArtworkHandler()
    
    # Mock metadata
    metadata = {
        'artist': 'Lo-Fi Beats Orchestra',
        'title': 'Midnight Study Session',
        'album': 'Chill Vibes Vol. 3',
        'status': 'Playing',
        'position': 145.7,
        'length': 242.0,
        'art_url': None
    }
    
    print("\n" + "="*80)
    print("BASS-SENPAI DEMO - Mock Track Display")
    print("="*80 + "\n")
    
    # Render track info
    artwork_width = 42  # 40 char width + 2 for padding
    left_panel = ui.render_track_info(metadata, artwork_width)
    
    # Render placeholder artwork (no actual image)
    right_panel = artwork._render_placeholder(40, 20)
    
    # Combine panels
    combined = ui.render_split_layout(left_panel, right_panel)
    
    # Add header
    header = "\n  \x1b[1m\x1b[35mbass-senpai\x1b[0m\n  \x1b[90m" + "─" * ui.term_width + "\x1b[0m"
    full_output = header + '\n\n' + combined
    
    print(full_output)
    
    print("\n" + "="*80)
    print("This is how bass-senpai displays track information.")
    print("With a real media player, it would show actual album artwork!")
    print("="*80 + "\n")
    
    # Show different statuses
    print("\nDifferent playback statuses:")
    print("-" * 40)
    
    for status in ['Playing', 'Paused', 'Stopped']:
        metadata['status'] = status
        icon = ui._get_status_icon(status)
        color = ui._get_status_color(status)
        print(f"  {color}{icon} {status}\x1b[0m")
    
    print("\nProgress bar animation:")
    print("-" * 40)
    for i in range(0, 101, 20):
        bar = ui.create_progress_bar(i, 100, 40)
        print(f"  {i:3d}% {bar}")
    
    print("\nTime formatting examples:")
    print("-" * 40)
    for seconds in [0, 61, 125, 3661]:
        formatted = ui.format_time(seconds)
        print(f"  {seconds:5d} seconds = {formatted}")
    
    print()


if __name__ == '__main__':
    main()
