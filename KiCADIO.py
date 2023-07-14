#!/usr/bin/env python3
import pandas as pd
import enum
from invoke import run
import os.path
import tempfile
from io import StringIO

def read_kicad_pos_file(filename_or_file):
    pos = pd.read_table(filename_or_file, delim_whitespace=True, names=["Ref", "Val", "Package", "PosX", "PosY", "Rot", "Side"], comment="#")
    pos.set_index("Ref", inplace=True)
    return pos

def pcb_and_sch_filenames(proj_filename):
    """
    Given a KiCAD project filename (or path),
    guess the PCB and schematic filenames.
    th, pos_outfile.name)
        pos_outfile.flush()
    """
    prefix, _ = os.path.splitext(proj_filename)
    return prefix + ".kicad_pcb", prefix + ".kicad_sch"

def export_pos_from_pcb(pcb_filepath, pos_filepath):
    """
    Export position .pos file from a given .kicad_pcb file
    """
    run(f"kicad-cli pcb export pos '{pcb_filepath}' --units mm -o '{pos_filepath}'")

def export_bom_xml_from_pcb(pcb_filepath, pos_filepath):
    """
    Export position .pos file from a given .kicad_pcb file
    """
    run(f"kicad-cli pcb export pos '{pcb_filepath}' --units mm -o '{pos_filepath}'")

def export_and_read_position_file(pcb_filepath):
    """
    Export position .pos file from a given .kicad_pcb file
    """
    with tempfile.NamedTemporaryFile(mode='w+') as pos_outfile:
        export_pos_from_pcb(pcb_filepath, pos_outfile.name)
        pos_outfile.flush()
        # Read generated file
        pos_outfile.seek(0)
        pos_data = pos_outfile.read()
        return read_kicad_pos_file(StringIO(pos_data))
