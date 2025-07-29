# text_analyzer_base.py
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import nltk
from textblob import TextBlob

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

@dataclass
class MatchResult:
    """Data class to store analysis results."""
    company_name: str
    ticker: str
    date: str
    url: str
    agent_category: str
    matched_terms: List[Dict]
    implications: str
    next_steps: str

class TextAnalyzerBase:
    """Base class for text analysis using simpler NLP approaches."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
    def analyze_text(self, text: str, company_name: str, ticker: str, date: str, url: str) -> Optional[MatchResult]:
        """Analyze text for specific patterns and return results if matches found."""
        if not text:
            return None
            
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Get matches using the specific agent's patterns
        matches = self._find_matches(text_lower, text)
        
        if not matches:
            return None
            
        # Generate implications and next steps
        implications = self._generate_implications(matches, text)
        next_steps = self._generate_next_steps(matches, company_name)
        
        return MatchResult(
            company_name=company_name,
            ticker=ticker,
            date=date,
            url=url,
            agent_category=self.agent_name,
            matched_terms=matches,
            implications=implications,
            next_steps=next_steps
        )
    
    def _find_matches(self, text_lower: str, original_text: str) -> List[Dict]:
        """Find matches in the text. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _find_matches")
    
    def _generate_implications(self, matches: List[Dict], text: str) -> str:
        """Generate financial implications based on matches."""
        implications = []
        
        for match in matches:
            category = match.get('category', 'Unknown')
            term = match.get('phrase', match.get('pattern', 'Unknown'))
            
            if 'pricing' in category.lower() or 'price' in term.lower():
                implications.append("Potential pricing power and margin expansion opportunities.")
            elif 'efficiency' in category.lower() or 'operational' in category.lower():
                implications.append("Operational improvements could drive cost savings and margin expansion.")
            elif 'growth' in category.lower() or 'revenue' in category.lower():
                implications.append("Strong growth indicators suggest revenue acceleration potential.")
            elif 'backlog' in category.lower() or 'order' in category.lower():
                implications.append("Growing backlog indicates strong future revenue visibility.")
            else:
                implications.append(f"Positive signal in {category} category.")
        
        return " ".join(implications) if implications else "No specific financial implications identified."
    
    def _generate_next_steps(self, matches: List[Dict], company_name: str) -> str:
        """Generate recommended next steps for analysis."""
        steps = [
            f"Monitor {company_name} for follow-up announcements",
            "Review quarterly earnings for confirmation of trends",
            "Analyze peer company performance for industry context",
            "Track management commentary on earnings calls"
        ]
        
        return "; ".join(steps)
    
    def _extract_context(self, text: str, match_start: int, match_end: int, context_window: int = 100) -> str:
        """Extract context around a match."""
        start = max(0, match_start - context_window)
        end = min(len(text), match_end + context_window)
        
        context = text[start:end].strip()
        
        # Clean up context
        context = re.sub(r'\s+', ' ', context)
        context = context.replace('\n', ' ')
        
        return context
    
    def _simple_sentence_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenization using regex."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using TextBlob."""
        blob = TextBlob(text)
        return [phrase for phrase in blob.noun_phrases if len(phrase.split()) >= 2]