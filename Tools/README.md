# Streets of Ace - GIF Animation Tools

This project contains tools for processing and optimizing GIF animations, particularly for game development workflows.

## Directory Structure

- `gifdelta/` - GIF delta extraction and processing tools
- `gifd_tools/` - Binary format conversion tools for C/C++ integration
- `Test_art/` - Test images and assets
- `process_all_gifs.py` - Batch GIF processing script

## Key Features

### GIF Delta Processing
- Extract frame deltas from GIF animations
- Generate optimized PNG sequences
- JSON metadata for frame timing and positioning

### Binary Format Tools
- Convert JSON metadata to compact binary format
- C/C++ library for efficient data loading
- 60-80% size reduction compared to JSON
- See `gifd_tools/` directory for full documentation

## Quick Start

Process GIF files:
```bash
python process_all_gifs.py
```

Convert metadata to binary format:
```bash
cd gifd_tools
python json_to_binary_converter.py -r ../gifdelta/batch_output/
```

For detailed usage of the binary tools, see [`gifd_tools/README.md`](gifd_tools/README.md). 