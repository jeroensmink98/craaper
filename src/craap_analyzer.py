#!/usr/bin/env python3

import os
import json
import hashlib
from datetime import datetime
import openai
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, Dict
from pathlib import Path

@dataclass
class CRAAPScore:
    currency: float
    currency_explanation: str
    currency_confidence: float
    
    relevance: float
    relevance_explanation: str
    relevance_confidence: float
    
    authority: float
    authority_explanation: str
    authority_confidence: float
    
    accuracy: float
    accuracy_explanation: str
    accuracy_confidence: float
    
    purpose: float
    purpose_explanation: str
    purpose_confidence: float
    
    entry_key: str
    entry_citation: str
    
    # Token usage tracking
    input_tokens: int
    output_tokens: int
    cached: bool = False  # Whether this result came from cache

    def get_total_score(self) -> float:
        """Calculate the total CRAAP score (max 50 points)"""
        return self.currency + self.relevance + self.authority + self.accuracy + self.purpose

    def get_category(self) -> str:
        """Get the evaluation category based on total score"""
        total = self.get_total_score()
        if total >= 45:
            return "Excellent"
        elif total >= 40:
            return "Good"
        elif total >= 35:
            return "Average"
        elif total >= 30:
            return "Borderline"
        else:
            return "Unreliable, not suitable for use"
            
    def get_estimated_cost(self) -> float:
        """Calculate estimated cost in USD based on current GPT-4 pricing"""
        if self.cached:
            return 0.0
        # Current GPT-4 pricing (as of 2024): $0.03/1K tokens input, $0.06/1K tokens output
        input_cost = (self.input_tokens / 1000) * 0.03
        output_cost = (self.output_tokens / 1000) * 0.06
        return input_cost + output_cost

class CRAAPAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.cache_dir = Path.home() / ".craaper" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "analysis_cache.json"
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load the cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_cache(self):
        """Save the cache to disk"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _clean_entry(self, entry: Dict) -> Dict:
        """Remove large fields like abstract from the entry"""
        cleaned = entry.copy()
        fields_to_remove = ['abstract', 'Abstract']  # Case variations
        for field in fields_to_remove:
            cleaned.pop(field, None)
        return cleaned
    
    def _compute_entry_hash(self, entry) -> str:
        """Compute a hash for the bibliography entry"""
        # Create a string with all entry fields, excluding abstract
        cleaned_entry = self._clean_entry(entry)
        entry_str = json.dumps(cleaned_entry, sort_keys=True)
        return hashlib.sha256(entry_str.encode()).hexdigest()
    
    def _cache_key(self, entry_hash: str) -> str:
        """Create a cache key for the entry"""
        return f"analysis_{entry_hash}"
    
    def _deserialize_craap_score(self, cached_data: Dict) -> CRAAPScore:
        """Convert cached dictionary back to CRAAPScore object"""
        return CRAAPScore(
            currency=cached_data['currency'],
            currency_explanation=cached_data['currency_explanation'],
            currency_confidence=cached_data['currency_confidence'],
            relevance=cached_data['relevance'],
            relevance_explanation=cached_data['relevance_explanation'],
            relevance_confidence=cached_data['relevance_confidence'],
            authority=cached_data['authority'],
            authority_explanation=cached_data['authority_explanation'],
            authority_confidence=cached_data['authority_confidence'],
            accuracy=cached_data['accuracy'],
            accuracy_explanation=cached_data['accuracy_explanation'],
            accuracy_confidence=cached_data['accuracy_confidence'],
            purpose=cached_data['purpose'],
            purpose_explanation=cached_data['purpose_explanation'],
            purpose_confidence=cached_data['purpose_confidence'],
            entry_key=cached_data['entry_key'],
            entry_citation=cached_data['entry_citation'],
            input_tokens=cached_data.get('input_tokens', 0),
            output_tokens=cached_data.get('output_tokens', 0),
            cached=True
        )

    def _fetch_url_content(self, url):
        """Fetch content from URL if available"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()[:1000]  # Get first 1000 chars
        except:
            return None
    
    def _format_citation_apa7(self, entry):
        """Format entry in APA7 style"""
        authors = entry['author'].split(' and ')
        author_text = authors[0].split(',')[0] if authors else 'Unknown'
        if len(authors) > 1:
            author_text += ' et al.'
        
        year = entry['year'] or 'n.d.'
        return f"{author_text} ({year})"
    
    def analyze(self, entry) -> CRAAPScore:
        """Analyze a single bibliography entry using the CRAAP test"""
        # Clean the entry first
        entry = self._clean_entry(entry)
        
        # Check cache first
        entry_hash = self._compute_entry_hash(entry)
        cache_key = self._cache_key(entry_hash)
        
        if cache_key in self.cache:
            print(f"Using cached analysis for entry: {entry['key']}")
            return self._deserialize_craap_score(self.cache[cache_key])
        
        # If not in cache, perform analysis
        url_content = self._fetch_url_content(entry['url']) if entry['url'] else None
        citation = self._format_citation_apa7(entry)
        
        # Prepare prompt for GPT
        prompt = f"""Analyze this academic source using the CRAAP test criteria. For each criterion, provide:
1. A score from 0.00 to 10.00
2. A brief explanation
3. A confidence score from 0.00 to 1.00 indicating how certain you are about your assessment

Source details:
Title: {entry['title']}
Author(s): {entry['author']}
Year: {entry['year']}
Journal: {entry['journal']}
Publisher: {entry['publisher']}
DOI: {entry['doi']}
URL: {entry['url']}

Additional content from URL: {url_content if url_content else 'Not available'}

Provide your analysis in the following JSON format:
{
    "currency": {
        "score": float,
        "explanation": string,
        "confidence": float
    },
    "relevance": {
        "score": float,
        "explanation": string,
        "confidence": float
    },
    "authority": {
        "score": float,
        "explanation": string,
        "confidence": float
    },
    "accuracy": {
        "score": float,
        "explanation": string,
        "confidence": float
    },
    "purpose": {
        "score": float,
        "explanation": string,
        "confidence": float
    }
}"""

        # Get analysis from GPT
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            max_tokens=1000,
            messages=[
                {"role": "system", "content": "You are a research librarian expert in evaluating academic sources."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get token usage
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Parse response
        analysis = eval(response.choices[0].message.content)
        
        # Create CRAAPScore object
        score = CRAAPScore(
            currency=analysis['currency']['score'],
            currency_explanation=analysis['currency']['explanation'],
            currency_confidence=analysis['currency']['confidence'],
            relevance=analysis['relevance']['score'],
            relevance_explanation=analysis['relevance']['explanation'],
            relevance_confidence=analysis['relevance']['confidence'],
            authority=analysis['authority']['score'],
            authority_explanation=analysis['authority']['explanation'],
            authority_confidence=analysis['authority']['confidence'],
            accuracy=analysis['accuracy']['score'],
            accuracy_explanation=analysis['accuracy']['explanation'],
            accuracy_confidence=analysis['accuracy']['confidence'],
            purpose=analysis['purpose']['score'],
            purpose_explanation=analysis['purpose']['explanation'],
            purpose_confidence=analysis['purpose']['confidence'],
            entry_key=entry['key'],
            entry_citation=citation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached=False
        )
        
        # Cache the results
        self.cache[cache_key] = {
            'currency': score.currency,
            'currency_explanation': score.currency_explanation,
            'currency_confidence': score.currency_confidence,
            'relevance': score.relevance,
            'relevance_explanation': score.relevance_explanation,
            'relevance_confidence': score.relevance_confidence,
            'authority': score.authority,
            'authority_explanation': score.authority_explanation,
            'authority_confidence': score.authority_confidence,
            'accuracy': score.accuracy,
            'accuracy_explanation': score.accuracy_explanation,
            'accuracy_confidence': score.accuracy_confidence,
            'purpose': score.purpose,
            'purpose_explanation': score.purpose_explanation,
            'purpose_confidence': score.purpose_confidence,
            'entry_key': score.entry_key,
            'entry_citation': score.entry_citation,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        }
        self._save_cache()
        
        return score 