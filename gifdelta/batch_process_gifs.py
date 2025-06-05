#!/usr/bin/env python3
"""
Batch GIF Delta Extractor
Processes all GIF files in the Test_art directory and extracts XOR deltas
"""

import os
import sys
import time
import argparse
from pathlib import Path
from gif_delta_extractor import process_gif


def find_gif_files(directory: str) -> list:
    """Find all GIF files in the specified directory."""
    gif_files = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.lower().endswith('.gif'):
                gif_files.append(os.path.join(directory, file))
    return sorted(gif_files)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def get_directory_size(directory: str) -> int:
    """Calculate total size of all files in a directory."""
    total_size = 0
    if os.path.exists(directory):
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    return total_size


def main():
    parser = argparse.ArgumentParser(description='Batch process GIF files for delta extraction')
    parser.add_argument('-d', '--delta-mode', choices=['previous', 'first'], default='previous',
                        help='Delta calculation mode: "previous" (from previous frame) or "first" (from first frame). Default: previous')
    parser.add_argument('-b', '--box-mode', choices=['multi', 'single'], default='multi',
                        help='Box splitting mode: "multi" (multiple optimized boxes) or "single" (single bounding box). Default: multi')
    parser.add_argument('-i', '--input-dir', default='../Test_art',
                        help='Input directory containing GIF files (default: ../Test_art)')
    parser.add_argument('-o', '--output-dir', default='batch_output',
                        help='Output directory for processed files (default: batch_output)')
    
    args = parser.parse_args()
    
    print("=== Batch GIF Delta Extractor ===\n")
    print(f"Delta mode: {args.delta_mode} frame")
    print(f"Box mode: {args.box_mode} box{'es' if args.box_mode == 'multi' else ''}")
    
    # Configuration
    test_art_dir = args.input_dir
    output_base_dir = args.output_dir
    
    # Find all GIF files
    print(f"Scanning for GIF files in '{test_art_dir}'...")
    gif_files = find_gif_files(test_art_dir)
    
    if not gif_files:
        print(f"No GIF files found in '{test_art_dir}'")
        return 1
    
    print(f"Found {len(gif_files)} GIF file(s):")
    total_input_size = 0
    for gif_file in gif_files:
        file_size = os.path.getsize(gif_file)
        total_input_size += file_size
        print(f"  - {os.path.basename(gif_file)} ({format_file_size(file_size)})")
    
    print(f"\nTotal input size: {format_file_size(total_input_size)}")
    print(f"Output directory: {output_base_dir}/\n")
    
    # Create base output directory
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Process each GIF
    processed_count = 0
    failed_count = 0
    start_time = time.time()
    processing_stats = []
    
    for i, gif_file in enumerate(gif_files, 1):
        gif_name = os.path.splitext(os.path.basename(gif_file))[0]
        output_dir = os.path.join(output_base_dir, f"{gif_name}_deltas")
        
        print(f"[{i}/{len(gif_files)}] Processing {os.path.basename(gif_file)}...")
        
        try:
            file_start_time = time.time()
            metadata = process_gif(gif_file, output_dir, args.delta_mode, args.box_mode)
            file_process_time = time.time() - file_start_time
            
            # Calculate statistics for both box modes
            delta_frames = sum(1 for frame in metadata['frames'] if frame['type'] in ['multi_delta', 'single_delta'])
            no_change_frames = sum(1 for frame in metadata['frames'] if frame['type'] == 'no_change')
            total_boxes = sum(frame.get('box_count', 0) for frame in metadata['frames'])
            
            output_size = get_directory_size(output_dir)
            input_size = os.path.getsize(gif_file)
            
            stats = {
                'name': os.path.basename(gif_file),
                'input_size': input_size,
                'output_size': output_size,
                'total_frames': metadata['gif_info']['total_frames'],
                'delta_frames': delta_frames,
                'no_change_frames': no_change_frames,
                'total_boxes': total_boxes,
                'avg_boxes_per_delta': total_boxes / delta_frames if delta_frames > 0 else 0,
                'dimensions': f"{metadata['gif_info']['width']}x{metadata['gif_info']['height']}",
                'process_time': file_process_time,
                'compression_ratio': output_size / input_size if input_size > 0 else 0
            }
            processing_stats.append(stats)
            
            box_info = f"({total_boxes} boxes)" if args.box_mode == 'multi' else ""
            print(f"  ✓ Success! {metadata['gif_info']['total_frames']} frames → "
                  f"{delta_frames} deltas {box_info}, {no_change_frames} no-change "
                  f"({format_file_size(input_size)} → {format_file_size(output_size)}, "
                  f"{stats['compression_ratio']:.2f}x ratio)")
            
            processed_count += 1
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed_count += 1
    
    # Print summary
    total_time = time.time() - start_time
    print(f"\n=== Processing Complete ===")
    print(f"Processed: {processed_count}/{len(gif_files)} files")
    print(f"Failed: {failed_count} files")
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Average time per file: {total_time/len(gif_files):.1f} seconds")
    print(f"Delta mode used: {args.delta_mode}")
    print(f"Box mode used: {args.box_mode}")
    
    if processing_stats:
        print(f"\n=== Statistics ===")
        total_input = sum(s['input_size'] for s in processing_stats)
        total_output = sum(s['output_size'] for s in processing_stats)
        total_frames = sum(s['total_frames'] for s in processing_stats)
        total_deltas = sum(s['delta_frames'] for s in processing_stats)
        total_boxes = sum(s['total_boxes'] for s in processing_stats)
        
        print(f"Total input size: {format_file_size(total_input)}")
        print(f"Total output size: {format_file_size(total_output)}")
        print(f"Overall compression ratio: {total_output/total_input:.2f}x")
        print(f"Total frames processed: {total_frames}")
        print(f"Total delta frames: {total_deltas}")
        print(f"Total delta boxes: {total_boxes}")
        
        if args.box_mode == 'multi':
            print(f"Average boxes per delta frame: {total_boxes/total_deltas:.1f}" if total_deltas > 0 else "Average boxes per delta frame: 0")
        
        print(f"Delta efficiency: {total_deltas/total_frames*100:.1f}% of frames needed deltas")
        
        print(f"\n=== Individual Results ===")
        if args.box_mode == 'multi':
            print(f"{'File':<35} {'Frames':<8} {'Deltas':<8} {'Boxes':<8} {'Avg/Delta':<10} {'Size Ratio':<12} {'Time':<8}")
            print("-" * 95)
        else:
            print(f"{'File':<35} {'Frames':<8} {'Deltas':<8} {'Size Ratio':<12} {'Time':<8}")
            print("-" * 75)
        
        for stats in processing_stats:
            if args.box_mode == 'multi':
                print(f"{stats['name']:<35} "
                      f"{stats['total_frames']:<8} "
                      f"{stats['delta_frames']:<8} "
                      f"{stats['total_boxes']:<8} "
                      f"{stats['avg_boxes_per_delta']:.1f}{'':<6} "
                      f"{stats['compression_ratio']:.2f}x{'':<8} "
                      f"{stats['process_time']:.1f}s")
            else:
                print(f"{stats['name']:<35} "
                      f"{stats['total_frames']:<8} "
                      f"{stats['delta_frames']:<8} "
                      f"{stats['compression_ratio']:.2f}x{'':<8} "
                      f"{stats['process_time']:.1f}s")
    
    print(f"\nAll output saved to: {output_base_dir}/")
    print(f"Each GIF has its own subdirectory with delta images and metadata.json")
    
    if args.box_mode == 'multi':
        print(f"Delta images are split into multiple boxes when separated by empty space!")
    else:
        print(f"Delta images are saved as single bounding boxes for simplicity!")
    
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    exit(main()) 