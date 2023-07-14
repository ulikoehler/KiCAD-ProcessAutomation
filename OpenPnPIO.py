#!/usr/bin/env python3
from collections import namedtuple
import xml.etree.ElementTree as ET
import xml.dom.minidom

PlacementPosition = namedtuple("PlacementPosition", ["x", "y", "z", "rotation"])
DefaultPlacementPosition = PlacementPosition(0.0, 0.0, 0.0, 0.0)

# namedtuple Placement with attributes Ref, Position, Side, PartID, Enabled
Placement = namedtuple("Placement", ["ref", "position", "side", "part_id", "enabled"])

def create_placement(placements, placement: Placement):
    """
    Create a placement subelement in the given placements element,
    parameterized by the given Placement object.
    """
    # Create the placement element
    placement_element = ET.SubElement(placements, "placement")
    placement_element.set("version", "1.4")
    placement_element.set("id", placement.ref)
    placement_element.set("side", placement.side.capitalize())
    placement_element.set("part-id", placement.part_id)
    placement_element.set("type", "Placement")
    placement_element.set("enabled", str(placement.enabled))

    # Create the location element
    location = ET.SubElement(placement_element, "location")
    location.set("units", "Millimeters")
    location.set("x", str(placement.position.x))
    location.set("y", str(placement.position.y))
    location.set("z", str(placement.position.z))
    location.set("rotation", str(placement.position.rotation))
    
    # Create the error-handling element
    error_handling = ET.SubElement(placement_element, "error-handling")
    error_handling.text = "Alert"

def create_board(name, board_position: PlacementPosition, placements: list[Placement]) -> str:
    """
    Create an OpenPnP board XML string from a list of Placement objects.
    """
    # Create the root element
    root = ET.Element("openpnp-board")
    root.set("version", "1.1")
    root.set("name", name)

    # Create the dimensions element
    dimensions = ET.SubElement(root, "dimensions")
    dimensions.set("units", "Millimeters")
    dimensions.set("x", str(board_position.x))
    dimensions.set("y", str(board_position.y))
    dimensions.set("z", str(board_position.z))
    dimensions.set("rotation", str(board_position.rotation))

    # Create the placements element
    placements_element = ET.SubElement(root, "placements")
    
    # Add placements
    for placement in placements:
        create_placement(placements_element, placement)

    # Print the XML
    xml_string = ET.tostring(root, encoding="unicode")
    xml_pretty = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="    ")
    return xml_pretty.strip()
