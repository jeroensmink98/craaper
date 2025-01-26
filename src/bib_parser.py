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
        # Allow all entry types by setting common_strings to False
        parser.ignore_nonstandard_types = False
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    
    total_entries = len(bib_database.entries)
    print(f"\nFound {total_entries} entries in {file_path}")
    
    # Normalize entries
    entries = []
    for entry in bib_database.entries:
        print(f"Processing entry: {entry.get('ID', '')}")
        # Include all entries regardless of type
        normalized_entry = {
            'key': entry.get('ID', ''),
            'title': entry.get('title', ''),
            'author': entry.get('author', ''),
            'year': entry.get('date', entry.get('year', '')).split('-')[0] if entry.get('date') else '',  # Handle date field and extract year
            'url': entry.get('url', ''),
            'journal': entry.get('journal', entry.get('booktitle', '')),  # Use booktitle as fallback
            'publisher': entry.get('publisher', entry.get('institution', '')),  # Use institution as fallback
            'doi': entry.get('doi', ''),
            'type': entry.get('ENTRYTYPE', 'unknown'),
            'abstract': entry.get('abstract', ''),
            'keywords': entry.get('keywords', ''),
            'note': entry.get('note', '')
        }
        entries.append(normalized_entry)
    
    print(f"Successfully processed {len(entries)} entries\n")
    return entries 