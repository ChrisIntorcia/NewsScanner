# analysis_agent_financial_news.py
import re
from typing import List, Dict
from text_analyzer_base import TextAnalyzerBase

class FinancialNewsAnalysisAgent(TextAnalyzerBase):
    """Comprehensive agent for analyzing various types of financial news and press releases."""
    
    def __init__(self):
        super().__init__("Financial News Analysis")
        
        # Define comprehensive financial patterns
        self.financial_patterns = {
            'earnings_reports': [
                'earnings report',
                'quarterly results',
                'financial results',
                'revenue growth',
                'profit increase',
                'earnings per share',
                'eps growth',
                'quarterly earnings',
                'annual results',
                'financial performance'
            ],
            'guidance_updates': [
                'guidance update',
                'outlook revision',
                'forecast change',
                'earnings guidance',
                'revenue guidance',
                'financial outlook',
                'future expectations',
                'projected results',
                'guidance withdrawal',
                'outlook withdrawal'
            ],
            'operational_updates': [
                'operational update',
                'business update',
                'strategic initiative',
                'cost reduction',
                'restructuring plan',
                'operational efficiency',
                'business transformation',
                'operational improvement',
                'cost savings',
                'efficiency gains'
            ],
            'legal_issues': [
                'class action',
                'securities fraud',
                'investigation',
                'legal proceedings',
                'regulatory action',
                'compliance issue',
                'litigation',
                'legal claim',
                'securities lawsuit',
                'investor lawsuit'
            ],
            'market_reactions': [
                'stock price',
                'share price',
                'market reaction',
                'trading volume',
                'stock decline',
                'price drop',
                'market response',
                'investor reaction',
                'shareholder impact',
                'market impact'
            ],
            'business_developments': [
                'new product',
                'market expansion',
                'acquisition',
                'merger',
                'partnership',
                'strategic alliance',
                'business development',
                'market opportunity',
                'growth initiative',
                'expansion plan'
            ]
        }
    
    def _find_matches(self, text_lower: str, original_text: str) -> List[Dict]:
        """Find comprehensive financial patterns in the text."""
        matches = []
        
        for category, patterns in self.financial_patterns.items():
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
        
        # Look for percentage patterns and financial metrics
        financial_metrics_patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*(increase|decrease|growth|decline|drop|fall|rise)',
            r'(increase|decrease|growth|decline|drop|fall|rise)\s*of\s*(\d+(?:\.\d+)?)\s*%',
            r'\$(\d+(?:\.\d+)?)\s*(million|billion|thousand)',
            r'(\d+(?:\.\d+)?)\s*per\s*share',
            r'revenue\s*(\d+(?:\.\d+)?)\s*(million|billion)',
            r'loss\s*of\s*\$(\d+(?:\.\d+)?)',
            r'profit\s*of\s*\$(\d+(?:\.\d+)?)'
        ]
        
        for pattern in financial_metrics_patterns:
            for match in re.finditer(pattern, text_lower):
                context = self._extract_context(original_text, match.start(), match.end())
                matches.append({
                    'category': 'financial_metrics',
                    'phrase': match.group(0),
                    'context': context,
                    'match_type': 'metric',
                    'position': match.start()
                })
        
        return matches
    
    def _generate_implications(self, matches: List[Dict], text: str) -> str:
        """Generate comprehensive financial implications."""
        implications = []
        
        for match in matches:
            category = match.get('category', '')
            phrase = match.get('phrase', '')
            
            if 'earnings_reports' in category:
                implications.append("Financial performance indicators suggest operational strength or weakness.")
            elif 'guidance_updates' in category:
                implications.append("Management outlook changes indicate business confidence or concerns.")
            elif 'operational_updates' in category:
                implications.append("Operational changes may impact future financial performance and efficiency.")
            elif 'legal_issues' in category:
                implications.append("Legal proceedings could impact company reputation and financial stability.")
            elif 'market_reactions' in category:
                implications.append("Market response reflects investor sentiment and perceived value.")
            elif 'business_developments' in category:
                implications.append("Strategic initiatives may drive future growth and market position.")
            elif 'financial_metrics' in category:
                implications.append("Quantified financial data provides concrete performance indicators.")
        
        return " ".join(implications) if implications else "No specific financial implications identified."
    
    def _generate_next_steps(self, matches: List[Dict], company_name: str) -> str:
        """Generate specific next steps for financial analysis."""
        steps = [
            f"Monitor {company_name} quarterly earnings and management commentary",
            "Track analyst coverage and price target revisions",
            "Review SEC filings for additional details",
            "Analyze peer company performance for industry context",
            "Monitor legal proceedings and regulatory developments"
        ]
        
        return "; ".join(steps) 