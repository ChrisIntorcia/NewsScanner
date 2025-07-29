# analysis_agent_growth_inflection.py
from text_analyzer_base import BaseTextAnalyzer, MatchResult
from typing import List, Dict, Tuple, Optional
import spacy
import logging

class GrowthInflectionAgent(BaseTextAnalyzer):
    def __init__(self):
        super().__init__()
        self.agent_name = "Growth & Inflection Points Agent"
        
        # Define search patterns SPECIFIC TO GROWTH & INFLECTION POINTS
        self.exact_phrases = {
            "Pivotal Events": [
                "inflection point",
                "our first earnings call",
                "our first earnings call since",
                "first ever earnings call",
                "first capital markets day",
                "first investor day"
            ]
        }
        
        self.bracketed_phrases = {
            "Strategic Opportunities": [
                ("transformational", "opportunity"),
                ("transformational", "agreement") # Lowercase for consistency
            ]
        }
        self.default_proximity = 10 

    def analyze_implications(self, matches: List[Dict[str, str]]) -> str:
        """Analyze the implications SPECIFIC TO GROWTH & INFLECTION POINTS."""
        implications = []
        for match in matches:
            phrase = match['phrase'].lower()
            if "inflection point" == phrase:
                implications.append("Suggests a **pivotal moment** that could lead to accelerated revenue growth or improved business model efficiency.")
                implications.append("Indicates management's strong belief in a **significant positive change** in future financial performance.")
            elif "first earnings call" in phrase or "first investor day" in phrase or "first capital markets day" in phrase:
                implications.append("Signals new transparency or a formal re-engagement with the market, potentially leading to **increased investor interest and valuation**.")
                implications.append("Opportunity for the company to reset expectations or unveil new strategic direction.")
            elif "transformational opportunity" in phrase or "transformational agreement" in phrase:
                implications.append("Points to a potentially **game-changing event** (e.g., M&A, major partnership, new market entry) that could fundamentally alter the company's prospects.")
                implications.append("High potential for **significant revenue growth** or **market share expansion**.")
        return '; '.join(list(set(implications))) if implications else f"No clear implications identified by {self.agent_name}."

    def suggest_next_steps(self, matches: List[Dict[str, str]]) -> str:
        """Suggest next steps SPECIFIC TO GROWTH & INFLECTION POINTS."""
        next_steps = []
        for match in matches:
            phrase = match['phrase'].lower()
            if "inflection point" == phrase:
                next_steps.append("Monitor upcoming news and earnings for confirmation of the strategic shift's impact.")
                next_steps.append("Re-evaluate long-term growth forecasts based on the implied change.")
            elif "first earnings call" in phrase or "first investor day" in phrase or "first capital markets day" in phrase:
                next_steps.append("Listen to the recording or read the transcript of the mentioned call immediately.")
                next_steps.append("Assess new guidance, management tone, and any unveiled strategic initiatives.")
            elif "transformational opportunity" in phrase or "transformational agreement" in phrase:
                next_steps.append("Investigate the specifics of the opportunity/agreement (partners, terms, market impact).")
                next_steps.append("Quantify potential revenue or market share gains implied by the transformation.")
        return '; '.join(list(set(next_steps))) if next_steps else f"Monitor future press releases for {self.agent_name} commentary."