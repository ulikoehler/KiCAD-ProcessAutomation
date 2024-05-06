#!/usr/bin/env python3
import argparse
import os
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from collections import namedtuple

from SExpressions import *

PartCanDeriveFromPart = namedtuple("PartCanDeriveFromPart", ["a", "b", "similarity"])

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
    
    results = []
    
    for (pins, parts) in identical_pins.items():
        for i in range(len(parts)):
            for j in range(i+1, len(parts)):
                part_i = parts[i]
                part_j = parts[j]
                graphical_i = symbol_to_graphical_map[part_i]
                graphical_j = symbol_to_graphical_map[part_j]
                graphical_i_set = set(graphical_i)
                graphical_j_set = set(graphical_j)

                intersection = graphical_i_set.intersection(graphical_j_set)
                union = graphical_i_set.union(graphical_j_set)

                percentage = len(intersection) / len(union) * 100
                if percentage >= 99.0:
                    results.append(PartCanDeriveFromPart(part_i, part_j, percentage))
    return result
    
                    
def print_results(results: list[PartCanDeriveFromPart]):
    for result in results:
        if result.similarity >= 99.9:
            print(f"{result.a} can derive from {result.b}: Identical")
        else:
            print(f"{result.a} can derive from {result.b}: Similarity {result.similarity}%")
    

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
                print_results(results)
    else:
        print_results(process_file(args.filename))
    