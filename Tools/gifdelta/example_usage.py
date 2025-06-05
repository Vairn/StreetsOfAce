#!/usr/bin/env python3
"""
Example usage of the GIF Delta Extractor
Demonstrates both delta modes ('previous' vs 'first') and box modes ('multi' vs 'single')
"""

from gif_delta_extractor import process_gif
import os

def compare_all_modes():
    """Compare the results of all combinations of delta and box modes."""
    # Example: Process one of the GIFs in Test_art directory
    gif_path = "Test_art/lastblade2-graveyard-stage.gif"
    
    if not os.path.exists(gif_path):
        print(f"GIF file not found: {gif_path}")
        print("Available GIFs in Test_art/:")
        if os.path.exists("Test_art"):
            for file in os.listdir("Test_art"):
                if file.endswith('.gif'):
                    print(f"  - {file}")
        return
    
    print("=== Comparing All Delta & Box Modes ===\n")
    
    # Process with all combinations
    delta_modes = ['previous', 'first']
    box_modes = ['multi', 'single']
    results = {}
    
    for delta_mode in delta_modes:
        for box_mode in box_modes:
            mode_key = f"{delta_mode}_{box_mode}"
            output_dir = f"graveyard_deltas_{mode_key}"
            print(f"Processing with '{delta_mode}' delta + '{box_mode}' box mode...")
            
            try:
                metadata = process_gif(gif_path, output_dir, delta_mode=delta_mode, box_mode=box_mode)
                
                # Calculate statistics
                total_boxes = sum(frame.get('box_count', 0) for frame in metadata['frames'])
                delta_frames = sum(1 for frame in metadata['frames'] if frame['type'] in ['multi_delta', 'single_delta'])
                no_change_frames = sum(1 for frame in metadata['frames'] if frame['type'] == 'no_change')
                
                # Calculate total output size
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        if file.endswith('.png'):
                            total_size += os.path.getsize(os.path.join(root, file))
                            file_count += 1
                
                results[mode_key] = {
                    'metadata': metadata,
                    'total_boxes': total_boxes,
                    'delta_frames': delta_frames,
                    'no_change_frames': no_change_frames,
                    'output_size': total_size,
                    'file_count': file_count,
                    'delta_mode': delta_mode,
                    'box_mode': box_mode
                }
                
                print(f"  ✓ {delta_mode}+{box_mode} mode complete!")
                
            except Exception as e:
                print(f"  ✗ {delta_mode}+{box_mode} mode failed: {e}")
                return
    
    # Compare results
    print("\n=== Comparison Results ===\n")
    
    gif_info = list(results.values())[0]['metadata']['gif_info']
    print(f"GIF: {gif_info['original_file']}")
    print(f"Dimensions: {gif_info['width']}x{gif_info['height']}")
    print(f"Total frames: {gif_info['total_frames']}\n")
    
    print(f"{'Mode':<20} {'Delta Frames':<12} {'Total Boxes':<12} {'Files':<8} {'Size (bytes)':<12} {'Avg Box/Delta':<12}")
    print("-" * 90)
    
    # Compare all combinations
    for mode_key, result in results.items():
        delta_mode = result['delta_mode']
        box_mode = result['box_mode']
        mode_display = f"{delta_mode}+{box_mode}"
        
        avg_boxes = result['total_boxes'] / result['delta_frames'] if result['delta_frames'] > 0 else 0
        
        print(f"{mode_display:<20} "
              f"{result['delta_frames']:<12} "
              f"{result['total_boxes']:<12} "
              f"{result['file_count']:<8} "
              f"{result['output_size']:<12} "
              f"{avg_boxes:.1f}")
    
    print(f"\n=== Size Comparisons ===")
    
    # Compare box modes for same delta mode
    for delta_mode in delta_modes:
        multi_key = f"{delta_mode}_multi"
        single_key = f"{delta_mode}_single"
        
        if multi_key in results and single_key in results:
            multi_size = results[multi_key]['output_size']
            single_size = results[single_key]['output_size']
            ratio = single_size / multi_size if multi_size > 0 else 0
            
            print(f"{delta_mode.title()} mode - Single vs Multi box ratio: {ratio:.2f}x")
            if ratio > 1:
                print(f"  → Single box mode is {ratio:.1f}x larger")
            else:
                print(f"  → Multi box mode is {1/ratio:.1f}x larger")
    
    # Compare delta modes for same box mode
    for box_mode in box_modes:
        prev_key = f"previous_{box_mode}"
        first_key = f"first_{box_mode}"
        
        if prev_key in results and first_key in results:
            prev_size = results[prev_key]['output_size']
            first_size = results[first_key]['output_size']
            ratio = first_size / prev_size if prev_size > 0 else 0
            
            print(f"{box_mode.title()} box mode - First vs Previous delta ratio: {ratio:.2f}x")
            if ratio > 1:
                print(f"  → First frame deltas are {ratio:.1f}x larger")
            else:
                print(f"  → Previous frame deltas are {1/ratio:.1f}x larger")
    
    print(f"\n=== Mode Recommendations ===")
    
    print(f"\nDelta Mode Guidelines:")
    print(f"  Previous frame deltas:")
    print(f"    ✓ Better for smooth animations with incremental changes")
    print(f"    ✓ Typically smaller file sizes")
    print(f"    ✓ Sequential playback optimization")
    print(f"    ✗ Cannot jump to arbitrary frames independently")
    
    print(f"\n  First frame deltas:")
    print(f"    ✓ Can jump to any frame independently")
    print(f"    ✓ No accumulation of errors")
    print(f"    ✓ Better for random access")
    print(f"    ✗ Typically larger file sizes")
    
    print(f"\nBox Mode Guidelines:")
    print(f"  Multi-box mode:")
    print(f"    ✓ Maximum space efficiency (eliminates empty areas)")
    print(f"    ✓ Optimal for scattered changes")
    print(f"    ✓ Better compression ratios")
    print(f"    ✗ More complex reconstruction")
    print(f"    ✗ More files to manage")
    
    print(f"\n  Single-box mode:")
    print(f"    ✓ Simpler reconstruction (one file per frame)")
    print(f"    ✓ Easier to manage")
    print(f"    ✓ Compatible with traditional delta systems")
    print(f"    ✗ May include empty space")
    print(f"    ✗ Less optimal compression")
    
    print(f"\n=== Output Directories ===")
    for mode_key in results.keys():
        print(f"  {mode_key}: graveyard_deltas_{mode_key}/")

def main():
    print("=== GIF Delta Extractor Example ===\n")
    compare_all_modes()

if __name__ == '__main__':
    main() 