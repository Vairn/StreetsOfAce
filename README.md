# Streets of Ace

![Amiga](https://img.shields.io/badge/Platform-Amiga%201200-red.svg)
![AmiGameJam 2025](https://img.shields.io/badge/AmiGameJam-2025-blue.svg)
![License](https://img.shields.io/badge/License-MPL--2.0-green.svg)

An arcade-style game for the Amiga 1200 built for [AmiGameJam 2025](https://itch.io/jam/amigamejam).

## About

**Streets of Ace** is an original arcade-style game created specifically for the AmiGameJam 2025 competition. The theme challenges developers to create games worthy of their own arcade cabinet, targeting classic Amiga hardware with modern development techniques.

### Competition Details
- **Event**: [AmiGameJam 2025](https://itch.io/jam/amigamejam)
- **Timeline**: June 1st - December 1st, 2025
- **Theme**: Return of the Arcade - games worthy of arcade cabinets
- **Platform**: Amiga (targeting A1200 with AGA chipset)

## Features

- **AGA Enhanced Graphics**: Utilizes the advanced graphics capabilities of the Amiga 1200
- **Arcade-Style Gameplay**: Classic arcade mechanics with modern polish
- **Optimized Performance**: Direct hardware access for maximum speed
- **OS-Friendly**: Graceful integration with AmigaOS

## Technical Stack

- **Engine**: [ACE (Amiga C Engine)](https://github.com/Vairn/ACE/tree/AGA) - AGA Branch
- **Language**: C/C++ with assembly optimizations
- **Build System**: CMake with CPM package management
- **Graphics**: AGA chipset targeting 256+ colors
- **Audio**: MOD/sample-based audio system

## Project Structure

```
StreetsOfAce/
├── src/                    # Game source code
├── include/                # Header files
├── assets/                 # Game assets (graphics, audio)
├── Tools/                  # Python development tools
│   ├── gifd_tools/        # GIF animation processing
│   ├── gifdelta/          # Frame delta extraction
│   └── process_all_gifs.py # Batch processing script
├── build/                  # Build artifacts
├── CMakeLists.txt         # Main CMake configuration
└── README.md              # This file
```

## Prerequisites

### Development Environment
- **CMake** 3.15+ 
- **Cross-compiler** for 68000/68020 (e.g., m68k-amigaos-gcc)
- **Python 3.7+** (for asset processing tools)

### Target Hardware
- **Amiga 1200** or compatible (AGA chipset required)
- **2MB+ RAM** recommended
- **Hard drive** or CF card for development builds

## Quick Start

### 1. Clone and Build

```bash
git clone <repository-url> StreetsOfAce
cd StreetsOfAce
mkdir build && cd build
cmake ..
make
```

### 2. Process Assets

```bash
cd Tools
python process_all_gifs.py
cd gifd_tools
python json_to_binary_converter.py -r ../gifdelta/batch_output/
```

### 3. Deploy to Amiga

Copy the built executable and assets to your Amiga system.

## Development Tools

### GIF Animation Pipeline
The project includes a sophisticated GIF processing pipeline:

- **Delta Extraction**: Optimizes animations by extracting only changed pixels
- **Binary Format**: Converts JSON metadata to compact binary format (60-80% size reduction)
- **C Integration**: Provides C libraries for efficient runtime loading

See [`Tools/README.md`](Tools/README.md) for detailed tool documentation.

## ACE Engine Integration

This project uses the AGA-enhanced branch of the ACE engine, which provides:

- **AGA Screen Support**: Enhanced graphics modes beyond OCS/ECS
- **Hardware Abstraction**: Direct but safe hardware access
- **Performance Focus**: Minimal overhead, maximum speed
- **OS Compatibility**: Runs from Workbench, exits gracefully

## Building

### CMake Configuration

The project uses CPM (CMake Package Manager) to automatically fetch and build the ACE engine:

```bash
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

### Debug Builds

For development with runtime error checking:

```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
make
```

## Asset Pipeline

### Graphics
- Source graphics in PNG/GIF format
- Automated conversion to Amiga-compatible formats
- Palette optimization for AGA modes
- Sprite atlas generation

### Audio
- MOD tracker files for music
- WAV samples for sound effects
- Automatic format conversion

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Mozilla Public License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **ACE Engine**: [Vairn's AGA branch](https://github.com/Vairn/ACE/tree/AGA)
- **AmiGameJam 2025**: [Hosted by Amiga Cammy](https://itch.io/jam/amigamejam)
- **Amiga Community**: For keeping the platform alive and thriving

## Links

- [AmiGameJam 2025](https://itch.io/jam/amigamejam)
- [ACE Engine (AGA Branch)](https://github.com/Vairn/ACE/tree/AGA)
- [Amiga Development Resources](https://github.com/AmigaPorts)

---

*"Return of the Arcade" - Built with passion for the Amiga platform* 🎮 