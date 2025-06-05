# GIFD Binary Format Specification

## Overview

The GIFD (GIF Delta) format is a compact binary representation of GIF animation metadata, specifically designed for efficient loading in C/C++ applications. It stores information about frame deltas, bounding boxes, and timing data extracted from GIF animations.

**File Extension:** `.gifd`  
**Magic Number:** `0x44464947` ("GIFD" in ASCII)  
**Current Version:** `1`  
**Byte Order:** Little-endian  

## File Structure

The GIFD file consists of:
1. [File Header](#file-header)
2. [Frame Data](#frame-data) (repeated for each frame)

### Data Types

| Type | Size | Description |
|------|------|-------------|
| `uint8_t` | 1 byte | Unsigned 8-bit integer |
| `uint32_t` | 4 bytes | Unsigned 32-bit integer (little-endian) |
| `string` | variable | UTF-8 string prefixed with `uint32_t` length |

## File Header

The file header contains global information about the GIF animation:

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| 0x00 | `uint32_t` | magic_number | Magic number `0x44464947` ("GIFD") |
| 0x04 | `uint32_t` | format_version | Format version (currently `1`) |
| 0x08 | `uint32_t` | width | GIF canvas width in pixels |
| 0x0C | `uint32_t` | height | GIF canvas height in pixels |
| 0x10 | `uint32_t` | frame_count | Total number of frames |
| 0x14 | `string` | original_filename | Original GIF filename |

**Total Header Size:** 20 bytes + original_filename length

## Frame Data

Each frame is stored sequentially after the header. There are two frame types:

### Frame Header (Common to all frame types)

| Offset | Type | Field | Description |
|--------|------|-------|-------------|
| 0x00 | `uint32_t` | frame_index | Zero-based frame index |
| 0x04 | `uint8_t` | frame_type | Frame type (see below) |
| 0x05 | `uint32_t` | duration | Frame duration in milliseconds |
| 0x09 | `uint32_t` | bbox_x1 | Bounding box left coordinate |
| 0x0D | `uint32_t` | bbox_y1 | Bounding box top coordinate |
| 0x11 | `uint32_t` | bbox_x2 | Bounding box right coordinate (exclusive) |
| 0x15 | `uint32_t` | bbox_y2 | Bounding box bottom coordinate (exclusive) |

**Frame Header Size:** 25 bytes

### Frame Types

| Value | Type | Description |
|-------|------|-------------|
| `0` | Reference | Full reference frame (typically frame 0) |
| `1` | Multi-Delta | Frame with multiple delta regions |

### Reference Frame (Type 0)

Reference frames contain the complete image data for a frame, typically the first frame of an animation.

**Additional Fields:**
| Type | Field | Description |
|------|-------|-------------|
| `string` | reference_filename | Filename of the reference image (PNG) |
| `uint32_t` | delta_box_count | Number of delta boxes (always `0` for reference frames) |

### Multi-Delta Frame (Type 1)

Multi-delta frames contain one or more rectangular regions that differ from the previous frame.

**Additional Fields:**
| Type | Field | Description |
|------|-------|-------------|
| `uint32_t` | delta_box_count | Number of delta boxes in this frame |
| `delta_box[]` | delta_boxes | Array of delta box structures |

### Delta Box Structure

Each delta box represents a rectangular region that changed between frames:

| Type | Field | Description |
|------|-------|-------------|
| `string` | filename | Filename of the delta image (PNG) |
| `uint32_t` | bbox_x1 | Delta bounding box left coordinate |
| `uint32_t` | bbox_y1 | Delta bounding box top coordinate |
| `uint32_t` | bbox_x2 | Delta bounding box right coordinate (exclusive) |
| `uint32_t` | bbox_y2 | Delta bounding box bottom coordinate (exclusive) |
| `uint32_t` | pos_x | Position X coordinate within the canvas |
| `uint32_t` | pos_y | Position Y coordinate within the canvas |
| `uint32_t` | size_width | Width of the delta region |
| `uint32_t` | size_height | Height of the delta region |

**Delta Box Size:** Variable (filename length + 36 bytes)

## String Format

Strings are stored as:
1. `uint32_t` length (number of UTF-8 bytes, not including null terminator)
2. UTF-8 encoded string data (no null terminator in file)

Empty strings are stored as length `0` with no following data.

## Usage Pattern

1. **Load File:** Use `gifd_load_from_file()` to read the entire file into memory
2. **Access Frames:** Use `gifd_get_frame()` to access specific frames by index
3. **Process Deltas:** For each delta frame, iterate through delta boxes to reconstruct the frame
4. **Clean Up:** Use `gifd_free()` to release all allocated memory

## Example File Structure

```
[Header]
Magic: 0x44464947
Version: 1
Dimensions: 800x336
Frame Count: 3
Filename: "animation.gif"

[Frame 0 - Reference]
Index: 0, Type: 0, Duration: 80ms
BBox: (0,0) to (800,336)
Reference: "frame_000_reference.png"
Delta Count: 0

[Frame 1 - Multi-Delta]
Index: 1, Type: 1, Duration: 80ms
BBox: (60,180) to (745,244)
Delta Count: 7
  Delta 0: "frame_001_delta_00.png" at (187,180) size 21x9
  Delta 1: "frame_001_delta_01.png" at (260,180) size 10x5
  ... (5 more deltas)

[Frame 2 - Multi-Delta]
Index: 2, Type: 1, Duration: 80ms
BBox: (12,180) to (800,327)
Delta Count: 16
  Delta 0: "frame_002_delta_00.png" at (187,180) size 22x9
  ... (15 more deltas)
```

## Error Handling

Readers should validate:
- Magic number matches `0x44464947`
- Format version is supported (currently `1`)
- File size is sufficient for the declared number of frames
- String lengths don't exceed remaining file size
- Frame indices are sequential and within expected range

## Advantages

1. **Compact:** Significantly smaller than JSON (typically 60-80% reduction)
2. **Fast Loading:** Binary format with no parsing overhead
3. **Memory Efficient:** Fixed-size structures with minimal padding
4. **Platform Independent:** Little-endian format works across platforms
5. **Extensible:** Version field allows for future format extensions

## Compression Comparison

Based on typical usage:
- Original JSON: ~27KB
- Binary GIFD: ~8-12KB
- Compression ratio: 30-45% of original size

## Tools

- **Converter:** `json_to_binary_converter.py` - Converts JSON metadata to GIFD format
- **C/C++ Reader:** `gif_delta_reader.h/.c` - Loads and parses GIFD files
- **Validation:** Built-in validation functions check file integrity 