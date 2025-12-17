# Bass-Senpai Development Summary

## Overview
bass-senpai is a terminal music status viewer that displays currently playing tracks with album artwork. It integrates with MPRIS-compatible media players via playerctl. **Now written in C++ for better performance and resource efficiency.**

## Architecture

### Core Modules
1. **mpris_client.cpp** - MPRIS integration via playerctl subprocess calls
2. **artwork_handler.cpp** - Album artwork downloading, caching, and rendering using stb_image
3. **terminal_ui.cpp** - Terminal UI rendering with ANSI escape sequences
4. **bass_senpai.cpp** - Main application loop and orchestration
5. **main.cpp** - CLI entry point and argument parsing

### Key Features Implemented
✅ MPRIS integration using playerctl
✅ Smart album artwork caching (hash-based, stored in ~/.cache/bass-senpai/artwork/)
✅ Unicode half-block colored text-art rendering
✅ Split-screen layout (track info left, artwork right)
✅ Animated progress bar with timestamps
✅ Efficient screen updates (only replace changed content)
✅ Graceful error handling for missing players
✅ Track change detection to avoid unnecessary updates
✅ **Proper vertical centering (fixes offset issue from previous Python version)**
✅ Dynamic terminal size adaptation

### Technical Decisions

**Language Choice:**
- C++ chosen for better performance and lower resource usage
- Standard C++17 for modern features while maintaining compatibility
- Uses standard library and minimal external dependencies

**Caching Strategy:**
- Album artwork cached using hash of URL as filename
- Cache location: ~/.cache/bass-senpai/artwork/
- Prevents re-downloading on every update cycle
- Checks if track changed before updating artwork
- Uses stb_image for image loading and resizing

**Rendering Approach:**
- Direct terminal manipulation using ANSI escape sequences
- Uses Unicode half-block (▀) with 24-bit color for text-art
- Efficient screen updates by moving cursor to home and clearing to end
- **Proper vertical centering ensures track info aligns with artwork height**
- Decorative Unicode borders around artwork (╔═╗║╚╝)

**MPRIS Integration:**
- Uses playerctl with formatted output for single subprocess call
- Parses: artist, title, album, status, position, length, artUrl
- Converts MPRIS microsecond timestamps to seconds
- Gracefully handles missing or stopped players
- Proper shell escaping to handle special characters in format strings

**Terminal Size Detection:**
- Uses ioctl(TIOCGWINSZ) for accurate terminal size
- Falls back to sensible defaults (120x30) if detection fails
- Automatically adjusts artwork size based on terminal width:
  - < 80 cols: 20x10 artwork
  - 80-119 cols: 30x15 artwork
  - ≥ 120 cols: 40x20 artwork

### Dependencies
- **Build-time:**
  - CMake 3.15+
  - C++17 compiler (GCC 8+, Clang 7+, MSVC 2019+)
  - libcurl (for HTTP downloads)
  
- **Runtime:**
  - playerctl (system package for MPRIS)
  
- **Automatic (fetched by CMake):**
  - nlohmann/json (JSON parsing, though not heavily used currently)
  - stb_image (image loading and resizing)

### Building
See [BUILD.md](BUILD.md) for detailed build instructions.

```bash
mkdir build && cd build
cmake ..
cmake --build . -j$(nproc)
./bass-senpai
```

### Testing
- Built and tested successfully on Ubuntu 24.04
- Verified with no active media player (graceful degradation)
- Command-line argument parsing (--help, --version, --interval)
- Terminal UI rendering with proper alignment

### Security
- Safe subprocess calls with proper escaping
- No secrets or sensitive data handling
- Validated HTTP downloads with error handling
- Cache directory created with appropriate permissions

## Files Structure
```
bass-senpai/
├── include/
│   ├── artwork_handler.hpp   # Artwork handling
│   ├── bass_senpai.hpp        # Main application
│   ├── mpris_client.hpp       # MPRIS integration
│   └── terminal_ui.hpp        # Terminal UI
├── src/
│   ├── artwork_handler.cpp    # Artwork implementation
│   ├── bass_senpai.cpp        # Main app implementation
│   ├── main.cpp               # Entry point
│   ├── mpris_client.cpp       # MPRIS implementation
│   └── terminal_ui.cpp        # UI implementation
├── bass_senpai/ (Python - legacy)
│   ├── __init__.py
│   ├── main.py
│   ├── mpris.py
│   ├── artwork.py
│   └── ui.py
├── tests/ (Python tests - to be updated for C++)
│   ├── __init__.py
│   └── test_bass_senpai.py
├── CMakeLists.txt            # Build configuration
├── BUILD.md                  # Build instructions
├── README.md                 # Documentation
├── LICENSE                   # MIT License
└── .gitignore               # Git ignore patterns
```

## Improvements Over Python Version

1. **Performance**: C++ offers significantly better performance and lower memory usage
2. **Resource Efficiency**: No Python interpreter overhead
3. **Startup Time**: Faster startup due to compiled binary
4. **Dependencies**: Fewer runtime dependencies (no Python packages needed)
5. **Offset Fix**: Proper vertical centering implementation fixes alignment issues
6. **Build System**: Modern CMake with automatic dependency fetching
7. **Type Safety**: Compile-time type checking catches more errors early

## Known Limitations

- Kitty graphics protocol not yet implemented (text-art only)
- Limited to Linux/Unix systems (uses POSIX APIs)
- Requires playerctl to be installed system-wide

## Future Enhancement Ideas

- Support for Kitty graphics protocol for pixel-perfect images
- Support for other terminal graphics protocols (iTerm2, sixel)
- Interactive controls (play/pause, skip)
- Multiple player support
- Configurable themes/colors
- Lyrics display
- Notification integration
- Windows/macOS compatibility
- Unit tests for C++ code

## Development Notes

- All code follows modern C++17 conventions
- Modular design for easy extension
- Comprehensive error handling
- Memory-efficient caching
- No external services required
- CMake handles all dependencies automatically
