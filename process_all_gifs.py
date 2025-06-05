#!/usr/bin/env python3
"""
Launcher script to process all GIFs in Test_art directory
Run this from the root directory to batch process all GIF files
"""

import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description='Batch process all GIFs in Test_art directory')
    parser.add_argument('-d', '--delta-mode', choices=['previous', 'first'], default='previous',
                        help='Delta calculation mode: "previous" (from previous frame) or "first" (from first frame). Default: previous')
    parser.add_argument('-b', '--box-mode', choices=['multi', 'single'], default='multi',
                        help='Box splitting mode: "multi" (multiple optimized boxes) or "single" (single bounding box). Default: multi')
    
    args = parser.parse_args()
    
    print("=== GIF Delta Batch Processor Launcher ===\n")
    print(f"Delta mode: {args.delta_mode}")
    print(f"Box mode: {args.box_mode}")
    
    # Check if gifdelta directory exists
    if not os.path.exists("gifdelta"):
        print("Error: gifdelta directory not found!")
        print("Make sure you're running this from the root directory.")
        return 1
    
    # Check if Test_art directory exists
    if not os.path.exists("Test_art"):
        print("Error: Test_art directory not found!")
        print("Make sure the Test_art directory with GIF files exists.")
        return 1
    
    # Count GIFs in Test_art
    gif_count = len([f for f in os.listdir("Test_art") if f.lower().endswith('.gif')])
    if gif_count == 0:
        print("No GIF files found in Test_art directory.")
        return 1
    
    print(f"Found {gif_count} GIF file(s) in Test_art directory.")
    print("Starting batch processing...\n")
    
    # Change to gifdelta directory and run the batch processor
    original_dir = os.getcwd()
    try:
        os.chdir("gifdelta")
        
        # Run the batch processor with both delta mode and box mode arguments
        cmd = [sys.executable, "batch_process_gifs.py", 
               "--delta-mode", args.delta_mode,
               "--box-mode", args.box_mode]
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running batch processor: {e}")
        return 1
    finally:
        os.chdir(original_dir)

if __name__ == '__main__':
    exit(main()) 