#!/usr/bin/env python3
import argparse
import os
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from collections import namedtuple

from SExpressions import *

PartCanDeriveFromPart = namedtuple("PartCanDeriveFromPart", ["filename", "a", "b", "similarity"])

def extract_identical_pins_groups(symbols_to_pins_map):
    pins_to_symbols_map = {}
    for symbol, pins in symbols_to_pins_map.items():
        pins_tuple = tuple(sorted(pins))
        if pins_tuple in pins_to_symbols_map:
            pins_to_symbols_map[pins_tuple].append(symbol)
        else:
            pins_to_symbols_map[pins_tuple] = [symbol]

    identical_pins = {pins: symbols for pins, symbols in pins_to_symbols_map.items() if len(symbols) > 1}
    return identical_pins


def process_file(filename) -> list[PartCanDeriveFromPart]:
    tree = read_sexpr(filename)

    symbols_to_pins_map = extract_symbols_to_pins_map(tree)
    symbols_to_graphical_map = extract_symbols_to_graphical_elements_map(tree)
    
    identical_pins = extract_identical_pins_groups(symbols_to_pins_map)
    
    results: list[PartCanDeriveFromPart] = []
    
    for (_pins, parts) in identical_pins.items():
        for i, part_i in enumerate(parts):
            for part_j in parts[i+1:]:
                graphical_i = symbols_to_graphical_map[part_i]
                graphical_j = symbols_to_graphical_map[part_j]
                graphical_i_set = set(graphical_i)
                graphical_j_set = set(graphical_j)

                intersection = graphical_i_set.intersection(graphical_j_set)
                union = graphical_i_set.union(graphical_j_set)

                percentage = len(intersection) / len(union) * 100 if len(union) > 0 else 100.
                if percentage >= 99.0:
                    results.append(PartCanDeriveFromPart(filename, part_i, part_j, percentage))
    return results
    
                    
def print_results(results: list[PartCanDeriveFromPart]):
    for result in results:
        if result.similarity >= 99.9:
            print(f"{os.path.basename(result.filename)}: {result.a} can derive from {result.b}: Identical")
        else:
            print(f"{os.path.basename(result.filename)}: {result.a} can derive from {result.b}: Similarity {result.similarity}%")
    

if __name__ == "__main__":
    # argparse:
    parser = argparse.ArgumentParser(description="Identify identical symbols")
    parser.add_argument("filename", help="Input file or directory")
    args = parser.parse_args()
    
    if os.path.isdir(args.filename):
        with ProcessPoolExecutor() as executor:
            futures = []
            for filename in os.listdir(args.filename):
                if filename.endswith(".kicad_sym"):
                    futures.append(executor.submit(process_file, os.path.join(args.filename, filename)))
            # Print results when they arrive
            for result in concurrent.futures.as_completed(futures):
                print_results(result.result())
    else:
        print_results(process_file(args.filename))
    
