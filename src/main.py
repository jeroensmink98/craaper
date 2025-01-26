#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from pathlib import Path
from bib_parser import parse_bibtex_file
from craap_analyzer import CRAAPAnalyzer
from output_formatter import format_results

def main():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Please set OPENAI_API_KEY in your environment or .env file")
    
    # Get input file from command line argument
    import argparse
    parser = argparse.ArgumentParser(description='Perform CRAAP analysis on bibliography entries')
    parser.add_argument('bib_file', type=str, help='Path to the BibTeX file')
    args = parser.parse_args()
    
    # Parse BibTeX file
    entries = parse_bibtex_file(args.bib_file)
    
    # Initialize analyzer
    analyzer = CRAAPAnalyzer()
    
    # Analyze each entry
    results = []
    for entry in entries:
        analysis = analyzer.analyze(entry)
        results.append(analysis)
    
    # Format and display results
    formatted_output = format_results(results)
    print(formatted_output)

if __name__ == "__main__":
    main() 