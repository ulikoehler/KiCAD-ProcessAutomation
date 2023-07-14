#!/usr/bin/env python3
"""
Compare two KiCAD PCB files:
Check, for all components, if:
- the position has changed
- the rotation has changed
- the side has changed
- the component is new or has been removed
"""
import argparse
from KiCADIO import *
import enum

# enum.IntEnum of what changed
class ChangeType(enum.IntEnum):
    Value = 1
    Package = 2
    Position = 3
    Rotation = 4
    Side = 5
    
class Change(object):
    def __init__(self, ref, changetype, old, new):
        self.ref = ref
        self.changetype = changetype
        self.old = old
        self.new = new
    def __str__(self):
        return f"[{self.ref}]: {self.changetype.name} change: {self.old} -> {self.new}"
    def __repr__(self) -> str:
        return self.__str__()

def compare_component_entries(ref, comp1, comp2):
    """
    Compare two component entries from a KiCAD position file
    """
    changes = []
    if comp1["Val"] != comp2["Val"]:
        changes.append(Change(ref, ChangeType.Value, comp1["Val"], comp2["Val"]))
    if comp1["Package"] != comp2["Package"]:
        changes.append(Change(ref, ChangeType.Package, comp1["Package"], comp2["Package"]))
    if comp1["PosX"] != comp2["PosX"] or comp1["PosY"] != comp2["PosY"]:
        changes.append(Change(ref, ChangeType.Position, (comp1["PosX"], comp1["PosY"]), (comp2["PosX"], comp2["PosY"])))
    if comp1["Rot"] != comp2["Rot"]:
        changes.append(Change(ref, ChangeType.Rotation, comp1["Rot"], comp2["Rot"]))
    if comp1["Side"] != comp2["Side"]:
        changes.append(Change(ref, ChangeType.Side, comp1["Side"], comp2["Side"]))
    return changes

def compare_pcbs(old, new):
    # Extract list of refdes from both PCBs
    old_refdes = set(old.index)
    new_refdes = set(new.index)
    # Compute intersection, union and difference
    common_refdes = old_refdes & new_refdes
    added_refdes = new_refdes - old_refdes
    removed_refdes = old_refdes - new_refdes
    # Compare common refdes
    ignore = [ChangeType.Value]
    changes = []
    for ref in common_refdes:
        comp1 = old.loc[ref]
        comp2 = new.loc[ref]
        changes += compare_component_entries(ref, comp1, comp2)
    changes = [change for change in changes if change.changetype not in ignore]
    # Sort changes by changetype, then by refdes
    changes.sort(key=lambda change: (change.changetype, change.ref))

    return changes
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare two KiCAD files')
    parser.add_argument('old', type=str, help='path to old KiCAD PCB')
    parser.add_argument('new', type=str, help='path to new KiCAD PCB')
    args = parser.parse_args()

    # Get filenames of old & new PCBs
    old_pcb = args.old
    new_pcb = args.new
    
    # If the user gave a project file instead of a PCB file, try to guess the PCB filename
    if old_pcb.endswith(".kicad_pro") or old_pcb.endswith(".pro"):
        old_pcb = os.path.splitext(old_pcb)[0] + ".kicad_pcb"
        print(f"Guesing old PCB filename from project file: {old_pcb}")
    if new_pcb.endswith(".kicad_pro") or new_pcb.endswith(".pro"):
        new_pcb = os.path.splitext(new_pcb)[0] + ".kicad_pcb"
        print(f"Guesing new PCB filename from project file: {old_pcb}")
    
    # Export position files and read them into pandas DataFrames
    old_pos = export_and_read_position_file(old_pcb)
    new_pos = export_and_read_position_file(new_pcb)
    
    changes = compare_pcbs(old_pos, new_pos)
    
    for change in changes:
        print(change)