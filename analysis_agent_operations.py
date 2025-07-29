# analysis_agent_operations.py
from text_analyzer_base import BaseTextAnalyzer, MatchResult
from typing import List, Dict, Tuple, Optional
import spacy
import logging

class OperationalEfficiencyAgent(BaseTextAnalyzer):
    def __init__(self):
        super().__init__()
        self.agent_name = "Operational Efficiency & Margin Enhancement Agent"
        
        # Define search patterns SPECIFIC TO OPERATIONAL EFFICIENCY
        self.exact_phrases = {} # No exact phrases for this agent
        
        self.bracketed_phrases = {
            "Operational Shifts": [
                ("moving", "asset-light", "model"),
                ("outsourcing", "the", "manufacturing"),
                ("shift", "to", "asset-light"),
                ("fully", "automated", "manufacturing"),
                ("automation", "of", "our", "manufacturing", "process")
            ]
        }
        self.default_proximity = 10 

    def analyze_implications(self, matches: List[Dict[str, str]]) -> str:
        """Analyze the implications SPECIFIC TO OPERATIONAL EFFICIENCY."""
        implications = []
        for match in matches:
            phrase_tuple = tuple(match['phrase'].lower().split()) # Convert string back to tuple for comparison
            
            if phrase_tuple in [("moving", "asset-light", "model"), ("shift", "to", "asset-light")]:
                implications.append("Suggests potential for **cost reduction** by reducing fixed assets and improving capital efficiency.")
                implications.append("Indicates a strategic focus on **improving return on assets (ROA)** and **operational leverage**.")
            elif phrase_tuple in [("outsourcing", "the", "manufacturing")]:
                implications.append("Potential for **reduced overheads** and increased flexibility in production.")
                implications.append("May lead to **gross margin improvement** by offloading manufacturing complexities.")
            elif phrase_tuple in [("fully", "automated", "manufacturing"), ("automation", "of", "our", "manufacturing", "process")]:
                implications.append("Strong indicator of **cost reduction** through labor efficiency and reduced error rates.")
                implications.append("Suggests **improved production scalability** and consistency, leading to potential **gross margin expansion**.")
        return '; '.join(list(set(implications))) if implications else f"No clear implications identified by {self.agent_name}."

    def suggest_next_steps(self, matches: List[Dict[str, str]]) -> str:
        """Suggest next steps SPECIFIC TO OPERATIONAL EFFICIENCY."""
        next_steps = []
        for match in matches:
            phrase_tuple = tuple(match['phrase'].lower().split())

            if phrase_tuple in [("moving", "asset-light", "model"), ("shift", "to", "asset-light")]:
                next_steps.append("Examine capital expenditures (CapEx) for reductions and changes in asset intensity.")
                next_steps.append("Review management commentary on operational restructuring and efficiency gains.")
            elif phrase_tuple in [("outsourcing", "the", "manufacturing")]:
                next_steps.append("Analyze COGS (Cost of Goods Sold) and supply chain costs in future financial reports.")
                next_steps.append("Investigate terms of outsourcing agreements and potential risks.")
            elif phrase_tuple in [("fully", "automated", "manufacturing"), ("automation", "of", "our", "manufacturing", "process")]:
                next_steps.append("Look for updates on automation project timelines and expected cost savings.")
                next_steps.append("Assess the impact on production capacity and quality control.")
        return '; '.join(list(set(next_steps))) if next_steps else f"Monitor future press releases for {self.agent_name} commentary."