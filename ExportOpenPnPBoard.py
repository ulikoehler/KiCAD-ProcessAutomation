#!/usr/bin/env python3
import argparse
from OpenPnPIO import *
from KiCADIO import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export OpenPnP board XML from Ki')
    parser.add_argument('project_file', type=str, help='path to the KiCAD project file')
    args = parser.parse_args()

    project_file = args.project_file
    
    if not project_file.endswith(".kicad_pro") and not project_file.endswith(".pro"):
        print("ERROR: Project file must have .kicad_pro or .pro extension")
        exit(1)
        
    if not os.path.exists(project_file):
        print(f"ERROR: Project file {project_file} does not exist")
        exit(1)
    if not os.path.isfile(project_file):
        print(f"ERROR: Project file {project_file} is not a regular file")
        exit(1)
    
    # Get filenames of old & new PCBs
    project_name = os.path.splitext(os.path.basename(project_file))[0]
    
    # Compute schematic and PCB filename
    pcb_filename, sch_filename = pcb_and_sch_filenames(project_file)
    
    # Generate & parse position table
    position_table = export_and_read_position_file(pcb_filename)
    
    # Generate Placement objects from position_table
    # Generate Placement objects from position_table
    placements = []
    for refdes, row in position_table.iterrows():
        package_dash_value = f"{row['Package']}-{row['Val']}"
        placement = Placement(refdes,
                PlacementPosition(row["PosX"], row["PosY"], 0.0, row["Rot"]),
                row["Side"],
                package_dash_value,
                True # Enabled
                )
        placements.append(placement)
    
    # Create OpenPnP xml from placement list
    export_filename = f"{project_name}.board.xml"
    print(f"Exporting OpenPnP board XML to {export_filename}")
    with open(export_filename, "w") as f:
        xml_str = create_board(project_name, DefaultPlacementPosition, placements)
        f.write(xml_str)