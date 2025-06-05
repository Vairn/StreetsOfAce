# GIF Delta Extractor

This tool extracts frames from GIF files and saves only the XOR deltas between consecutive frames, along with JSON metadata describing where each delta should be drawn. This is useful for optimizing animated sprites by storing only the changes between frames.

## Features

- Extracts all frames from a GIF file
- **Configurable delta modes**: Choose between previous frame or first frame deltas
- **Configurable box modes**: Choose between multi-box splitting or single bounding box
- **Multi-box delta extraction** - Splits delta regions into separate boxes when separated by empty space
- **Single-box mode** - Traditional single bounding box per frame for simplicity
- Connected component analysis to identify separate change regions (multi-box mode)
- Automatic merging of nearby regions to avoid over-fragmentation (multi-box mode)
- Minimum box size filtering to ignore tiny changes (multi-box mode)
- Saves comprehensive JSON metadata with positioning information
- Handles transparent pixels correctly
- Supports both command-line and programmatic usage

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Basic usage - process a GIF file (defaults: previous frame deltas, multi-box mode)
python gif_delta_extractor.py path/to/your/animation.gif

# Use first frame deltas with single-box mode
python gif_delta_extractor.py path/to/your/animation.gif --delta-mode first --box-mode single

# Multi-box mode with previous frame deltas (most efficient)
python gif_delta_extractor.py Test_art/lastblade2-graveyard-stage.gif -d previous -b multi

# Single-box mode for simpler reconstruction  
python gif_delta_extractor.py Test_art/lastblade2-graveyard-stage.gif -d previous -b single
```

### Batch Processing

```bash
# Process all GIFs with defaults (previous frame deltas, multi-box mode)
python batch_process_gifs.py

# Process all GIFs with first frame deltas and single-box mode
python batch_process_gifs.py --delta-mode first --box-mode single

# Or run from root directory
cd ..
python process_all_gifs.py --delta-mode previous --box-mode multi
```

### Programmatic Usage

```python
from gif_delta_extractor import process_gif

# Process with defaults (previous frame deltas, multi-box mode)
metadata = process_gif("path/to/animation.gif", "output_directory")

# Process with first frame deltas and single-box mode
metadata = process_gif("path/to/animation.gif", "output_directory", 
                      delta_mode="first", box_mode="single")

# Access the metadata
print(f"Delta mode: {metadata['extraction_info']['delta_mode']}")
print(f"Box mode: {metadata['extraction_info']['box_mode']}")
for frame in metadata['frames']:
    if frame['type'] in ['multi_delta', 'single_delta']:
        print(f"Frame {frame['frame_index']}: {frame['box_count']} delta boxes")
```

### Compare All Modes

```bash
# Run example that compares all combinations of delta and box modes
python example_usage.py
```

## Delta Modes

### Previous Frame Deltas (default)
- **How it works**: Each frame is compared with the immediately previous frame
- **Best for**: Smooth animations, traditional sprite animations, looping sequences
- **Advantages**: 
  - Smaller output files (only incremental changes)
  - Efficient for sequential playback
  - Better compression ratios
- **Disadvantages**: 
  - Cannot jump to arbitrary frames without reconstructing sequence
  - Potential error accumulation

### First Frame Deltas
- **How it works**: Each frame is compared with the first (reference) frame
- **Best for**: Random access animations, frame-independent updates
- **Advantages**: 
  - Can jump to any frame independently
  - No error accumulation
  - Better for non-sequential access
- **Disadvantages**: 
  - Larger output files (more changes from reference)
  - Less efficient for smooth animations

## Box Modes

### Multi-Box Mode (default)
- **How it works**: Delta regions are split into multiple optimized boxes using connected component analysis
- **Best for**: Maximum space efficiency, animations with scattered changes
- **Advantages**:
  - Eliminates empty space between change regions
  - Optimal compression ratios
  - Perfect for complex animations
- **Disadvantages**:
  - More complex reconstruction
  - More files to manage

### Single-Box Mode
- **How it works**: Each frame delta is saved as one bounding box containing all changes
- **Best for**: Simplicity, compatibility with traditional delta systems
- **Advantages**:
  - Simple reconstruction (one file per frame)
  - Easier to manage
  - Compatible with existing systems
- **Disadvantages**:
  - May include empty space
  - Less optimal compression

## Output Structure

### Multi-Box Mode Output
```
output_directory/
├── metadata.json                   # Complete metadata about the extraction
├── frame_000_reference.png         # First frame (reference/base frame)
├── frame_001_delta_00.png          # First delta box for frame 1
├── frame_001_delta_01.png          # Second delta box for frame 1 (if multiple regions)
├── frame_002_delta_00.png          # Delta boxes for frame 2
└── ...                             # Additional delta frames and boxes
```

### Single-Box Mode Output
```
output_directory/
├── metadata.json                   # Complete metadata about the extraction
├── frame_000_reference.png         # First frame (reference/base frame)
├── frame_001_delta.png             # Single delta box for frame 1
├── frame_002_delta.png             # Single delta box for frame 2
└── ...                             # Additional delta frames
```

## JSON Metadata Structure

The `metadata.json` file contains enhanced information for both modes:

```json
{
  "gif_info": {
    "width": 320,
    "height": 240,
    "total_frames": 10,
    "original_file": "animation.gif"
  },
  "frames": [
    {
      "frame_index": 0,
      "type": "reference",
      "filename": "frame_000_reference.png",
      "bounding_box": [0, 0, 320, 240],
      "delta_boxes": [],
      "duration": 100
    },
    {
      "frame_index": 1,
      "type": "multi_delta",
      "filename": null,
      "bounding_box": [20, 30, 200, 180],
      "box_count": 2,
      "delta_boxes": [
        {
          "filename": "frame_001_delta_00.png",
          "bounding_box": [20, 30, 80, 90],
          "position": [20, 30],
          "size": [60, 60]
        },
        {
          "filename": "frame_001_delta_01.png",
          "bounding_box": [140, 120, 200, 180],
          "position": [140, 120],
          "size": [60, 60]
        }
      ],
      "duration": 100
    }
  ],
  "extraction_info": {
    "method": "xor_delta_multiboxes",
    "delta_mode": "previous",
    "box_mode": "multi",
    "description": "First frame is reference, subsequent frames are XOR deltas split into multiple boxes to optimize space. Deltas calculated from previous frame.",
    "features": [
      "Multi-box delta extraction",
      "Connected component analysis", 
      "Automatic box merging for nearby regions",
      "Minimum box size filtering",
      "Delta mode: previous frame",
      "Box mode: multi"
    ]
  }
}
```

### Frame Types

- **reference**: The first frame, saved as a complete image
- **multi_delta**: A frame with changes split into multiple optimized boxes (multi-box mode)
- **single_delta**: A frame with changes in one bounding box (single-box mode)
- **no_change**: A frame identical to the comparison frame (no files saved)

## Command Line Options

### Single File Processing
```bash
python gif_delta_extractor.py [OPTIONS] gif_path

Options:
  -o, --output DIR          Output directory (default: gif_basename_deltas)
  -d, --delta-mode MODE     Delta mode: 'previous' or 'first' (default: previous)
  -b, --box-mode MODE       Box mode: 'multi' or 'single' (default: multi)
  -h, --help               Show help message
```

### Batch Processing
```bash
python batch_process_gifs.py [OPTIONS]

Options:
  -d, --delta-mode MODE     Delta mode: 'previous' or 'first' (default: previous)
  -b, --box-mode MODE       Box mode: 'multi' or 'single' (default: multi)
  -i, --input-dir DIR       Input directory (default: ../Test_art)
  -o, --output-dir DIR      Output directory (default: batch_output)
  -h, --help               Show help message
```

## How It Works

1. **Frame Extraction**: All frames are loaded from the GIF file
2. **Delta Calculation**: Each frame is compared with previous/first frame based on delta mode
3. **Box Detection**: 
   - **Multi-box mode**: Connected component analysis groups changed pixels into regions
   - **Single-box mode**: Single bounding box calculation finds overall changed area
4. **Box Processing**:
   - **Multi-box mode**: Nearby regions merged, small boxes filtered, each region cropped optimally
   - **Single-box mode**: Single region cropped to minimal bounding box
5. **Metadata Generation**: Complete positioning information for each box is saved

## Benefits Comparison

| Feature | Multi-Box Mode | Single-Box Mode |
|---------|----------------|-----------------|
| **Space Efficiency** | ✅ Maximum (no empty areas) | ⚠️ Good (may include empty space) |
| **File Management** | ⚠️ More files | ✅ Fewer files |
| **Reconstruction** | ⚠️ More complex | ✅ Simple |
| **Compatibility** | ⚠️ Custom format | ✅ Traditional delta format |
| **Compression** | ✅ Optimal | ⚠️ Good |
| **Performance** | ⚠️ More processing | ✅ Faster processing |

## Configuration Parameters

Multi-box extraction can be tuned with these parameters in `find_delta_boxes()`:

- `min_box_size`: Minimum width or height for a box to be saved (default: 4 pixels)
- `merge_distance`: Maximum distance between regions to merge them (default: 20 pixels)

## Reconstruction

### Multi-Box Mode
1. Start with the reference frame
2. For each frame with `multi_delta` type:
   - For each box in `delta_boxes`:
     - Load the delta image file
     - Draw it at the specified position over the current frame
   - Display the result

### Single-Box Mode
1. Start with the reference frame  
2. For each frame with `single_delta` type:
   - Load the single delta image file
   - Draw it at the specified position over the current frame
   - Display the result

## Dependencies

- **Pillow (PIL)**: For image loading, manipulation, and saving
- **NumPy**: For efficient array operations and pixel manipulation  
- **SciPy**: For connected component analysis and region labeling (multi-box mode)

## Example GIFs

The `Test_art/` directory contains several example GIF files you can test with:
- `lastblade2-graveyard-stage.gif`
- `lastblade2-cloudy-battlefield-stage.gif`
- `lastblade2-forgotten-forest-stage.gif`
- And more...

## Choosing the Right Configuration

| Use Case | Recommended Delta Mode | Recommended Box Mode | Reason |
|----------|----------------------|---------------------|--------|
| Sequential playback | Previous | Multi | Smallest files, best compression |
| Random frame access | First | Single | Independent frames, simple reconstruction |
| Smooth animations | Previous | Multi | Minimal incremental changes, optimal compression |
| Simple integration | Previous | Single | Compatible with traditional delta systems |
| Maximum efficiency | Previous | Multi | Best compression, eliminates all waste |
| Rapid prototyping | Previous | Single | Quick to implement and test |

## Notes

- The first frame is always saved as a complete reference image
- Delta images use RGBA format with transparency for unchanged pixels
- Multi-box mode: Multiple boxes per frame numbered sequentially (`_00`, `_01`, etc.)
- Single-box mode: One file per frame with simple naming (`_delta.png`)
- Connected component analysis ensures optimal region detection (multi-box mode)
- Box merging prevents over-fragmentation while maintaining efficiency (multi-box mode)
- Delta and box modes are recorded in metadata for reconstruction guidance 