#!/usr/bin/env python3
"""
JSON to Binary Converter for GIF Delta Metadata
Converts JSON metadata files to a compact binary format for C/C++ consumption.
"""

import json
import struct
import os
import argparse
from typing import Dict, List, Any


class BinaryGifDeltaWriter:
    """Writes GIF delta metadata to binary format."""
    
    # Format version for compatibility checking
    FORMAT_VERSION = 1
    
    # Magic number to identify file format: "GIFD" (GIF Delta)
    MAGIC_NUMBER = 0x44464947
    
    def __init__(self):
        self.data = bytearray()
    
    def write_header(self, gif_info: Dict[str, Any], frame_count: int):
        """Write the file header."""
        # Magic number (4 bytes)
        self.data.extend(struct.pack('<I', self.MAGIC_NUMBER))
        
        # Format version (4 bytes)
        self.data.extend(struct.pack('<I', self.FORMAT_VERSION))
        
        # GIF dimensions (8 bytes)
        self.data.extend(struct.pack('<II', gif_info['width'], gif_info['height']))
        
        # Frame count (4 bytes)
        self.data.extend(struct.pack('<I', frame_count))
        
        # Original filename length and string
        filename = gif_info.get('original_file', '').encode('utf-8')
        self.data.extend(struct.pack('<I', len(filename)))
        self.data.extend(filename)
    
    def write_frame(self, frame: Dict[str, Any]):
        """Write a single frame's data."""
        # Frame index (4 bytes)
        self.data.extend(struct.pack('<I', frame['frame_index']))
        
        # Frame type (1 byte): 0=reference, 1=multi_delta
        frame_type = 0 if frame['type'] == 'reference' else 1
        self.data.extend(struct.pack('<B', frame_type))
        
        # Duration (4 bytes)
        self.data.extend(struct.pack('<I', frame.get('duration', 0)))
        
        # Bounding box (16 bytes)
        bbox = frame['bounding_box']
        self.data.extend(struct.pack('<IIII', bbox[0], bbox[1], bbox[2], bbox[3]))
        
        # Reference frame filename (for type 0)
        if frame_type == 0:
            filename = frame.get('filename', '').encode('utf-8')
            self.data.extend(struct.pack('<I', len(filename)))
            self.data.extend(filename)
            # No delta boxes for reference frames
            self.data.extend(struct.pack('<I', 0))
        else:
            # Delta boxes count (4 bytes)
            delta_boxes = frame.get('delta_boxes', [])
            self.data.extend(struct.pack('<I', len(delta_boxes)))
            
            # Write each delta box
            for delta_box in delta_boxes:
                # Filename
                filename = delta_box['filename'].encode('utf-8')
                self.data.extend(struct.pack('<I', len(filename)))
                self.data.extend(filename)
                
                # Bounding box (16 bytes)
                bbox = delta_box['bounding_box']
                self.data.extend(struct.pack('<IIII', bbox[0], bbox[1], bbox[2], bbox[3]))
                
                # Position (8 bytes)
                pos = delta_box['position']
                self.data.extend(struct.pack('<II', pos[0], pos[1]))
                
                # Size (8 bytes)
                size = delta_box['size']
                self.data.extend(struct.pack('<II', size[0], size[1]))
    
    def save_to_file(self, filename: str):
        """Save the binary data to a file."""
        with open(filename, 'wb') as f:
            f.write(self.data)


def convert_json_to_binary(json_path: str, output_path: str = None) -> str:
    """
    Convert a JSON metadata file to binary format.
    
    Args:
        json_path: Path to the input JSON file
        output_path: Path for the output binary file (optional)
    
    Returns:
        Path to the created binary file
    """
    if output_path is None:
        base_name = os.path.splitext(json_path)[0]
        output_path = f"{base_name}.gifd"
    
    # Load JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Create binary writer
    writer = BinaryGifDeltaWriter()
    
    # Write header
    gif_info = data['gif_info']
    frames = data['frames']
    writer.write_header(gif_info, len(frames))
    
    # Write each frame
    for frame in frames:
        writer.write_frame(frame)
    
    # Save to file
    writer.save_to_file(output_path)
    
    print(f"Converted {json_path} to {output_path}")
    print(f"Original JSON size: {os.path.getsize(json_path)} bytes")
    print(f"Binary size: {os.path.getsize(output_path)} bytes")
    print(f"Compression ratio: {os.path.getsize(output_path) / os.path.getsize(json_path):.2%}")
    
    return output_path


def batch_convert_directory(input_dir: str, output_dir: str = None):
    """Convert all metadata.json files in a directory and its subdirectories."""
    if output_dir is None:
        output_dir = input_dir
    
    converted_count = 0
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file == 'metadata.json':
                json_path = os.path.join(root, file)
                
                # Create corresponding output directory
                rel_path = os.path.relpath(root, input_dir)
                out_dir = os.path.join(output_dir, rel_path)
                os.makedirs(out_dir, exist_ok=True)
                
                # Convert the file
                output_path = os.path.join(out_dir, 'metadata.gifd')
                convert_json_to_binary(json_path, output_path)
                converted_count += 1
    
    print(f"\nConverted {converted_count} files total.")


def main():
    parser = argparse.ArgumentParser(description='Convert JSON metadata to binary format')
    parser.add_argument('input', help='Input JSON file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-r', '--recursive', action='store_true', 
                        help='Process directories recursively')
    
    args = parser.parse_args()
    
    if os.path.isfile(args.input):
        # Convert single file
        convert_json_to_binary(args.input, args.output)
    elif os.path.isdir(args.input):
        # Convert directory
        if args.recursive:
            batch_convert_directory(args.input, args.output)
        else:
            # Just convert metadata.json files in the specified directory
            metadata_path = os.path.join(args.input, 'metadata.json')
            if os.path.exists(metadata_path):
                output_path = args.output or os.path.join(args.input, 'metadata.gifd')
                convert_json_to_binary(metadata_path, output_path)
            else:
                print(f"No metadata.json found in {args.input}")
    else:
        print(f"Input path {args.input} does not exist")


if __name__ == '__main__':
    main() 