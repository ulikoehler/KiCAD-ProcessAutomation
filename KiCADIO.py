#!/usr/bin/env python3
import pandas as pd
from collections import namedtuple
import os
from invoke import run
import os.path
import tempfile
from io import StringIO
from bs4 import BeautifulSoup

class AssemblySide(object):
    Top = 0
    Bottom = 1
    Both = 2

def read_kicad_pos_file(filename_or_file):
    pos = pd.read_table(filename_or_file, delim_whitespace=True, names=["Ref", "Val", "Package", "PosX", "PosY", "Rot", "Side"], comment="#")
    pos.set_index("Ref", inplace=True)
    return pos
class KiCADFilenames(namedtuple("Filenames", ["pro", "pcb", "sch"])):
    """
    A class representing the top-level filenames of a KiCAD project.
    """
    def check_files_exist(self):
        """
        Check if all files in the Filenames tuple exist
        """
        for file in self:
            if not os.path.exists(file):
                raise FileNotFoundError(f"{file} does not exist.")
        return True

def kicad_project_filenames(proj_filename) -> KiCADFilenames:
    """
    Given a KiCAD project filename (or path),
    guess the PCB and schematic filenames.
    th, pos_outfile.name)
        pos_outfile.flush()
    """
    prefix, _ = os.path.splitext(proj_filename)
    return KiCADFilenames(
        prefix + ".kicad_pro",
        prefix + ".kicad_pcb",
        prefix + ".kicad_sch"
    )

def export_pos_from_pcb(pcb_filepath, pos_filepath, side=AssemblySide.Top, smd_only=False, exclude_through_hole=True, use_drill_file_origin=True):
    """
    Export position .pos file from a given .kicad_pcb file
    """
    extra_args = ""
    if smd_only:
        extra_args += " --smd-only"
    if exclude_through_hole:
        extra_args += " --exclude-fp-th"
    if side == AssemblySide.Top:
        extra_args += " --side front"
    elif side == AssemblySide.Bottom:
        extra_args += " --side back"
    if use_drill_file_origin:
        extra_args += " --use-drill-file-origin"
    
    cmd = f"kicad-cli pcb export pos '{pcb_filepath}' {extra_args} --units mm -o '{pos_filepath}'"
    print(cmd)
    run(cmd)

def export_bom_xml_from_sch(sch_filepath, xml_filepath):
    """
    Export position .pos file from a given .kicad_pcb file
    """
    run(f"kicad-cli sch export python-bom '{sch_filepath}' -o '{xml_filepath}'")

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

def export_and_read_bom_file(sch_filepath):
    """
    Export position .pos file from a given .kicad_pcb file
    """
    with tempfile.NamedTemporaryFile(mode='w+') as bom_outfile:
        export_bom_xml_from_sch(sch_filepath, bom_outfile.name)
        bom_outfile.flush()
        # Read generated file
        bom_outfile.seek(0)
        bom_data = bom_outfile.read()
        soup = BeautifulSoup(bom_data, 'xml')
        return soup
