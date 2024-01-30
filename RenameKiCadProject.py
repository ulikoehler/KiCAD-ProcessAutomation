#!/usr/bin/env python3
import argparse
import os
import fnmatch
import re

def is_binary(file_path):
    """
    Check if the given file is a binary file or has specific extensions.
    """
    # List of binary file extensions to ignore, in lowercase
    binary_extensions = ['.zip', '.step', '.stp']

    # Get the file extension and convert it to lowercase
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    # Check if the file has a binary extension
    if file_extension in binary_extensions:
        return True

    # Check the content of the file
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(32768)
            return b'\0' in chunk
    except:
        return True

def rename_files(root_dir, old_name, new_name):
    """
    Rename files and replace text within text files.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            # Rename files containing the old project name
            if old_name in filename:
                new_filename = filename.replace(old_name, new_name)
                new_file_path = os.path.join(dirpath, new_filename)
                os.rename(file_path, new_file_path)
                file_path = new_file_path

            # Replace text in text files
            if not is_binary(file_path):
                with open(file_path, 'r+', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    content_new = re.sub(r'(?<=\W)' + re.escape(old_name) + r'(?=\W)', new_name, content)
                    if content_new != content:
                        file.seek(0)
                        file.write(content_new)
                        file.truncate()

def main():
    parser = argparse.ArgumentParser(description='Rename KiCad projects.')
    parser.add_argument('kicad_project_file', type=str, help='Path to the *.kicad_pro file')
    parser.add_argument('new_name', type=str, help='New name for the project')
    args = parser.parse_args()
    
    if " " in args.new_name:
        raise ValueError('The new name must not contain spaces (currently unsupported).')

    kicad_project_path = os.path.abspath(args.kicad_project_file)
    new_name = args.new_name

    if not kicad_project_path.endswith('.kicad_pro'):
        raise ValueError('The provided file must be a .kicad_pro file.')

    project_dir = os.path.dirname(kicad_project_path)
    old_name = os.path.splitext(os.path.basename(kicad_project_path))[0]

    rename_files(project_dir, old_name, new_name)

if __name__ == '__main__':
    main()
