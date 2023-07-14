#!/usr/bin/env python3
import sys
import argparse
import xml.etree.ElementTree as ET

def rotate_placements(board_file, rotation_offset):
    tree = ET.parse(board_file)
    root = tree.getroot()

    for placement in root.iter('placement'):
        location = placement.find('location')
        if location is not None:
            rotation = float(location.get('rotation', 0))
            new_rotation = (rotation + rotation_offset) % 360
            location.set('rotation', str(new_rotation))
            print(rotation, new_rotation)

    tree.write(board_file, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate placements in an OpenPnP board.xml file")
    parser.add_argument("board_file", type=str, help="Path to the board.xml file")
    parser.add_argument("-r", "--rotation-offset", required=True, type=float, help="Rotation offset in degrees")

    args = parser.parse_args()

    rotate_placements(args.board_file, args.rotation_offset)
