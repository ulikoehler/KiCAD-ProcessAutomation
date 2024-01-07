#!/usr/bin/env python3
"""
Utilities for directly parsing & serializing S-expressions found in KiCad libraries etc.
"""
from pyparsing import nestedExpr, Word, alphanums, dblQuotedString, OneOrMore, ParserElement

__all__ = ["parse_sexpr", "extract_datasheets"]

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
    for symbol in parsed_data.get('symbol', []):
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

# Example usage
# s_expression = "(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor))"
#lib = parse_sexpr(s_expression)

# Accessing data
# print(lib["version"])  # Should return "20220914"
