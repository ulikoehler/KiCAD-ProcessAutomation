#!/usr/bin/env python3
"""
Utilities for directly parsing & serializing S-expressions found in KiCad libraries etc.
"""
from pyparsing import nestedExpr, Word, alphanums, dblQuotedString, OneOrMore, ParserElement
from collections import namedtuple

__all__ = [
    "parse_sexpr", "read_sexpr", "extract_datasheets", "Pin",
    "extract_symbols_to_pins_map", "extract_graphical_texts",
    "extract_graphical_rectangles", "extract_graphical_polylines",
    "extract_symbols_to_graphical_elements_map"
]

Pin = namedtuple('Pin', ['name', 'number', 'type', 'rotation', 'x', 'y'])

GraphicalText = namedtuple("GraphicalText", ["text", "x", "y", "rotation"])
GraphicalRectangle = namedtuple("GraphicalRectangle", ["start", "end", "fill"])
GraphicalPolyline = namedtuple("GraphicalPolyline", ["points"])

def read_sexpr(filename_or_filelike):
    """
    Read the given filename or file-like object
    and perform parse_sexpr on it
    """
    if isinstance(filename_or_filelike, str):
        with open(filename_or_filelike, "r", encoding="utf-8") as fin:
            return parse_sexpr(fin.read())
    else:
        return parse_sexpr(filename_or_filelike.read())

def parse_sexpr(sexpr):
    """
    Parses a given S-expression string into a nested dictionary structure.

    The function handles S-expressions commonly found in configurations and data representation, 
    like those used in KiCad symbol libraries. It supports nested structures and differentiates 
    between named and unnamed (unnamed) attributes. The parser is capable of handling nested 
    lists within the S-expression and converting them into a hierarchical dictionary format.

    Parameters:
    sexpr (file-like or str): Data representing the S-expression to be parsed. The S-expression is 
                 expected to be in a format where nested lists are enclosed in parentheses '()',
                 and each list can contain both words and numbers. Words can be regular text or 
                 double-quoted strings.

    Returns:
    dict: A nested dictionary representing the parsed S-expression. Each key in the dictionary 
          corresponds to the first element of a list in the S-expression. The values are either 
          strings, numbers, lists, or other dictionaries, depending on the structure of the 
          S-expression. Unnamed (positional) attributes within a list are stored in a list under 
          the key 'positional'.

    Example:
    Given the S-expression: 
    "(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor))", 
    the function will return:
    {'version': {'positional': ['20220914']},
    'generator': {'positional': ['kicad_symbol_editor']},
    'positional': ['kicad_symbol_lib']}

    The function is robust and can handle complex nested structures, making it suitable for 
    parsing detailed configurations and data representations in S-expression format.

    Notes:
    - The function uses 'pyparsing' for parsing the S-expression.
    - It automatically handles whitespace, including newlines and tabs, as delimiters.
    - The parser is designed to be flexible and can handle various forms of S-expressions, 
      but it expects a well-formed input according to the S-expression syntax.

    Raises:
    ParseException: If the input string is not a well-formed S-expression.
    """
    ParserElement.setDefaultWhitespaceChars(' \t\r\n')

    # Define the grammar elements
    word = Word(alphanums + '_-.:/?=&') | dblQuotedString.setParseAction(lambda t: t[0][1:-1])
    token = nestedExpr(opener='(', closer=')', content=OneOrMore(word))

    # Parse the expression
    if isinstance(sexpr, str):
        parsed_data = token.parseString(sexpr, parseAll=True).asList()
    else: # Assume file-like object
        parsed_data = token.parse_file(sexpr, parseAll=True).asList()

    # Convert parsed data to dictionary
    def to_dict(lst):
        d = {}
        for i, item in enumerate(lst):
            if isinstance(item, list):
                # Check if the first item in the list is a string
                if isinstance(item[0], str):
                    key = item[0]
                    value = to_dict(item[0:])
                    # If this is "just a string", replace it by a string
                    if set(value.keys()) == {"tag", "positional"}:
                        value = value["positional"]
                        # If value is a list with only one item, replace it by the item
                        if len(value) == 1:
                            value = value[0]
                    if key in d: # Handle keys with multiple values
                        if not isinstance(d[key], list):
                            d[key] = [d[key]]
                        d[key].append(value)
                    else:
                        d[key] = value
                else:
                    positional = [to_dict(sub_item) for sub_item in item]
                    d.setdefault('positional', []).extend(positional)
            else: # String attribute
                # Handle the first unnamed value differently
                if i == 0:
                    d['tag'] = item
                else:
                    d.setdefault('positional', []).append(item)
        return d
    
    return to_dict(parsed_data[0]) # Parse the root element

def extract_datasheets(parsed_data):
    """
    Extracts datasheets from KiCad symbol library data.

    Args:
        parsed_data (dict): Parsed data containing symbols and properties.

    Returns:
        dict: A dictionary mapping symbol names to datasheet URLs.
    """
    assert isinstance(parsed_data, dict), "parsed_data must be a dictionary"
    assert parsed_data.get('tag') == 'kicad_symbol_lib', "parsed_data must be a KiCad symbol library"
    datasheets = {}
    symbols = parsed_data.get('symbol', [])
    # If there is only a single symbol, emulate a list
    if isinstance(symbols, dict):
        symbols = [symbols]
    for symbol in symbols:
        assert symbol.get('positional') is not None, "symbol must have positional data"
        assert len(symbol['positional']) > 0, "symbol must have at least one positional item"
        symbol_name = symbol["positional"][0]
        assert symbol.get('property') is not None, "symbol must have property data"
        properties = symbol.get('property', [])
        for prop in properties:
            if prop.get('tag') == 'property' and 'Datasheet' in prop.get('positional', []):
                datasheet_url = prop['positional'][1]  # Get the URL, which is the second item in the 'positional' list
                datasheets[symbol_name] = datasheet_url
    return datasheets

def extract_symbols_to_pins_map(tree) -> dict[str, Pin]:
    symbol_to_pins_map = {}
    
    symbols = tree.get('symbol', [])

    # If there is only a single symbol, emulate a list
    if isinstance(symbols, dict):
        symbols = [symbols]
    for symbol in symbols:
        assert symbol.get('positional') is not None, "symbol must have positional data"
        assert len(symbol['positional']) > 0, "symbol must have at least one positional item"
        symbol_name = symbol["positional"][0]
        assert symbol.get('property') is not None, "symbol must have property data"

        extends = symbol.get("extends")
        # Skip extended symbols
        if extends is not None:
            # Skip this symbol
            continue
        # Iterate sub-symbols which contain the pins
        subsymbols = symbol.get("symbol")
        if not isinstance(subsymbols, list):
            subsymbols = [subsymbols]
            
        current_symbol_pins = []
        
        for subsymbol in subsymbols:
            if "pin" in subsymbol:
                # Iterate pins
                pins = subsymbol["pin"]
                if not isinstance(pins, list):
                    pins = [pins]
                for pin in pins:
                    pin_type = pin["positional"][0] # e.g. 'passive'
                    x, y, rotation = pin["at"]
                    x, y, rotation = float(x), float(y), int(rotation)
                    
                    pin_name = pin["name"]["positional"][0]
                    pin_number = pin["number"]["positional"][0]
                    pin_obj = Pin(pin_name, pin_number, pin_type, rotation, x, y)
                    current_symbol_pins.append(pin_obj)
        
        # Sort pin list by number
        current_symbol_pins.sort(key=lambda x: int(x.number))
        # Add to symbol map
        symbol_to_pins_map[symbol_name] = current_symbol_pins
    return symbol_to_pins_map

def extract_graphical_texts(texts):
    if not isinstance(texts, list):
        texts = [texts]
    graphical_texts = []
    for text in texts:
        text_content = text["positional"][0]
        x, y, rotation = text["at"]
        x, y, rotation = float(x), float(y), int(rotation)
        graphical_texts.append(GraphicalText(text_content, x, y, rotation))
    return graphical_texts

def extract_graphical_rectangles(rectangles):
    if not isinstance(rectangles, list):
        rectangles = [rectangles]
    graphical_rectangles = []
    for rectangle in rectangles:
        start_x, start_y = rectangle["start"]
        end_x, end_y = rectangle["end"]
        start_x, start_y = float(start_x), float(start_y)
        end_x, end_y = float(end_x), float(end_y)
        fill = rectangle.get("fill", {}).get("type")
        graphical_rectangles.append(GraphicalRectangle((start_x, start_y), (end_x, end_y), fill))
    return graphical_rectangles

def extract_graphical_polylines(polylines):
    if not isinstance(polylines, list):
        polylines = [polylines]
    graphical_polylines = []
    for polyline in polylines:
        points = polyline.get("pts", []).get("xy", [])
        if points:
            # First elements of [points] is start x,y coordinate
            # pop those from points
            current_polyline_points = []
            if len(points) >= 2 and isinstance(points[0], str) and isinstance(points[1], str):
                start_x, start_y = float(points.pop(0)), float(points.pop(0))
                current_polyline_points.append((start_x, start_y))
            for xy_pair in points:
                x, y = float(xy_pair[0]), float(xy_pair[1])
                current_polyline_points.append((x, y))
            graphical_polylines.append(GraphicalPolyline(tuple(current_polyline_points)))
    return graphical_polylines

def extract_symbols_to_graphical_elements_map(tree):

    symbols = tree.get('symbol', [])
    
    symbol_to_graphical_map = {}

    # If there is only a single symbol, emulate a list
    if isinstance(symbols, dict):
        symbols = [symbols]
    for symbol in symbols:
        assert symbol.get('positional') is not None, "symbol must have positional data"
        assert len(symbol['positional']) > 0, "symbol must have at least one positional item"
        symbol_name = symbol["positional"][0]
        assert symbol.get('property') is not None, "symbol must have property data"

        extends = symbol.get("extends")
        # Skip extended symbols
        if extends is not None:
            # Skip this symbol
            continue
        # Iterate sub-symbols which contain the pins
        subsymbols = symbol.get("symbol")
        if not isinstance(subsymbols, list):
            subsymbols = [subsymbols]
            
        current_symbol_graphical = []
        
        for subsymbol in subsymbols:
            # Extract texts
            texts = subsymbol.get("text", [])
            current_symbol_graphical += extract_graphical_texts(texts)
            # Extract rectangles
            rectangles = subsymbol.get("rectangle", [])
            current_symbol_graphical += extract_graphical_rectangles(rectangles)
            # Extract polylines
            polylines = subsymbol.get("polyline", [])
            current_symbol_graphical += extract_graphical_polylines(polylines)
            # NOTE: Arcs are currently not processed
            # NOTE: Pins are not processed here
            
            # Sort current_symbol_graphical by str representation
            current_symbol_graphical = sorted(current_symbol_graphical, key=lambda x: str(x))
            
            symbol_to_graphical_map[symbol_name] = current_symbol_graphical
    return symbol_to_graphical_map

# Example usage
# s_expression = "(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor))"
#lib = parse_sexpr(s_expression)

# Accessing data
# print(lib["version"])  # Should return "20220914"
