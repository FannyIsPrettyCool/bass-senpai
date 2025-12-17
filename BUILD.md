# Building bass-senpai (C++ Version)

## Prerequisites

### System Dependencies
- **CMake** (version 3.15 or higher)
- **C++ compiler** with C++17 support (GCC 8+, Clang 7+, or MSVC 2019+)
- **libcurl** development libraries
- **playerctl** - for MPRIS integration with media players

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install cmake g++ libcurl4-openssl-dev playerctl
```

**Arch Linux:**
```bash
sudo pacman -S cmake gcc curl playerctl
```

**Fedora:**
```bash
sudo dnf install cmake gcc-c++ libcurl-devel playerctl
```

**macOS:**
```bash
brew install cmake curl playerctl
```

## Building

1. Clone the repository:
```bash
git clone https://github.com/FannyIsPrettyCool/bass-senpai.git
cd bass-senpai
```

2. Create a build directory:
```bash
mkdir build
cd build
```

3. Configure the project:
```bash
cmake ..
```

4. Build:
```bash
cmake --build . -j$(nproc)
```

This will automatically download and build the required dependencies:
- nlohmann/json (for JSON parsing)
- stb_image (for image processing)

## Installation

After building, install the executable system-wide:

```bash
sudo cmake --install .
```

Or run directly from the build directory:
```bash
./bass-senpai
```

## Running

Simply run:
```bash
bass-senpai
```

With custom update interval:
```bash
bass-senpai --interval 2.0
```

## Troubleshooting

### CMake can't find CURL
Ensure libcurl development libraries are installed:
- Ubuntu/Debian: `sudo apt install libcurl4-openssl-dev`
- Fedora: `sudo dnf install libcurl-devel`
- macOS: `brew install curl`

### Compiler errors
Make sure you have a C++17-compatible compiler:
```bash
g++ --version  # Should be 8.0 or higher
```

### Missing playerctl
Install playerctl using your package manager (see Prerequisites).

## Development

### Debug Build
```bash
mkdir build-debug
cd build-debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
```

### Clean Build
```bash
rm -rf build
mkdir build
cd build
cmake ..
cmake --build .
```
