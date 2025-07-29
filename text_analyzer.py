import re
from typing import List, Dict, Set, Tuple, Optional, Union, Any
import spacy
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MatchResult:
    company_name: str
    date: str
    url: str
    matched_terms: List[Dict[str, str]]
    context: str
    implications: str
    next_steps: str

class TextAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define search patterns
        self.exact_phrases = {
            "Financial Performance": [
                "reintroduced guidance",
                "strategic pricing actions",
                "pricing increases",
                "increase in gross profit pricing",
                "record backlog",
                "Growing Backlog",
                "Unprecedented Backlog",
                "Record High Backlog",
                "Significant Backlog",
                "Increasing Backlog",
                "our first earnings call",
                "our first earnings call since",
                "first ever earnings call",
                "first capital markets day",
                "first investor day",
                "inflection point"
            ],
            "Operational Shifts": [
                "Moving asset-light model",
                "Outsourcing the manufacturing",
                "shift to asset-light",
                "fully automated manufacturing",
                "automation of our manufacturing process"
            ]
        }
        
        # Define bracketed phrases with their proximity requirements
        self.bracketed_phrases = {
            "Financial Performance": [
                ("margins", "will", "increase", "over", "time"),
                ("transformational", "opportunity"),
                ("Transformational", "Agreement")
            ],
            "Operational Shifts": [
                ("Moving", "asset-light", "model"),
                ("Outsourcing", "manufacturing"),
                ("shift", "asset-light"),
                ("fully", "automated", "manufacturing"),
                ("automation", "manufacturing", "process")
            ]
        }
        
        # Default proximity for bracketed phrases
        self.default_proximity = 10

    def extract_company_name(self, text: str) -> str:
        """Extract company name from text using NLP."""
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text
        return "Unknown Company"

    def find_exact_matches(self, text: str) -> List[Dict[str, str]]:
        """Find exact phrase matches in text."""
        matches = []
        for category, phrases in self.exact_phrases.items():
            for phrase in phrases:
                if phrase.lower() in text.lower():
                    # Get context (2 sentences before and after)
                    sentences = text.split('.')
                    for i, sentence in enumerate(sentences):
                        if phrase.lower() in sentence.lower():
                            start = max(0, i - 2)
                            end = min(len(sentences), i + 3)
                            context = '. '.join(sentences[start:end])
                            matches.append({
                                'category': category,
                                'phrase': phrase,
                                'context': context,
                                'match_type': 'exact'
                            })
        return matches

    def find_proximity_matches(self, text: str) -> List[Dict[str, str]]:
        """Find matches based on word proximity patterns."""
        matches = []
        text_lower = text.lower()
        words = text_lower.split()
        
        for category, phrases in self.bracketed_phrases.items():
            for phrase_tuple in phrases:
                # Convert phrase tuple to lowercase for case-insensitive matching
                phrase_words = [word.lower() for word in phrase_tuple]
                
                # Find all positions of each word in the text
                word_positions = {}
                for i, word in enumerate(words):
                    for phrase_word in phrase_words:
                        if phrase_word in word:
                            if phrase_word not in word_positions:
                                word_positions[phrase_word] = []
                            word_positions[phrase_word].append(i)
                
                # Check if all words are present
                if len(word_positions) == len(phrase_words):
                    # Find the smallest window containing all words
                    for pos_list in word_positions.values():
                        for pos in pos_list:
                            window_start = max(0, pos - self.default_proximity)
                            window_end = min(len(words), pos + self.default_proximity + 1)
                            window = words[window_start:window_end]
                            
                            # Check if all words are in the window
                            if all(any(phrase_word in w for w in window) for phrase_word in phrase_words):
                                # Get context (2 sentences before and after)
                                sentences = text.split('.')
                                for i, sentence in enumerate(sentences):
                                    if any(phrase_word in sentence.lower() for phrase_word in phrase_words):
                                        start = max(0, i - 2)
                                        end = min(len(sentences), i + 3)
                                        context = '. '.join(sentences[start:end])
                                        matches.append({
                                            'category': category,
                                            'phrase': ' '.join(phrase_tuple),
                                            'context': context,
                                            'match_type': 'proximity'
                                        })
                                        break
        return matches

    def analyze_implications(self, matches: List[Dict[str, str]]) -> str:
        """Analyze the implications of the matches."""
        implications = []
        for match in matches:
            phrase = match['phrase'].lower()
            if 'backlog' in phrase:
                implications.append("Strong indication of future revenue growth")
            elif 'guidance' in phrase:
                implications.append("Management confidence in future performance")
            elif 'pricing' in phrase:
                implications.append("Potential margin expansion")
            elif 'automation' in phrase or 'asset-light' in phrase:
                implications.append("Potential operational efficiency improvements")
            elif 'transformational' in phrase:
                implications.append("Potential major strategic shift")
            elif 'margins' in phrase and 'increase' in phrase:
                implications.append("Expected margin improvement")
        return '; '.join(implications) if implications else "No clear implications identified"

    def suggest_next_steps(self, matches: List[Dict[str, str]]) -> str:
        """Suggest next steps for analysis."""
        next_steps = []
        for match in matches:
            phrase = match['phrase'].lower()
            if 'backlog' in phrase:
                next_steps.append("Verify backlog numbers in next earnings report")
            elif 'guidance' in phrase:
                next_steps.append("Compare guidance with historical performance")
            elif 'pricing' in phrase:
                next_steps.append("Analyze margin trends over last 4 quarters")
            elif 'automation' in phrase or 'asset-light' in phrase:
                next_steps.append("Review operational metrics and efficiency gains")
            elif 'transformational' in phrase:
                next_steps.append("Investigate strategic initiatives and partnerships")
        return '; '.join(next_steps) if next_steps else "Monitor future press releases"

    def analyze_news_item(self, news_item: Dict) -> Optional[MatchResult]:
        """Analyze a single news item for matches."""
        text = f"{news_item['title']} {news_item['content']}"
        
        # Find all matches
        exact_matches = self.find_exact_matches(text)
        proximity_matches = self.find_proximity_matches(text)
        all_matches = exact_matches + proximity_matches
        
        if not all_matches:
            return None
            
        company_name = self.extract_company_name(text)
        implications = self.analyze_implications(all_matches)
        next_steps = self.suggest_next_steps(all_matches)
        
        return MatchResult(
            company_name=company_name,
            date=news_item['date'],
            url=news_item['url'],
            matched_terms=all_matches,
            context=text[:500] + "...",  # First 500 characters for context
            implications=implications,
            next_steps=next_steps
        )

    def analyze_news_items(self, news_items: List[Dict]) -> List[MatchResult]:
        """Analyze multiple news items."""
        results = []
        for item in news_items:
            result = self.analyze_news_item(item)
            if result:
                results.append(result)
        return results 