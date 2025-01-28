#!/usr/bin/env python3

import pandas as pd
from tabulate import tabulate
from typing import List
from craap_analyzer import CRAAPScore
from pathlib import Path

def export_to_csv(results: List[CRAAPScore], output_dir: str = "output"):
    """Export CRAAP analysis results to CSV files"""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create combined scores and explanations DataFrame
    combined_df = pd.DataFrame([
        {
            'Citation': result.entry_citation,
            # Scores
            'Currency_Score': result.currency,
            'Currency_Confidence': result.currency_confidence,
            'Currency_Explanation': result.currency_explanation,
            
            'Relevance_Score': result.relevance,
            'Relevance_Confidence': result.relevance_confidence,
            'Relevance_Explanation': result.relevance_explanation,
            
            'Authority_Score': result.authority,
            'Authority_Confidence': result.authority_confidence,
            'Authority_Explanation': result.authority_explanation,
            
            'Accuracy_Score': result.accuracy,
            'Accuracy_Confidence': result.accuracy_confidence,
            'Accuracy_Explanation': result.accuracy_explanation,
            
            'Purpose_Score': result.purpose,
            'Purpose_Confidence': result.purpose_confidence,
            'Purpose_Explanation': result.purpose_explanation,
            
            'Total_Score': result.get_total_score(),
            'Category': result.get_category()
        }
        for result in results
    ])
    combined_df.to_csv(output_path / "craap_analysis.csv", index=False)
    
    # Create usage statistics DataFrame
    usage_df = pd.DataFrame([
        {
            'Citation': result.entry_citation,
            'Input_Tokens': result.input_tokens,
            'Output_Tokens': result.output_tokens,
            'Total_Tokens': result.input_tokens + result.output_tokens,
            'Estimated_Cost': result.get_estimated_cost(),
            'Cached': result.cached
        }
        for result in results
    ])
    usage_df.to_csv(output_path / "usage_stats.csv", index=False)
    
    return output_path

def format_results(results: List[CRAAPScore], output_format: str = "text") -> str:
    """Format CRAAP analysis results into a readable table or export to CSV"""
    
    if output_format == "csv":
        output_path = export_to_csv(results)
        return f"\nResults have been exported to CSV files in the {output_path} directory:\n" + \
               f"- {output_path}/craap_analysis.csv: Complete CRAAP analysis (scores, confidence levels, and explanations)\n" + \
               f"- {output_path}/usage_stats.csv: Token usage and cost statistics"
    
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
    
    # Calculate total token usage and costs
    total_input_tokens = sum(result.input_tokens for result in results)
    total_output_tokens = sum(result.output_tokens for result in results)
    total_cost = sum(result.get_estimated_cost() for result in results)
    cached_results = sum(1 for result in results if result.cached)
    
    # Create token usage and cost summary
    usage_summary = [
        "\nToken Usage and Cost Summary:",
        f"Total Input Tokens: {total_input_tokens:,}",
        f"Total Output Tokens: {total_output_tokens:,}",
        f"Total Tokens: {total_input_tokens + total_output_tokens:,}",
        f"Estimated Cost: ${total_cost:.4f}",
        f"Results from Cache: {cached_results}/{len(results)}",
    ]
    
    # Create detailed explanations
    explanations = []
    for result in results:
        total_score = result.get_total_score()
        category = result.get_category()
        cache_status = "(Cached)" if result.cached else f"(Tokens: {result.input_tokens + result.output_tokens:,}, Cost: ${result.get_estimated_cost():.4f})"
        explanations.extend([
            f"\nDetailed Analysis for {result.entry_citation} {cache_status}:",
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
        *usage_summary,
        "",
        "Detailed Explanations:",
        *explanations
    ]
    
    return "\n".join(output) 