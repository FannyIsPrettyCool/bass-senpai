# bass-senpai 🎵

A stylized terminal music status viewer that displays currently playing tracks with album artwork. Designed to be beautiful, responsive, and lightweight.

![bass-senpai demo](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🎵 **Real-time track information**: Display artist, title, album, and playback status with live updates
- 🎨 **Album artwork display**: 
  - Pixel-perfect images in Kitty terminal using the Kitty graphics protocol
  - Beautiful colored text-art fallback for other terminals using Unicode half-blocks
  - Decorative borders around artwork
- 📊 **Animated progress bar**: Visual representation of current playback position
- 📐 **Dynamic resizing**: Automatically adapts to terminal size changes
  - Small terminals (< 80 cols): 20x10 artwork
  - Medium terminals (80-119 cols): 30x15 artwork
  - Large terminals (≥ 120 cols): 40x20 artwork
- ⚡ **Efficient updates**: Only refreshes changed content to prevent stuttering
- 💾 **Smart caching**: Downloads album artwork once and caches it locally
- 🎮 **MPRIS support**: Works with any MPRIS-compatible media player via playerctl
- 🎨 **Unicode decorations**: Beautiful icons and symbols for enhanced visual appeal

## 📋 Requirements

- **Python 3.8 or higher**
- **playerctl** - for MPRIS integration with media players
- A running media player that supports MPRIS (Spotify, VLC, Rhythmbox, Clementine, etc.)

### Installing playerctl

**Ubuntu/Debian:**
```bash
sudo apt install playerctl
```

**Arch Linux:**
```bash
sudo pacman -S playerctl
```

**Fedora:**
```bash
sudo dnf install playerctl
```

**macOS:**
```bash
brew install playerctl
```

## 🚀 Installation

### Option 1: Install with pip (Recommended)

1. Clone this repository:
```bash
git clone https://github.com/FannyIsPrettyCool/bass-senpai.git
cd bass-senpai
```

2. Install the package:
```bash
pip install -e .
```

This will install bass-senpai and all its dependencies (Pillow, requests).

### Option 2: Manual dependency installation

```bash
pip install Pillow requests
```

Then run directly:
```bash
python -m bass_senpai.main
```

## 🎮 Usage

Simply run:
```bash
bass-senpai
```

The application will:
1. Connect to your currently active media player via MPRIS
2. Display track information and album artwork
3. Update in real-time as tracks change
4. Automatically adapt to your terminal size

### Command-line Options

```bash
bass-senpai                     # Start with default 1 second update interval
bass-senpai --interval 2.0      # Update every 2 seconds
bass-senpai --interval 0.5      # Update twice per second (smoother progress bar)
bass-senpai --help              # Show help message
bass-senpai --version           # Show version information
```

### Controls

- **Ctrl+C** - Exit bass-senpai gracefully

## 🎨 Display Layout

```
  bass-senpai
  ────────────────────────────────────────────────────────────────

                                                  ╔════════════╗
                                                  ║            ║
    ♪ Song Title                                  ║            ║
                                                  ║   Album    ║
    👤 Artist Name                                 ║  Artwork   ║
                                                  ║            ║
    💿 Album Name                                  ║            ║
                                                  ║            ║
                                                  ╚════════════╝
    ▶ Playing

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━───────────────

    02:34 / 04:12
```

### Status Indicators

- ▶ **Playing** (green) - Track is currently playing
- ⏸ **Paused** (yellow) - Playback is paused
- ⏹ **Stopped** (red) - Player is stopped

## 🛠️ How It Works

### Architecture

1. **MPRIS Integration**: Uses `playerctl` to communicate with media players via the MPRIS D-Bus interface
2. **Track Change Detection**: Monitors track metadata to detect changes and avoid unnecessary artwork downloads
3. **Artwork Caching**: 
   - Downloads album artwork from URLs provided by the media player
   - Stores images in `~/.cache/bass-senpai/artwork/` using MD5 hash of URL as filename
   - Reuses cached images for repeated plays
   - Supports both `file://` URLs and HTTP(S) URLs
4. **Efficient Rendering**: 
   - Updates only changed screen areas using ANSI escape sequences
   - Prevents flicker and stuttering during updates
   - Automatically clears to end of screen to handle terminal resizing
5. **Terminal Detection**:
   - Detects Kitty terminal via `$TERM` environment variable
   - Uses Kitty graphics protocol for pixel-perfect images
   - Falls back to Unicode colored text-art for compatibility

### Supported Media Players

Any media player that implements the MPRIS D-Bus interface, including:
- Spotify
- VLC
- Rhythmbox
- Clementine
- Audacious
- MPD (via mpDris2)
- Chromium/Chrome (with browser extension)
- And many more!

Test if your player is supported:
```bash
playerctl metadata
```

## 📐 Terminal Compatibility

### Full Support (Pixel-Perfect Images)
- **Kitty terminal**: Displays album artwork using the Kitty graphics protocol with full color and resolution

### Good Support (Colored Text-Art)
- **Any modern terminal**: Displays artwork as colored text-art using Unicode half-block characters (▀)
- Recommended terminals for best text-art quality:
  - Alacritty
  - iTerm2
  - GNOME Terminal
  - Konsole
  - Windows Terminal

### Small Terminal Support
Bass-senpai automatically adapts to small terminal sizes. Tested and working on:
- 1/4 of 1080p screen (480x270 pixels, approximately 60x30 characters)
- Vertical terminal splits
- Tiling window managers with small panes

## 📁 Cache Location

Album artwork is cached at:
```
~/.cache/bass-senpai/artwork/
```

Each artwork is stored as a JPEG file named with the MD5 hash of the artwork URL.

You can safely delete this directory to clear the cache:
```bash
rm -rf ~/.cache/bass-senpai/artwork/
```

## 🐛 Troubleshooting

### "playerctl is not available"
**Solution:** Install playerctl using your package manager (see Requirements section)

### No track information showing
**Possible causes:**
- No media player is running
- Media player doesn't support MPRIS
- Nothing is currently playing

**Debugging steps:**
1. Check if playerctl can see your player:
   ```bash
   playerctl -l
   ```
2. Check if metadata is available:
   ```bash
   playerctl metadata
   ```

### Album artwork not showing
**Possible causes:**
- Media player doesn't provide artwork URLs
- Network issue downloading remote artwork
- Local file permissions for `file://` URLs

**Debugging steps:**
1. Check if artwork URL is provided:
   ```bash
   playerctl metadata mpris:artUrl
   ```
2. Check cache directory permissions:
   ```bash
   ls -la ~/.cache/bass-senpai/
   ```

### Artwork looks pixelated or blocky
- **For best quality:** Use Kitty terminal
- **Other terminals:** Will show text-art representation which is intentionally stylized
- **Tip:** Larger terminal size = better text-art quality

### Display is cut off or misaligned
**Solution:** Resize your terminal or let bass-senpai restart - it automatically detects and adapts to terminal size changes on each update

### Unicode characters not displaying correctly
**Solution:** Ensure your terminal supports UTF-8 and has a font with good Unicode coverage installed (e.g., Noto Fonts, Fira Code, JetBrains Mono)

## 🎯 Advanced Usage

### Use with Specific Player
If you have multiple players running:
```bash
playerctl -p spotify metadata  # Test with specific player
```
Note: bass-senpai currently uses the default active player. To control which player is active, see `playerctl` documentation.

### Running as a Background Service
You can run bass-senpai in a tmux or screen session:
```bash
tmux new -s music "bass-senpai"
```

Detach with `Ctrl+B` then `D`, reattach with:
```bash
tmux attach -t music
```

### Custom Update Interval
Balance between responsiveness and CPU usage:
- **0.5 seconds**: Very smooth progress bar, higher CPU usage
- **1.0 seconds** (default): Good balance
- **2.0 seconds**: Lower CPU usage, less frequent updates

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
git clone https://github.com/FannyIsPrettyCool/bass-senpai.git
cd bass-senpai
pip install -e .
```

### Running Tests
```bash
python -m pytest tests/
```

### Running Demo
```bash
python demo.py
```

## 🙏 Acknowledgments

- Uses [playerctl](https://github.com/altdesktop/playerctl) for MPRIS integration
- Kitty graphics protocol for pixel-perfect images
- Inspired by various terminal music visualizers and players