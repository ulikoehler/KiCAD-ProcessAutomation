#!/usr/bin/env python3
import argparse
import os
import glob
import subprocess

class TitleBlockParser(object):
    """
    S-exp parse specifically for parsing (title_block ...)
    
    This assumes human-readable formatting.
    No assumption is taken on the amount of whitespace at the front of the line.
    """
    def insert_title_block_data(self, title_block_data, outfilename):
        # We insert the title block data just after the first UUID line
        # While KiCad places it after the paper line, the UUID line
        # always exists.
        already_inserted_title_block = False
        with open(outfilename, 'w', encoding='utf-8') as outfile:
            for line in self.lines_without_title_block:
                outfile.write(line)
                if not already_inserted_title_block and "(uuid" in line.strip():
                    outfile.write("   (title_block\n")
                    for key, value in title_block_data.items():
                        outfile.write(f"       ({key} \"{value}\")\n")
                    outfile.write("   )\n")
                    already_inserted_title_block = True
    
    def parse(self, infilename):
        in_title_block = False
        found_title_block = False
        title_block_data = {}
        
        self.lines_without_title_block = []
        
        with open(infilename, encoding='utf-8') as file:
            for line in file:
                stripped_line = line.strip()

                # Check for the start of the title block
                if "(title_block" in stripped_line:
                    found_title_block = True
                    in_title_block = True
                    continue

                # Check for the end of the title block
                if in_title_block and stripped_line == ")":
                    in_title_block = False

                # Extract key-value pairs within the title block
                if in_title_block:
                    parts = stripped_line.split()
                    if len(parts) >= 2:
                        key = parts[0][1:]  # Remove the leading '('
                        value = ' '.join(parts[1:]).strip('()"')
                        title_block_data[key] = value
                else: # Not in the title block
                    self.lines_without_title_block.append(line)

        print(title_block_data)
        return title_block_data if found_title_block else None



def find_kicad_project(directory):
    """
    Find the KiCAD project file (.kicad_pro) in the specified directory.

    Args:
        directory (str): The directory to search for the KiCAD project file.

    Raises:
        ValueError: If no .kicad_pro files are found in the directory.
        ValueError: If multiple .kicad_pro files are found in the directory.
    """
    # Get list of .kicad_pro files in the directory
    kicad_pro_files = glob.glob(os.path.join(directory, "*.kicad_pro"))

    if len(kicad_pro_files) == 0:
        raise ValueError("No .kicad_pro files found in the directory.")
    elif len(kicad_pro_files) > 1:
        raise ValueError("Multiple .kicad_pro files found in the directory.")
    
    return kicad_pro_files[0]

def find_kicad_main_schematic(project_filename):
    """
    Find the main KiCAD schematic file (.kicad_sch) in the specified project file.

    Args:
        project_filename (str): The KiCAD project file to search for the main schematic file.

    Raises:
        ValueError: If no .kicad_sch files are found in the project file.
        ValueError: If multiple .kicad_sch files are found in the project file.
    """
    schematic_filename = os.path.splitext(project_filename)[0] + ".kicad_sch"

    # Check if the schematic file exists
    if not os.path.isfile(schematic_filename):
        raise ValueError(f"The schematic file {schematic_filename} does not exist.")

    return schematic_filename

def find_kicad_pcb_filenames(project_filename):
    """
    Find the KiCAD PCB files (.kicad_pcb) in the specified project file.

    Args:
        project_filename (str): The KiCAD project file to search for the PCB files.

    Raises:
        ValueError: If no .kicad_pcb files are found in the project file.
    """
    # Get list of .kicad_pcb files in the project file
    kicad_pcb_file = os.path.splitext(project_filename)[0] + ".kicad_pcb"
    
    # Check if the PCB file exists
    if not os.path.isfile(kicad_pcb_file):
        raise ValueError(f"The PCB file {kicad_pcb_file} does not exist.")
    
    return kicad_pcb_file

def export_kicad_schematic_pdf(schematic_filename, outdir=".", verbose=False):
    # Determine the output filename
    output_filename = os.path.splitext(os.path.basename(schematic_filename))[0] + ".pdf"
    output_path = os.path.join(outdir, output_filename)
    # Define the command
    command = [
        'kicad-cli', 'sch', 'export', 'pdf',
        schematic_filename,
        '--output',
        output_path,
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{' '.join(command)}' returned non-zero exit status {e.returncode}.")
    
    if verbose:
        print(f"Exported schematic '{schematic_filename}' PDF to '{output_path}'")

def export_kicad_project(project_filename, outdir=".", verbose=False):
    main_schematic_filename = find_kicad_main_schematic(project_filename)
    export_kicad_schematic_pdf(main_schematic_filename, outdir=outdir, verbose=verbose)
    title_block_parser = TitleBlockParser()
    title_block_parser.parse(main_schematic_filename)
    title_block_parser.insert_title_block_data({
        "rev": "123456",
        "title": "Testxx",
    }, "/ram/x.kicad_sch")

    try:
        pcb_filename = find_kicad_pcb_filenames(project_filename)

    except ValueError as ex:
        print("No PCB files found: " + str(ex))
        pcb_filename = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('directory', type=str, help='The directory to process')
    parser.add_argument('-o', '--output', type=str, default=".", help='The output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"The provided directory argument '{args.directory}' is not a directory.")
        exit(1)
        
    print(f"Processing directory '{args.directory}'")
    
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    # Find the KiCAD project file (.kicad_pro) in the specified directory.
    kicad_project = find_kicad_project(args.directory)
    export_kicad_project(kicad_project, outdir=args.output, verbose=args.verbose)
    
    