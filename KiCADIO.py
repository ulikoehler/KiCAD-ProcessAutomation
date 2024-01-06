#!/usr/bin/env python3
import pandas as pd
from collections import namedtuple, Counter
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
    
AssemblyPosition = namedtuple("AssemblyPosition", ["x", "y", "rot", "side"])

class MPNMissingError(object):
    def __init__(self, refdes):
        self.refdes = refdes
        
    def __str__(self):
        return f"MPN missing for {self.refdes}"
    
class PositionMissingError(object):
    def __init__(self, refdes):
        self.refdes = refdes
        
    def __str__(self):
        return f"Position missing for {self.refdes}"

class Component(object):
    def __init__(self, refdes, value, mpn, footprint, populate=True, position: AssemblyPosition = None, extra_properties={}):
        self.refdes = refdes
        self.value = value
        self.mpn = mpn
        self.footprint = footprint
        self.populate = populate
        self.position = position
        self.extra_properties = extra_properties
        
    @property
    def errors(self):
        if self.mpn is None:
            self.errors.append(MPNMissingError(self.refdes))
        if self.position is None:
            self.errors.append(PositionMissingError(self.refdes))
            
    @property
    def mpn_or_value(self):
        if self.mpn is None or self.mpn in ["", "NA", "-", "~"]:
            return self.value
        return self.mpn
        
    @property
    def mpn_or_value_plus_footprint(self):
        """
        Returns the MPN if it exists, otherwise returns the value and footprint concatenated with a slash.
        """
        if self.mpn is None or self.mpn in ["", "NA", "-", "~"]:
            return f"{self.value} / {self.footprint}"
        return self.mpn
        
    def asdict(self):
        ret = {
            "Ref": self.refdes,
            "value": self.value,
            "MPN": self.mpn,
            "footprint": self.footprint,
            "populate": self.populate,
        }
        if self.position is not None:
            # Merge dict with dict(self.position)
            ret.update({
                "PosX": self.position.PosX,
                "PosY": self.position.PosY,
                "Rot": self.position.Rot,
                "Side": self.position.Side,
            })
        ret.update(self.extra_properties)
        return ret
            
    def __str__(self):
        return f"Component({self.refdes})"
    
    def __repr__(self) -> str:
        return self.__str__()

def extract_components_from_bom(bom, pnp_positions, extra_properties=[]):
    components = []
    for comp in bom.components.find_all("comp"):
        # Find whether to populate or not (<property name="dnp"/>)
        populate: bool = comp.find("property", {"name": "dnp"}) == None
        # Extract RefDes e.g. <comp ref="BC1">
        refdes: str = comp["ref"]
        # Extract value
        value = text_or_None(comp.find("value"))
        # Extract MPN
        mpn = text_or_None(comp.find("field", {"name": "MPN"}))
        # Extract additional properties
        component_extra_properties = {
            property: value_or_None(comp.find("property", {"name": property}))
            for property in extra_properties
        }
        # Filter None values from extra properties
        component_extra_properties = {
            property: value
            for property, value in component_extra_properties.items()
            if value is not None
        }
        # Extract footprint e.g. <footprint>KKS-Microcontroller-Board:10x10mm Laser Data Matrix</footprint>
        footprint = comp.find("footprint").text
        footprint_lib, _ , footprint_name = footprint.partition(":")
        # Extract positions from PNP file
        try:
            position = pnp_positions.loc[refdes]
        except KeyError:
            position = None
        # Add to component list
        components.append(
            Component(
                refdes=refdes,
                value=value,
                mpn=mpn,
                footprint=footprint_name,
                populate=populate,
                position=position,
                extra_properties=component_extra_properties
            )
        )
    return components

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

def text_or_None(elem):
    """
    Returns the text of an element if it exists, otherwise returns None.
    
    Args:
    elem: An element object.
    
    Returns:
    The text of the element if it exists, otherwise None.
    """
    if elem is None:
        return None
    else:
        return elem.text
    
def value_or_None(elem):
    """
    Returns the value attribute of an element if it exists, otherwise returns None.
    
    Args:
    elem: An element object.
    
    Returns:
    The value of the element if it exists, otherwise None.
    """
    if elem is None:
        return None
    else:
        return elem.get("value", None)

def component_list_to_dataframe(components):
    """
    Convert a list of Component objects to a Pandas DataFrame.
    The "Total count" column is automatically generated.
    """
    
    # Count how many times this specific part is used
    mpn_counter = Counter([c.mpn_or_value_plus_footprint for c in components if c.populate])
    
    # Create data frame from components
    df = pd.DataFrame([c.asdict() for c in components])

    # Build a map of RefDes => total count of this part
    mpn_total_count_by_refdes = {}
    for component in components:
        if not component.populate:
            continue
        mpn = component.mpn_or_value_plus_footprint
        mpn_total_count_by_refdes[component.refdes] = mpn_counter.get(mpn, 0)

    # Add total MPN counter column
    df['Total count'] = df['Ref'].map(lambda ref: mpn_total_count_by_refdes.get(ref, "NaN"))
    return df