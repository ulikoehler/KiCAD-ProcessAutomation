#!/usr/bin/env python3
import argparse
import glob
import os
import shutil
import subprocess

class TitleBlockParser(object):
    """
    S-exp parse specifically for parsing (title_block ...)
    
    This assumes human-readable formatting.
    No assumption is taken on the amount of whitespace at the front of the line.
    """
    
    @staticmethod
    def update_file(infile, outfile, title_block_update=None):
        """
        Update the title block data in the input file and write it to the output file.

        Args:
            infile (str): The path to the input file.
            outfile (str): The path to the output file.
            title_block_update (dict, optional): A dictionary containing the updated title block data. Defaults to {}.

        Returns:
            None
        """
        if title_block_update is None:
            title_block_update = {}
        parser = TitleBlockParser()
        # Parse from input file
        title_block_data = parser.parse(infile) or {}
        # Apply changes
        title_block_data.update(title_block_update)
        # Write to output file
        parser.insert_title_block_data(title_block_data, outfile)
        
    @staticmethod
    def update_file_inplace_with_backup(filename, title_block_update=None):
        """
        Update a file in-place with a backup of the original file.

        Args:
            filename (str): The path of the file to be updated.
            title_block_update (dict): Optional dictionary containing the updates to be made to the title block.

        Returns:
            None
        """
        if title_block_update is None:
            title_block_update = {}
        # Create a backup of the original file
        shutil.copyfile(filename, TitleBlockParser.backup_filename(filename))
        # Update the file in-place
        TitleBlockParser.update_file(filename, filename, title_block_update)
        
    @staticmethod
    def restore_backup(filename):
        """
        Restore the backup of a file.
        """
        # Restore the backup file to the
        shutil.copyfile(TitleBlockParser.backup_filename(filename), filename)
        # Remove the backup file
        os.remove(TitleBlockParser.backup_filename(filename))
        
    @staticmethod
    def backup_filename(filename):
        return filename + ".ki-pa.bak" # kicad-process-automation
    
    def insert_title_block_data(self, title_block_data, outfilename):
        # We insert the title block data just after the first UUID line
        # While KiCad places it after the paper line, the UUID line
        # always exists.
        already_inserted_title_block = False
        with open(outfilename, 'w', encoding='utf-8') as outfile:
            for line in self.lines_without_title_block:
                outfile.write(line)
                if not already_inserted_title_block and "(uuid" in line.strip():
                    outfile.write("  (title_block\n")
                    for key, value in title_block_data.items():
                        outfile.write(f"     ({key} \"{value}\")\n")
                    outfile.write("  )\n")
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
                
                # Extract key-value pairs within the title block
                if in_title_block:
                    parts = stripped_line.split()
                    if len(parts) >= 2:
                        key = parts[0][1:]  # Remove the leading '('
                        value = ' '.join(parts[1:]).strip('()"')
                        title_block_data[key] = value
                else: # Not in the title block
                    self.lines_without_title_block.append(line)

                # Check for the end of the title block
                if in_title_block and stripped_line == ")":
                    in_title_block = False

        return title_block_data if found_title_block else None





class KiCadCIExporter(object):
    def __init__(self, directory, revision=None, verbose=False, outdir=".", extra_attributes=None):
        self.directory = directory
        self.outdir = outdir
        self.project_filename = self.find_kicad_project(directory)
        if revision is None:
            self.revision = f"Git revision: {self.git_describe_tags()}"
        else:
            self.revision = revision
        self.extra_attributes = extra_attributes or {}
        self.verbose = verbose
        
    def git_describe_tags(self):
        """
        Get the git revision using 'git describe --long --tags'.
        """
        return subprocess.check_output(['git', 'describe', '--long', '--tags'], cwd=self.directory).decode('utf-8').strip()
        
    def git_describe_short_revid(self):
        """
        Get the git revision using 'git describe --long --tags'.
        """
        return subprocess.check_output(['git', 'describe', '--always'], cwd=self.directory).decode('utf-8').strip()
        
    def git_get_commit_date(self):
        """
        Get the git commit date using 'git log -1 --format=%cd'.
        """
        return subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=format:%Y-%m-%d'], cwd=self.directory).decode('utf-8').strip()
    
    def export_kicad_project(self):
        main_schematic_filename = self.find_kicad_main_schematic()
        # Find all schematics and apply revision & date tags
        tags = {
            # Note: rev needs to be short
            "date": self.git_get_commit_date(),
            "rev": self.git_describe_short_revid(),
            "comment 1": self.revision,
            # TODO: Get the date from the git commit
            # "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        }
        tags.update(self.extra_attributes)
        for schematic_file in self.find_all_kicad_schematics():
            TitleBlockParser.update_file_inplace_with_backup(schematic_file, tags)
        # Export the schematic to PDF. kicad-cli will export all schematics even
        # if only the main one is given
        self.export_kicad_schematic_pdf(main_schematic_filename)
        # Restore backed up (original, without modified tags) versions of all schematics
        for schematic_file in self.find_all_kicad_schematics():
            TitleBlockParser.restore_backup(schematic_file)
        
        try:
            pcb_filename = self.find_kicad_pcb_filenames()

        except ValueError as ex:
            print("No PCB files found: " + str(ex))
            pcb_filename = None
            
    def export_kicad_schematic_pdf(self, schematic_filename):
        # Determine the output filename
        output_filename = os.path.splitext(os.path.basename(schematic_filename))[0] + ".pdf"
        output_path = os.path.join(self.outdir, output_filename)
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
        
        if self.verbose:
            print(f"Exported schematic '{schematic_filename}' PDF to '{output_path}'")
    
    def find_kicad_project(self, directory):
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
    
    def find_all_kicad_schematics(self):
        # Find all *.kicad_sch files in self.directory
        kicad_sch_files = glob.glob(os.path.join(self.directory, "*.kicad_sch"))
        return kicad_sch_files

    def find_kicad_main_schematic(self):
        """
        Find the main KiCAD schematic file (.kicad_sch) in the specified project file.

        Args:
            project_filename (str): The KiCAD project file to search for the main schematic file.

        Raises:
            ValueError: If no .kicad_sch files are found in the project file.
            ValueError: If multiple .kicad_sch files are found in the project file.
        """
        schematic_filename = os.path.splitext(self.project_filename)[0] + ".kicad_sch"

        # Check if the schematic file exists
        if not os.path.isfile(schematic_filename):
            raise ValueError(f"The schematic file {schematic_filename} does not exist.")

        return schematic_filename

    def find_kicad_pcb_filenames(self):
        """
        Find the KiCAD PCB files (.kicad_pcb) in the specified project file.

        Args:
            project_filename (str): The KiCAD project file to search for the PCB files.

        Raises:
            ValueError: If no .kicad_pcb files are found in the project file.
        """
        # Get list of .kicad_pcb files in the project file
        kicad_pcb_file = os.path.splitext(self.project_filename)[0] + ".kicad_pcb"
        
        # Check if the PCB file exists
        if not os.path.isfile(kicad_pcb_file):
            raise ValueError(f"The PCB file {kicad_pcb_file} does not exist.")
        
        return kicad_pcb_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('directory', type=str, help='The directory to process')
    parser.add_argument('-r', '--revision', type=str, default=None, help='Force using a specific revision tag. Defaults to using "git describe --long --tags"')
    parser.add_argument('-o', '--output', type=str, default=".", help='The output directory')
    parser.add_argument('-a', '--attribute', action='append', type=str, help='Extra attributes in the form "key=value"')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"The provided directory argument '{args.directory}' is not a directory.")
        exit(1)
        
    print(f"Processing directory '{args.directory}'")
    
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        
    # Parse the attributes into a dictionary
    extra_attributes = {}
    if args.attribute:
        for attribute in args.attribute:
            key, value = attribute.split('=')
            extra_attributes[key] = value

    
    # Find the KiCAD project file (.kicad_pro) in the specified directory.
    exporter = KiCadCIExporter(
        args.directory,
        revision=args.revision,
        verbose=args.verbose,
        outdir=args.output,
        extra_attributes=extra_attributes,
    )
    exporter.export_kicad_project()
    
    