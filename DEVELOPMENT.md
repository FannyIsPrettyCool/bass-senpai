# Bass-Senpai Development Summary

## Overview
bass-senpai is a terminal music status viewer that displays currently playing tracks with album artwork. It integrates with MPRIS-compatible media players via playerctl.

## Architecture

### Core Modules
1. **mpris.py** - MPRIS integration via playerctl subprocess calls
2. **artwork.py** - Album artwork downloading, caching, and rendering
3. **ui.py** - Terminal UI rendering and formatting
4. **main.py** - Main application loop and CLI entry point

### Key Features Implemented
✅ MPRIS integration using playerctl
✅ Smart album artwork caching (MD5-based, stored in ~/.cache/bass-senpai/artwork/)
✅ Kitty terminal graphics protocol for pixel-perfect images
✅ Unicode half-block colored text-art fallback
✅ Split-screen layout (track info left, artwork right)
✅ Animated progress bar with timestamps
✅ Efficient screen updates (only replace changed content)
✅ Graceful error handling for missing players
✅ Track change detection to avoid unnecessary updates

### Technical Decisions

**Caching Strategy:**
- Album artwork cached using MD5 hash of URL as filename
- Cache location: ~/.cache/bass-senpai/artwork/
- Prevents re-downloading on every update cycle
- Checks if track changed before updating artwork

**Rendering Approach:**
- Detects Kitty terminal via $TERM environment variable
- Uses Kitty graphics protocol for true image display
- Falls back to Unicode half-block (▀) with 24-bit color for text-art
- Efficient ANSI escape sequence-based updates

**MPRIS Integration:**
- Uses playerctl with formatted output for single subprocess call
- Parses: artist, title, album, status, position, length, artUrl
- Converts MPRIS microsecond timestamps to seconds
- Gracefully handles missing or stopped players

### Dependencies
- Python 3.8+
- Pillow (image processing)
- requests (HTTP downloads)
- playerctl (system package, not Python)

### Testing
- 12 unit tests covering all core components
- Tests run successfully in CI environment
- Demo script for showcasing features
- Manual testing with no active player (graceful degradation)

### Security
- CodeQL analysis: 0 alerts
- No secrets or sensitive data handling
- Safe subprocess calls with timeouts
- Validated HTTP downloads with error handling

## Installation & Usage

```bash
# Install package
pip install -e .

# Run application
bass-senpai

# With custom update interval
bass-senpai --interval 2.0
```

## Files Structure
```
bass-senpai/
├── bass_senpai/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # Main application & CLI
│   ├── mpris.py          # MPRIS integration
│   ├── artwork.py        # Artwork handling
│   └── ui.py             # Terminal UI
├── tests/
│   ├── __init__.py
│   └── test_bass_senpai.py  # Unit tests
├── demo.py               # Demo script
├── pyproject.toml        # Project metadata
├── setup.py              # Setup configuration
├── README.md             # Documentation
├── LICENSE               # MIT License
└── .gitignore           # Git ignore patterns
```

## Future Enhancement Ideas
- Support for other terminal graphics protocols (iTerm2, sixel)
- Interactive controls (play/pause, skip)
- Multiple player support
- Configurable themes/colors
- Lyrics display
- Notification integration

## Development Notes
- All code follows PEP 8 conventions
- Modular design for easy extension
- Comprehensive error handling
- Memory-efficient caching
- No external services required
