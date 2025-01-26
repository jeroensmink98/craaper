#!/usr/bin/env python3

import pandas as pd
from tabulate import tabulate
from typing import List
from craap_analyzer import CRAAPScore

def format_results(results: List[CRAAPScore]) -> str:
    """Format CRAAP analysis results into a readable table"""
    
    # Create DataFrame for the main scores
    scores_df = pd.DataFrame([
        {
            'Citation': result.entry_citation,
            'Currency': f"{result.currency:.2f}" + ("*" if result.currency_confidence < 0.7 else ""),
            'Relevance': f"{result.relevance:.2f}" + ("*" if result.relevance_confidence < 0.7 else ""),
            'Authority': f"{result.authority:.2f}" + ("*" if result.authority_confidence < 0.7 else ""),
            'Accuracy': f"{result.accuracy:.2f}" + ("*" if result.accuracy_confidence < 0.7 else ""),
            'Purpose': f"{result.purpose:.2f}" + ("*" if result.purpose_confidence < 0.7 else ""),
            'Total': f"{result.get_total_score():.2f}",
            'Category': result.get_category()
        }
        for result in results
    ])
    
    # Create detailed explanations
    explanations = []
    for result in results:
        total_score = result.get_total_score()
        category = result.get_category()
        explanations.extend([
            f"\nDetailed Analysis for {result.entry_citation}:",
            f"Total Score: {total_score:.2f} - Category: {category}",
            f"Currency ({result.currency:.2f}): {result.currency_explanation}",
            f"Relevance ({result.relevance:.2f}): {result.relevance_explanation}",
            f"Authority ({result.authority:.2f}): {result.authority_explanation}",
            f"Accuracy ({result.accuracy:.2f}): {result.accuracy_explanation}",
            f"Purpose ({result.purpose:.2f}): {result.purpose_explanation}",
            "-" * 80
        ])
    
    # Combine table and explanations
    output = [
        "CRAAP Test Analysis Results",
        "=" * 80,
        "",
        "Scoring Categories:",
        "45-50: Excellent",
        "40-44: Good",
        "35-39: Average",
        "30-34: Borderline",
        "<30: Unreliable, not suitable for use",
        "",
        tabulate(scores_df, headers='keys', tablefmt='grid', showindex=False),
        "",
        "Note: Scores marked with * indicate lower confidence (< 0.7) in the assessment",
        "",
        "Detailed Explanations:",
        *explanations
    ]
    
    return "\n".join(output) 