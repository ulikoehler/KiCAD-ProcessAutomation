#!/usr/bin/env python3
import argparse
import glob
import os
import os.path
import shutil
import subprocess
import tempfile

class NoSchematicFile(Exception):
    """Raised when the schematic file is not found"""
    pass

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
    def __init__(self, arg, revision=None, verbose=False, outdir=".", extra_attributes=None, enabled_exports:dict={}):
        # If arg is a dir, find the project file
        if os.path.isdir(arg):
            self.directory = arg
            self.project_filename = self.find_kicad_project(arg)
        elif os.path.isfile(arg) and arg.endswith(".kicad_pro"):
            self.project_filename = arg
            # Set directory to parent dir of [arg]
            self.directory = os.path.dirname(arg)
        elif os.path.isfile(arg):
            raise ValueError(f"Project file '{arg}' does not end with .kicad_pro")
        else:
            raise ValueError(f"Project file '{arg}' does not exist or bad filename")
           
        self.outdir = outdir
        if revision is None:
            self.revision = self.git_describe_tags()
            self.custom_revision = False
        else:
            self.revision = revision
            self.custom_revision = True
        self.extra_attributes = extra_attributes or {}
        self.verbose = verbose
        if verbose:
            # Pipe run() stdout and stderr to the terminal
            self._run_extra_args = {'stdout': None, 'stderr': None}
        else: # not verbose
            # Pipe run() stdout and stderr to /dev/null
            self._run_extra_args = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
        self.enabled_exports = enabled_exports
        
    def git_describe_tags(self):
        """
        Get the git revision using 'git describe --long --tags'.
        """
        return subprocess.check_output(['git', 'describe', '--always', '--long', '--tags'], cwd=self.directory).decode('utf-8').strip()
        
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
        # Find all schematics and apply revision & date tags
        if self.enabled_exports["schematic_pdf"] is not False:
            try:
                main_schematic_filename = self.find_kicad_main_schematic()
                comment1 = f"Git revision: {self.revision}" if not self.custom_revision else "Custom revision"
                tags = {
                    # Note: rev needs to be short
                    "date": self.git_get_commit_date(),
                    "rev": self.git_describe_short_revid(),
                    "comment 1": comment1,
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
            except NoSchematicFile:
                print("No schematic file found! Skipping schematic export.")
        
        # Find PCB file and export
        try:
            pcb_filename = self.find_kicad_pcb_filename()
            if self.enabled_exports["step"] is not False:
                self.export_3d_model(pcb_filename)
                self.export_3d_model(pcb_filename, board_only=True)
            if self.enabled_exports["pcb_pdf"] is not False:
                self.export_pcb_pdf(pcb_filename)
            if self.enabled_exports["gerber"] is not False:
                self.export_pcb_gerbers(pcb_filename)
            if self.enabled_exports["pcb_svg"] is not False:
                self.export_pcb_svg(pcb_filename)
        except ValueError as ex:
            print("No PCB files found: " + str(ex))
            pcb_filename = None
            
    def export_kicad_schematic_pdf(self, schematic_filename):
        # Determine the output filename
        output_filename = os.path.splitext(os.path.basename(schematic_filename))[0] + "-Schematic.pdf"
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
            subprocess.run(command, check=True, **self._run_extra_args)
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
            raise NoSchematicFile(f"The schematic file {schematic_filename} does not exist.")

        return schematic_filename
    
    def export_3d_model(self, pcb_filename, board_only=False):
        step_filename = f"{os.path.splitext(pcb_filename)[0]}{'-BoardOnly' if board_only else ''}.step"
        
        step_filepath = os.path.join(self.outdir, os.path.basename(step_filename))
        # Define the command
        command = [
            'kicad-cli', 'pcb', 'export', 'step',
            '--drill-origin', '--no-dnp',
            pcb_filename, '--subst-models', '--output',
            step_filepath
        ]

        # Run the command
        try:
            subprocess.run(command, check=True, **self._run_extra_args)
            if self.verbose:
                print(f"Exported PCB '{pcb_filename}' 3D model to '{step_filepath}'")    
        except subprocess.CalledProcessError as e:
            print(f"Command '{' '.join(command)}' returned non-zero exit status {e.returncode}.")



    def export_pcb_pdf(self, pcb_filename):
        top_filename = f"{os.path.splitext(pcb_filename)[0]}-PCB-Top.pdf"
        bottom_filename = f"{os.path.splitext(pcb_filename)[0]}-PCB-Bottom.pdf"
        
        top_filepath = os.path.join(self.outdir, os.path.basename(top_filename))
        bottom_filepath = os.path.join(self.outdir, os.path.basename(bottom_filename))

        # Define the command
        top_command = [
            'kicad-cli', 'pcb', 'export', 'pdf', 
            '--layers', 'Edge.Cuts,F.Cu,F.Mask,F.Silkscreen',
            '--include-border-title',
            '--output', top_filepath,
            pcb_filename
        ]
        bottom_command = [
            'kicad-cli', 'pcb', 'export', 'pdf', 
            '--layers', 'Edge.Cuts,B.Cu,B.Mask,B.Silkscreen',
            '--include-border-title',
            '--output', bottom_filepath,
            pcb_filename
        ]

        # Run the command
        try:
            subprocess.run(top_command, check=True, **self._run_extra_args)
            if self.verbose:
                print(f"Exported PCB '{pcb_filename}' top PDF to '{top_filepath}'")
        except subprocess.CalledProcessError as e:
            print(f"Command '{' '.join(top_command)}' returned non-zero exit status {e.returncode}.")
    
        try:
            subprocess.run(bottom_command, check=True)
            if self.verbose:
                print(f"Exported PCB '{pcb_filename}' bottom PDF to '{bottom_filepath}'")
        except subprocess.CalledProcessError as e:
            print(f"Command '{' '.join(bottom_command)}' returned non-zero exit status {e.returncode}.")
    
    def export_pcb_svg(self, pcb_filename):
        """
        Export Top & bottom SVG. This differs from the PDF export in that it
        does not include the border title etc.
        """
        top_filename = f"{os.path.splitext(pcb_filename)[0]}-PCB-Top.svg"
        bottom_filename = f"{os.path.splitext(pcb_filename)[0]}-PCB-Bottom.svg"
        
        top_filepath = os.path.join(self.outdir, os.path.basename(top_filename))
        bottom_filepath = os.path.join(self.outdir, os.path.basename(bottom_filename))

        # Define the command
        base_command = [
            'kicad-cli', 'pcb', 'export', 'svg',
        ]
        extra_args = [
            '--exclude-drawing-sheet',
            '--page-size-mode', '2', # page size = only board area
            pcb_filename
        ]
        top_command = base_command + [
            '--layers', 'Edge.Cuts,F.Cu,F.Mask,F.Silkscreen',
            '--output', top_filepath,
        ] + extra_args
        bottom_command = base_command + [
            '--layers', 'Edge.Cuts,B.Cu,B.Mask,B.Silkscreen',
            '--output', bottom_filepath,
        ] + extra_args

        # Run the command
        # Export top
        try:
            subprocess.run(top_command, check=True, **self._run_extra_args)
            if self.verbose:
                print(f"Exported PCB '{pcb_filename}' top PDF to '{top_filepath}'")
        except subprocess.CalledProcessError as e:
            print(f"Command '{' '.join(top_command)}' returned non-zero exit status {e.returncode}.")
        # Export bottom
        try:
            subprocess.run(bottom_command, check=True)
            if self.verbose:
                print(f"Exported PCB '{pcb_filename}' bottom PDF to '{bottom_filepath}'")
        except subprocess.CalledProcessError as e:
            print(f"Command '{' '.join(bottom_command)}' returned non-zero exit status {e.returncode}.")
    
    def export_pcb_gerbers(self, pcb_filename):
        """
        Export all layers as Gerbers, plus drill files
        """
        # Create the output sub-directory
        canonical_project_name = os.path.splitext(os.path.basename(pcb_filename))[0]
        # Export gerbers to a temporary directory
        with tempfile.TemporaryDirectory() as gerber_dir:
            # Define the command
            gerber_command = [
                'kicad-cli', 'pcb', 'export', 'gerbers',
                pcb_filename, '--output', gerber_dir,
                '--use-drill-file-origin'
            ]
            gerber_dir_with_slash = gerber_dir + os.path.sep if not gerber_dir.endswith(os.path.sep) else gerber_dir
            drill_command = [
                'kicad-cli', 'pcb', 'export', 'drill',
                '--excellon-separate-th', # PTH & NPTH into separate file
                '--drill-origin', 'plot',
                '--output', gerber_dir_with_slash, # Slash: Hotfix for kicad-cli bug
                pcb_filename
            ]
            # Run the commands
            try:
                subprocess.run(gerber_command, check=True, **self._run_extra_args)
            except subprocess.CalledProcessError as e:
                print(f"Command '{' '.join(gerber_command)}' returned non-zero exit status {e.returncode}.")
            try:
                subprocess.run(drill_command, check=True, **self._run_extra_args)
            except subprocess.CalledProcessError as e:
                print(f"Command '{' '.join(drill_command)}' returned non-zero exit status {e.returncode}.")
            # Create ZIP from gerbers
            zip_name = os.path.join(self.outdir, f"{canonical_project_name}-Gerber-{self.revision}")
            if self.verbose:
                print(f"Creating ZIP file '{zip_name}' from gerbers in '{gerber_dir}'")
            shutil.make_archive(zip_name, 'zip', gerber_dir)
            # Delete the gerber directory after creating the ZIP
            shutil.rmtree(gerber_dir)
    
    def find_kicad_pcb_filename(self):
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

def find_kicad_project_files(directory):
    """
    Recursively searches the given directory for files with the '.kicad_pro' extension.

    This function walks through all subdirectories of the given directory and collects
    full paths to all files that end with '.kicad_pro'. It's useful for finding KiCad project files
    in a large directory structure.

    Parameters:
    - directory (str): The root directory path as a string from which the search will begin.

    Returns:
    - list: A list of strings where each string is the full path to a file matching the '.kicad_pro' extension found within the directory or its subdirectories.

    Example usage:
    ---------------
    directory_to_search = '/path/to/your/directory'
    kicad_pro_files = find_kicad_pro_files(directory_to_search)
    for file in kicad_pro_files:
        print(file)

    Note:
    -----
    This function does not follow symbolic links. It's designed to work with filesystem directories only.
    """
    matches = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.kicad_pro'):
                matches.append(os.path.join(root, file))
    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('directory', nargs='?', default=None, type=str, help='The directory to process')
    parser.add_argument('-d', '--discover', type=str, default=None, help='Discover & export all KiCad projects within the given directory.')
    parser.add_argument('-r', '--revision', type=str, default=None, help='Force using a specific revision tag. Defaults to using "git describe --long --tags"')
    parser.add_argument('-o', '--output', type=str, default=".", help='The output directory')
    parser.add_argument('-a', '--attribute', action='append', type=str, help='Extra attributes in the form "key=value"')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    parser.add_argument('--no-step', action='store_true', help='Disable full STEP export')
    parser.add_argument('--no-board-step', action='store_true', help='Disable board-only STEP export')
    parser.add_argument('--no-schematic-pdf', action='store_true', help='Disable schematic PDF export')
    parser.add_argument('--no-pcb-pdf', action='store_true', help='Disable PCB PDF export')
    parser.add_argument('--no-gerber', action='store_true', help='Disable PCB Gerber export')
    parser.add_argument('--no-svg', action='store_true', help='Disable PCB SVG export')
    args = parser.parse_args()

    # args.directory must be given unless --discover
    if args.discover is None and not os.path.isdir(args.directory):
        print(f"The provided directory argument '{args.directory}' is not a directory.")
        exit(1)
        
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        
    # Parse the attributes into a dictionary
    extra_attributes = {}
    if args.attribute:
        for attribute in args.attribute:
            key, value = attribute.split('=')
            extra_attributes[key] = value

    # Which exports are enabled?
    enabled_exports = {
        "step": not args.no_step,
        "schematic_pdf": not args.no_schematic_pdf,
        "pcb_pdf": not args.no_pcb_pdf,
        "gerber": not args.no_gerber,
        "pcb_svg": not args.no_svg,
    }
    
    if args.discover is not None:
        # Discover KiCad projects recursively
        projects = find_kicad_project_files(args.discover)
        if args.verbose:
            print("Discovered the following KiCad projects:")
            for project in projects:
                print(project)
        
        # Export each project
        for project in projects:
            if args.verbose:
                print(f"Exporting project '{project}'")
                
            # Add postfix to output dir: relative path of project
            # compared to discovery directory,
            # so that every project gets its own directory
            outpath = os.path.join(
                args.output,
                os.path.relpath(os.path.dirname(project), args.discover)
            )
            os.makedirs(outpath, exist_ok=True)
                
            exporter = KiCadCIExporter(
                project,
                revision=args.revision,
                verbose=args.verbose,
                outdir=outpath,
                extra_attributes=extra_attributes,
                enabled_exports=enabled_exports
            )
            exporter.export_kicad_project()
        
    else: # not discover 
        # Find the KiCAD project file (.kicad_pro) in the specified directory.
        print(f"Exporting project in '{args.directory}'")
        exporter = KiCadCIExporter(
            args.directory,
            revision=args.revision,
            verbose=args.verbose,
            outdir=args.output,
            extra_attributes=extra_attributes,
            enabled_exports=enabled_exports
        )
        exporter.export_kicad_project()
