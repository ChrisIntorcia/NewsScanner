# analysis_agent_backlog.py
from text_analyzer_base import BaseTextAnalyzer, MatchResult
from typing import List, Dict, Tuple, Optional
import spacy
import logging

class BacklogImpactAgent(BaseTextAnalyzer):
    def __init__(self):
        super().__init__()
        self.agent_name = "Backlog Impact Agent"
        
        # Define search patterns SPECIFIC TO BACKLOG INDICATORS
        self.exact_phrases = {
            "Backlog Levels": [
                "record backlog",
                "Growing Backlog",
                "Unprecedented Backlog",
                "Record High Backlog",
                "Significant Backlog",
                "Increasing Backlog"
            ]
        }
        
        self.bracketed_phrases = {
            "General Backlog Growth": [
                ("record", "backlog"), # Use this as a fallback/conjunction if needed
                ("backlog", "increased"),
                ("backlog", "grew")
            ]
        }
        self.default_proximity = 10 

    def analyze_implications(self, matches: List[Dict[str, str]]) -> str:
        """Analyze the implications SPECIFIC TO BACKLOG IMPACT."""
        implications = []
        for match in matches:
            phrase = match['phrase'].lower()
            if "backlog" in phrase:
                implications.append("Strong indication of **future revenue growth** that is already contracted but not yet recognized.")
                implications.append("Suggests high demand for the company's products/services and strong sales momentum.")
                implications.append("Provides good visibility into **near-term revenue potential** before it appears in official financial statements.")
        return '; '.join(list(set(implications))) if implications else f"No clear implications identified by {self.agent_name}."

    def suggest_next_steps(self, matches: List[Dict[str, str]]) -> str:
        """Suggest next steps SPECIFIC TO BACKLOG IMPACT."""
        next_steps = []
        for match in matches:
            phrase = match['phrase'].lower()
            if "backlog" in phrase:
                next_steps.append("Verify backlog numbers in the next official earnings report or 10-Q filing.")
                next_steps.append("Research typical backlog conversion rates to estimate timing of revenue recognition.")
                next_steps.append("Assess the quality and cancellability of the backlog (e.g., firm orders vs. tentative agreements).")
        return '; '.join(list(set(next_steps))) if next_steps else f"Monitor future press releases for {self.agent_name} commentary."