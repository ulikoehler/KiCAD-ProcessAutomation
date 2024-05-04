#!/usr/bin/env python3
import argparse
import os
from collections import Counter
from typing import Dict

import pandas as pd
from UliPlot.XLSX import auto_adjust_xlsx_column_width

from KiCADIO import *

parser = argparse.ArgumentParser(description='Export BOM and pick & place files from KiCAD project')
parser.add_argument('filepath', type=str, help='Path to KiCAD project file')
parser.add_argument('-o', '--output', type=str, help='Output filename')
args = parser.parse_args()

# Compute output filename
output_filename = args.output
if output_filename is None:
    # Compute from input filename, split extension and append .BOM.xlsx
    output_filename = os.path.splitext(args.filepath)[0] + ".BOM.xlsx"
print(f"Exporting BOM to {output_filename}")

filepath = os.path.expanduser(args.filepath)
proj_filenames = kicad_project_filenames(filepath)
proj_filenames.check_files_exist()
# Export BOM from schematic
bom = export_and_read_bom_file(proj_filenames.sch)
# Export pick & place positions from PCB
pnp_positions = export_and_read_position_file(proj_filenames.pcb)

components = extract_components_from_bom(bom, pnp_positions, extra_properties=[
    "Part replacement policy"
])

df = component_list_to_dataframe(components)

# Rename columns
column_map = {
    "value": "Wert",
    "footprint": "Footprint",
    "populate": "Bestücken",
    "Total count": "Gesamtzahl",
    "Side": "Seite",
    "Part replacement policy": "Ersatzschema",
}

"""
Maps a boolean value to either "x" (if True)
or an empty string (if False).
"""
XorNothingPolicy: Dict[bool, str] = {True: "x", False: "", None: ""}

value_map_policies = {
    "populate": XorNothingPolicy
}

# Export dataset to XLSX
with pd.ExcelWriter(output_filename) as writer:
    # Map values
    for column, value_map in value_map_policies.items():
        df[column] = df[column].map(value_map)
    # Apply column renaming maps
    df.rename(columns=column_map, inplace=True)
    df.to_excel(writer, sheet_name="BOM")
    auto_adjust_xlsx_column_width(df, writer, sheet_name="BOM", margin=0)