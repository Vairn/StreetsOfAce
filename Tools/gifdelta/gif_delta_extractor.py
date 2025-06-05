#!/usr/bin/env python3
"""
GIF Delta Extractor
Extracts frames from a GIF and saves only XOR deltas between consecutive frames
along with JSON metadata describing where each delta should be drawn.
"""

import os
import json
import argparse
from PIL import Image, ImageChops
import numpy as np
from typing import List, Tuple, Dict, Any
from scipy import ndimage
from scipy.ndimage import label


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    else:
        return obj


def load_gif_frames(gif_path: str) -> List[Image.Image]:
    """Load all frames from a GIF file."""
    frames = []
    with Image.open(gif_path) as gif:
        try:
            while True:
                # Convert to RGBA to ensure consistent format
                frame = gif.convert('RGBA')
                frames.append(frame.copy())
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
    return frames


def find_single_bounding_box(image: Image.Image) -> Tuple[int, int, int, int]:
    """Find the single overall bounding box of non-transparent pixels in an image."""
    # Convert to numpy array for faster processing
    arr = np.array(image)
    
    # Find non-transparent pixels (alpha > 0)
    if arr.shape[2] == 4:  # RGBA
        non_transparent = arr[:, :, 3] > 0
    else:  # RGB - treat all pixels as non-transparent
        non_transparent = np.ones((arr.shape[0], arr.shape[1]), dtype=bool)
    
    # Find bounding box
    if not np.any(non_transparent):
        return (0, 0, 0, 0)  # Empty bounding box
    
    rows = np.where(np.any(non_transparent, axis=1))[0]
    cols = np.where(np.any(non_transparent, axis=0))[0]
    
    if len(rows) == 0 or len(cols) == 0:
        return (0, 0, 0, 0)
    
    min_row, max_row = int(rows[0]), int(rows[-1])
    min_col, max_col = int(cols[0]), int(cols[-1])
    
    return (min_col, min_row, max_col + 1, max_row + 1)


def find_delta_boxes(image: Image.Image, min_box_size: int = 8, merge_distance: int = 16) -> List[Tuple[int, int, int, int]]:
    """
    Find multiple bounding boxes for non-transparent regions in an image.
    Splits large regions into smaller boxes when they're separated by enough space.
    
    Args:
        image: RGBA image with transparent pixels where no changes occurred
        min_box_size: Minimum size for a box to be considered (width or height)
        merge_distance: Maximum distance between regions to merge them into one box
    
    Returns:
        List of bounding boxes as (x, y, x+width, y+height) tuples
    """
    # Convert to numpy array for faster processing
    arr = np.array(image)
    
    # Find non-transparent pixels (alpha > 0)
    if arr.shape[2] == 4:  # RGBA
        non_transparent = arr[:, :, 3] > 0
    else:  # RGB - treat all pixels as non-transparent
        non_transparent = np.ones((arr.shape[0], arr.shape[1]), dtype=bool)
    
    # If no changes, return empty list
    if not np.any(non_transparent):
        return []
    
    # Label connected components
    labeled_array, num_features = label(non_transparent)
    
    if num_features == 0:
        return []
    
    # Find bounding box for each connected component
    component_boxes = []
    for i in range(1, num_features + 1):
        component_mask = labeled_array == i
        rows = np.where(np.any(component_mask, axis=1))[0]
        cols = np.where(np.any(component_mask, axis=0))[0]
        
        if len(rows) > 0 and len(cols) > 0:
            min_row, max_row = int(rows[0]), int(rows[-1])
            min_col, max_col = int(cols[0]), int(cols[-1])
            
            width = max_col - min_col + 1
            height = max_row - min_row + 1
            
            # Only include boxes that meet minimum size requirement
            if width >= min_box_size or height >= min_box_size:
                component_boxes.append((min_col, min_row, max_col + 1, max_row + 1))
    
    if not component_boxes:
        return []
    
    # Merge nearby boxes if they're close enough
    merged_boxes = []
    used_boxes = set()
    
    for i, box1 in enumerate(component_boxes):
        if i in used_boxes:
            continue
            
        # Start with current box
        merged_box = list(box1)  # [x1, y1, x2, y2]
        used_boxes.add(i)
        
        # Check if any other boxes should be merged with this one
        for j, box2 in enumerate(component_boxes):
            if j in used_boxes:
                continue
            
            # Calculate distance between boxes
            x1, y1, x2, y2 = merged_box
            bx1, by1, bx2, by2 = box2
            
            # Check if boxes are close enough to merge
            horizontal_gap = max(0, max(x1, bx1) - min(x2, bx2))
            vertical_gap = max(0, max(y1, by1) - min(y2, by2))
            
            if horizontal_gap <= merge_distance and vertical_gap <= merge_distance:
                # Merge the boxes
                merged_box[0] = min(merged_box[0], bx1)  # min x
                merged_box[1] = min(merged_box[1], by1)  # min y
                merged_box[2] = max(merged_box[2], bx2)  # max x
                merged_box[3] = max(merged_box[3], by2)  # max y
                used_boxes.add(j)
        
        merged_boxes.append(tuple(merged_box))
    
    # Sort boxes by position (top-to-bottom, left-to-right)
    merged_boxes.sort(key=lambda box: (box[1], box[0]))
    
    return merged_boxes


def calculate_xor_delta(frame1: Image.Image, frame2: Image.Image) -> Image.Image:
    """Calculate XOR delta between two frames."""
    # Ensure both images have the same size
    if frame1.size != frame2.size:
        frame2 = frame2.resize(frame1.size, Image.LANCZOS)
    
    # Convert both frames to the same mode
    if frame1.mode != frame2.mode:
        frame2 = frame2.convert(frame1.mode)
    
    # Calculate difference using ImageChops
    diff = ImageChops.difference(frame1, frame2)
    
    # Create XOR-like effect by making different pixels visible
    # and identical pixels transparent
    if diff.mode == 'RGBA':
        # Convert to numpy for pixel manipulation
        diff_array = np.array(diff)
        frame2_array = np.array(frame2)
        
        # Create result array
        result_array = frame2_array.copy()
        
        # Make pixels transparent where there's no difference
        diff_sum = np.sum(diff_array[:, :, :3], axis=2)
        transparent_mask = diff_sum == 0
        result_array[transparent_mask, 3] = 0  # Set alpha to 0 for identical pixels
        
        return Image.fromarray(result_array, 'RGBA')
    else:
        # For non-RGBA images, convert to RGBA and apply transparency
        diff_rgba = diff.convert('RGBA')
        frame2_rgba = frame2.convert('RGBA')
        
        diff_array = np.array(diff_rgba)
        frame2_array = np.array(frame2_rgba)
        result_array = frame2_array.copy()
        
        diff_sum = np.sum(diff_array[:, :, :3], axis=2)
        transparent_mask = diff_sum == 0
        result_array[transparent_mask, 3] = 0
        
        return Image.fromarray(result_array, 'RGBA')


def process_gif(gif_path: str, output_dir: str, delta_mode: str = 'previous', box_mode: str = 'multi') -> Dict[str, Any]:
    """
    Process a GIF file and extract delta frames with metadata.
    
    Args:
        gif_path: Path to the GIF file
        output_dir: Directory to save output files
        delta_mode: 'previous' for delta from previous frame, 'first' for delta from first frame
        box_mode: 'multi' for multiple optimized boxes, 'single' for single bounding box
    """
    if delta_mode not in ['previous', 'first']:
        raise ValueError("delta_mode must be 'previous' or 'first'")
    
    if box_mode not in ['multi', 'single']:
        raise ValueError("box_mode must be 'multi' or 'single'")
    
    print(f"Processing {gif_path}...")
    print(f"Delta mode: {delta_mode} frame")
    print(f"Box mode: {box_mode} box{'es' if box_mode == 'multi' else ''}")
    
    # Load all frames
    frames = load_gif_frames(gif_path)
    if len(frames) < 2:
        raise ValueError("GIF must have at least 2 frames")
    
    # Get GIF info
    with Image.open(gif_path) as gif:
        gif_info = {
            'width': gif.size[0],
            'height': gif.size[1],
            'total_frames': len(frames),
            'original_file': os.path.basename(gif_path)
        }
        
        # Try to get duration info
        try:
            gif.seek(0)
            duration = gif.info.get('duration', 100)  # Default 100ms
        except:
            duration = 100
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process deltas
    deltas_info = []
    
    # Save first frame as-is (reference frame)
    first_frame_path = os.path.join(output_dir, 'frame_000_reference.png')
    frames[0].save(first_frame_path, 'PNG')
    
    first_frame_info = {
        'frame_index': 0,
        'type': 'reference',
        'filename': 'frame_000_reference.png',
        'bounding_box': [0, 0, frames[0].size[0], frames[0].size[1]],
        'delta_boxes': [],
        'duration': int(duration)
    }
    deltas_info.append(first_frame_info)
    
    # Process remaining frames as deltas
    for i in range(1, len(frames)):
        print(f"  Processing frame {i}/{len(frames)-1}...")
        
        # Calculate XOR delta based on mode
        if delta_mode == 'previous':
            delta = calculate_xor_delta(frames[i-1], frames[i])
        else:  # delta_mode == 'first'
            delta = calculate_xor_delta(frames[0], frames[i])
        
        # Find delta boxes based on box mode
        if box_mode == 'multi':
            delta_boxes = find_delta_boxes(delta, min_box_size=4, merge_distance=20)
        else:  # box_mode == 'single'
            single_bbox = find_single_bounding_box(delta)
            delta_boxes = [single_bbox] if single_bbox != (0, 0, 0, 0) else []
        
        # If there are changes, crop and save each box
        if delta_boxes:
            saved_boxes = []
            
            for box_idx, bbox in enumerate(delta_boxes):
                cropped_delta = delta.crop(bbox)
                
                if box_mode == 'multi':
                    delta_filename = f'frame_{i:03d}_delta_{box_idx:02d}.png'
                else:  # single box mode
                    delta_filename = f'frame_{i:03d}_delta.png'
                
                delta_path = os.path.join(output_dir, delta_filename)
                cropped_delta.save(delta_path, 'PNG')
                
                box_info = {
                    'filename': delta_filename,
                    'bounding_box': [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                    'position': [int(bbox[0]), int(bbox[1])],
                    'size': [int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])]
                }
                saved_boxes.append(box_info)
            
            # Calculate overall bounding box for compatibility
            all_x1 = min(box['bounding_box'][0] for box in saved_boxes)
            all_y1 = min(box['bounding_box'][1] for box in saved_boxes)
            all_x2 = max(box['bounding_box'][2] for box in saved_boxes)
            all_y2 = max(box['bounding_box'][3] for box in saved_boxes)
            
            if box_mode == 'multi':
                frame_type = 'multi_delta'
                filename = None  # No single file, multiple boxes
            else:
                frame_type = 'single_delta'
                filename = saved_boxes[0]['filename']  # Single file
            
            delta_info = {
                'frame_index': i,
                'type': frame_type,
                'filename': filename,
                'bounding_box': [all_x1, all_y1, all_x2, all_y2],  # Overall bounds
                'delta_boxes': saved_boxes,  # Individual delta boxes
                'box_count': len(saved_boxes),
                'duration': int(duration)
            }
        else:
            # No changes, just metadata
            delta_info = {
                'frame_index': i,
                'type': 'no_change',
                'filename': None,
                'bounding_box': [0, 0, 0, 0],
                'delta_boxes': [],
                'box_count': 0,
                'duration': int(duration)
            }
        
        deltas_info.append(delta_info)
    
    # Create metadata and convert numpy types
    method_name = f"xor_delta_{box_mode}box{'es' if box_mode == 'multi' else ''}"
    box_description = "split into multiple boxes" if box_mode == 'multi' else "saved as single bounding box"
    
    metadata = {
        'gif_info': gif_info,
        'frames': deltas_info,
        'extraction_info': {
            'method': method_name,
            'delta_mode': delta_mode,
            'box_mode': box_mode,
            'description': f'First frame is reference, subsequent frames are XOR deltas {box_description} to optimize space. Deltas calculated from {delta_mode} frame.',
            'features': [
                f'{box_mode.title()}-box delta extraction',
                'Connected component analysis' if box_mode == 'multi' else 'Single bounding box calculation',
                'Automatic box merging for nearby regions' if box_mode == 'multi' else 'Minimal bounding box optimization',
                'Minimum box size filtering' if box_mode == 'multi' else 'Complete region preservation',
                f'Delta mode: {delta_mode} frame',
                f'Box mode: {box_mode}'
            ]
        }
    }
    
    # Convert any remaining numpy types to native Python types
    metadata = convert_numpy_types(metadata)
    
    # Save metadata JSON
    json_path = os.path.join(output_dir, 'metadata.json')
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"  Saved {len(deltas_info)} frame entries to {output_dir}")
    return metadata


def main():
    parser = argparse.ArgumentParser(description='Extract XOR deltas from GIF frames')
    parser.add_argument('gif_path', help='Path to the GIF file')
    parser.add_argument('-o', '--output', help='Output directory (default: gif_basename_deltas)')
    parser.add_argument('-d', '--delta-mode', choices=['previous', 'first'], default='previous',
                        help='Delta calculation mode: "previous" (from previous frame) or "first" (from first frame). Default: previous')
    parser.add_argument('-b', '--box-mode', choices=['multi', 'single'], default='multi',
                        help='Box splitting mode: "multi" (multiple optimized boxes) or "single" (single bounding box). Default: multi')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.gif_path):
        print(f"Error: GIF file '{args.gif_path}' not found")
        return 1
    
    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        gif_basename = os.path.splitext(os.path.basename(args.gif_path))[0]
        output_dir = f"{gif_basename}_deltas"
    
    try:
        metadata = process_gif(args.gif_path, output_dir, args.delta_mode, args.box_mode)
        print(f"\nSuccess! Extracted {len(metadata['frames'])} frames to '{output_dir}'")
        print(f"Metadata saved as '{os.path.join(output_dir, 'metadata.json')}'")
        print(f"Delta mode used: {args.delta_mode}")
        print(f"Box mode used: {args.box_mode}")
        
        # Print summary
        delta_count = sum(1 for frame in metadata['frames'] if frame['type'] in ['multi_delta', 'single_delta'])
        no_change_count = sum(1 for frame in metadata['frames'] if frame['type'] == 'no_change')
        total_boxes = sum(frame.get('box_count', 0) for frame in metadata['frames'])
        
        print(f"\nSummary:")
        print(f"  Reference frames: 1")
        print(f"  Delta frames: {delta_count}")
        print(f"  Total delta boxes: {total_boxes}")
        print(f"  No-change frames: {no_change_count}")
        
    except Exception as e:
        print(f"Error processing GIF: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main()) 