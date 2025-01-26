#!/usr/bin/env python3

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

def parse_bibtex_file(file_path):
    """
    Parse a BibTeX file and return a list of entries.
    
    Args:
        file_path (str): Path to the BibTeX file
        
    Returns:
        list: List of bibliography entries with normalized fields
    """
    with open(file_path) as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    
    # Normalize entries
    entries = []
    for entry in bib_database.entries:
        normalized_entry = {
            'key': entry.get('ID', ''),
            'title': entry.get('title', ''),
            'author': entry.get('author', ''),
            'year': entry.get('year', ''),
            'url': entry.get('url', ''),
            'journal': entry.get('journal', ''),
            'publisher': entry.get('publisher', ''),
            'doi': entry.get('doi', ''),
        }
        entries.append(normalized_entry)
    
    return entries 