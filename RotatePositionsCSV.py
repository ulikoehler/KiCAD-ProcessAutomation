#!/usr/bin/env python3
import pandas as pd
import argparse
import os.path

def rotate_positions(input_file, output_file, rotation_offset):
    df = pd.read_csv(input_file)
    df['Rotation'] = df['Rotation'] + rotation_offset
    # Export CSV
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate placements in a KiCAD positions.csv file")
    parser.add_argument("infile", type=str, help="Path to the input positions.csv file")
    parser.add_argument("outfile", type=str, help="Path to the output positions.csv file")
    parser.add_argument("-r", "--rotation-offset", required=True, type=float, help="Rotation offset in degrees")

    args = parser.parse_args()
    
    # Check if the input file exists
    if not os.path.isfile(args.infile):
        print("Input file does not exist")
        exit(1)
        
    # Check that the output file does not exist
    if os.path.isfile(args.outfile):
        print("Output file already exists")
        exit(1)

    rotate_positions(args.infile, args.outfile, args.rotation_offset)
