# bass-senpai 🎵

A stylized terminal music status viewer that displays currently playing tracks with album artwork.

![bass-senpai demo](https://img.shields.io/badge/Status-Active-green)

## Features

- 🎵 **Real-time track information**: Artist, title, album, playback status
- 🎨 **Album artwork display**: 
  - Pixel-perfect images in Kitty terminal
  - Colored text-art fallback for other terminals
- 📊 **Animated progress bar**: Shows current playback position
- ⚡ **Efficient updates**: Only refreshes changed content to prevent stuttering
- 💾 **Smart caching**: Downloads album artwork once and caches it locally
- 🎮 **MPRIS support**: Works with any MPRIS-compatible media player via playerctl

## Requirements

- Python 3.8 or higher
- `playerctl` - for MPRIS integration
- A running media player that supports MPRIS (Spotify, VLC, Rhythmbox, etc.)

### Installing playerctl

**Ubuntu/Debian:**
```bash
sudo apt install playerctl
```

**Arch Linux:**
```bash
sudo pacman -S playerctl
```

**macOS:**
```bash
brew install playerctl
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/FannyIsPrettyCool/bass-senpai.git
cd bass-senpai
```

2. Install the package:
```bash
pip install -e .
```

Or install dependencies manually:
```bash
pip install Pillow requests
```

## Usage

Simply run:
```bash
bass-senpai
```

### Options

```bash
bass-senpai --interval 2.0    # Update every 2 seconds instead of default 1 second
bass-senpai --help            # Show help message
bass-senpai --version         # Show version
```

### Controls

- Press `Ctrl+C` to exit

## How It Works

1. **MPRIS Integration**: Uses `playerctl` to fetch metadata from your media player
2. **Track Change Detection**: Monitors for track changes to avoid unnecessary updates
3. **Artwork Caching**: 
   - Downloads album artwork on first play
   - Stores in `~/.cache/bass-senpai/artwork/`
   - Reuses cached images for repeated plays
4. **Efficient Rendering**: 
   - Updates only changed screen areas
   - Prevents flicker and stuttering
5. **Terminal Detection**:
   - Detects Kitty terminal for pixel-perfect images
   - Falls back to Unicode colored text-art otherwise

## Display Layout

```
  bass-senpai
  ────────────────────────────────────────────────────────────────

    Song Title                                    ╔════════════╗
                                                  ║            ║
    Artist Name                                   ║   Album    ║
                                                  ║  Artwork   ║
    Album Name                                    ║            ║
                                                  ╚════════════╝
    ▶ Playing

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━───────────────

    02:34 / 04:12
```

## Terminal Compatibility

- **Kitty**: Full support with pixel-perfect album artwork
- **Other terminals**: Colored text-art representation using Unicode blocks

## Cache Location

Album artwork is cached at: `~/.cache/bass-senpai/artwork/`

You can safely delete this directory to clear the cache.

## Troubleshooting

**"playerctl is not available"**
- Install playerctl using your package manager (see Requirements)

**No track information showing**
- Make sure a media player is running and playing music
- Verify playerctl works: `playerctl metadata`

**Album artwork not showing**
- Check if the media player provides artwork metadata
- Verify with: `playerctl metadata mpris:artUrl`

**Artwork looks pixelated**
- Use Kitty terminal for best quality
- Other terminals will show text-art representation

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.