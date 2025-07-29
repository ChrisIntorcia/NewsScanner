# analysis_agent_pricing.py
import re
from typing import List, Dict
from text_analyzer_base import TextAnalyzerBase

class PricingAnalysisAgent(TextAnalyzerBase):
    """Specialized agent for analyzing pricing power and margin expansion signals."""
    
    def __init__(self):
        super().__init__("Pricing Power & Margin Expansion")
        
        # Define pricing-related patterns
        self.pricing_patterns = {
            'price_increases': [
                'price increase',
                'price hike',
                'price raise',
                'price adjustment',
                'price optimization',
                'price improvement',
                'price enhancement',
                'price strengthening',
                'price elevation',
                'price boost'
            ],
            'pricing_power': [
                'pricing power',
                'pricing flexibility',
                'pricing strength',
                'pricing advantage',
                'pricing position',
                'pricing capability',
                'pricing authority',
                'pricing leverage'
            ],
            'margin_expansion': [
                'margin expansion',
                'margin improvement',
                'margin enhancement',
                'margin growth',
                'margin increase',
                'margin strengthening',
                'margin optimization',
                'margin boost',
                'margin elevation',
                'margin acceleration'
            ],
            'cost_control': [
                'cost reduction',
                'cost savings',
                'cost optimization',
                'cost efficiency',
                'cost improvement',
                'cost control',
                'cost management',
                'cost structure',
                'cost discipline',
                'cost containment'
            ],
            'operational_efficiency': [
                'operational efficiency',
                'operational improvement',
                'operational optimization',
                'operational excellence',
                'operational performance',
                'operational enhancement',
                'operational streamlining',
                'operational effectiveness'
            ]
        }
    
    def _find_matches(self, text_lower: str, original_text: str) -> List[Dict]:
        """Find pricing and margin-related patterns in the text."""
        matches = []
        
        for category, patterns in self.pricing_patterns.items():
            for pattern in patterns:
                # Find all occurrences of the pattern
                pattern_lower = pattern.lower()
                start_pos = 0
                
                while True:
                    match_pos = text_lower.find(pattern_lower, start_pos)
                    if match_pos == -1:
                        break
                    
                    # Extract context around the match
                    context = self._extract_context(original_text, match_pos, match_pos + len(pattern))
                    
                    matches.append({
                        'category': category,
                        'phrase': pattern,
                        'context': context,
                        'match_type': 'exact',
                        'position': match_pos
                    })
                    
                    start_pos = match_pos + 1
        
        # Also look for percentage patterns (e.g., "10% increase", "15% margin improvement")
        percentage_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(increase|improvement|growth|expansion|enhancement|boost)',
            r'(increase|improvement|growth|expansion|enhancement|boost)\s*of\s*(\d+(?:\.\d+)?)\s*%',
            r'margin\s*(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*%\s*margin'
        ]
        
        for pattern in percentage_patterns:
            for match in re.finditer(pattern, text_lower):
                context = self._extract_context(original_text, match.start(), match.end())
                matches.append({
                    'category': 'percentage_metrics',
                    'phrase': match.group(0),
                    'context': context,
                    'match_type': 'percentage',
                    'position': match.start()
                })
        
        return matches
    
    def _generate_implications(self, matches: List[Dict], text: str) -> str:
        """Generate specific pricing and margin implications."""
        implications = []
        
        for match in matches:
            category = match.get('category', '')
            phrase = match.get('phrase', '')
            
            if 'price_increases' in category or 'price' in phrase.lower():
                implications.append("Strong pricing power indicates potential for margin expansion and revenue growth.")
            elif 'pricing_power' in category:
                implications.append("Pricing flexibility suggests competitive advantages and margin protection.")
            elif 'margin_expansion' in category or 'margin' in phrase.lower():
                implications.append("Margin expansion signals operational improvements and pricing strength.")
            elif 'cost_control' in category or 'cost' in phrase.lower():
                implications.append("Cost control measures support margin expansion and operational efficiency.")
            elif 'operational_efficiency' in category:
                implications.append("Operational efficiency gains can drive margin expansion and competitive advantages.")
            elif 'percentage_metrics' in category:
                implications.append("Quantified improvements suggest measurable operational and financial gains.")
        
        return " ".join(implications) if implications else "No specific pricing or margin implications identified."
    
    def _generate_next_steps(self, matches: List[Dict], company_name: str) -> str:
        """Generate specific next steps for pricing analysis."""
        steps = [
            f"Monitor {company_name} quarterly earnings for margin trends",
            "Track pricing actions and customer retention metrics",
            "Analyze competitive pricing dynamics in the industry",
            "Review cost structure changes and efficiency initiatives",
            "Monitor management commentary on pricing strategy"
        ]
        
        return "; ".join(steps)