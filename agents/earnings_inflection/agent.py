import re
from typing import List, Dict
from agents.earnings_inflection.llm_client import LLMClient
from text_analyzer_base import TextAnalyzerBase

class EarningsInflectionAgent(TextAnalyzerBase):
    """Agent for analyzing financial inflections and explosive growth signals, with LLM support."""
    def __init__(self, use_llm=True, llm_client=None):
        super().__init__("Earnings Inflection & Growth Signals")
        self.use_llm = use_llm
        self.llm_client = llm_client or LLMClient()
        self.inflection_patterns = {
            'explosive_revenue_growth': [
                'revenue grew', 'earnings surged', 'record profit', 'revenue increased',
                'earnings increased', 'profit increased', 'revenue growth', 'earnings growth',
                'profit growth', 'revenue surge', 'earnings surge', 'profit surge',
                'revenue jump', 'earnings jump', 'profit jump'
            ],
            'guidance_updates': [
                'raised guidance', 'updated outlook', 'forecast increased', 'expect strong growth',
                'guidance increase', 'outlook improvement', 'forecast improvement', 'guidance raised',
                'outlook raised', 'forecast raised', 'guidance update', 'outlook update',
                'forecast update', 'guidance revision', 'outlook revision', 'forecast revision'
            ],
            'margin_expansion': [
                'margin expansion', 'further margin improvement', 'margin inflection', 'margins to expand',
                'margin opportunity', 'margin improvement', 'margin enhancement', 'margin growth',
                'margin increase', 'margin strengthening', 'margin optimization', 'margin boost',
                'margin elevation', 'margin acceleration', 'gross margin improvement',
                'operating margin expansion', 'profit margin growth'
            ],
            'structural_improvements': [
                'operating leverage', 'cost leverage', 'automation', 'efficiency gains', 'cost reduction',
                'operational improvement', 'process improvement', 'structural improvement',
                'business model improvement', 'operating model improvement', 'cost structure improvement',
                'efficiency improvement', 'productivity improvement', 'operational excellence',
                'process optimization'
            ]
        }

    def analyze_text(self, text: str, company_name: str, ticker: str, date: str, url: str):
        if self.use_llm:
            prompt = (
                "You are an expert financial analyst. Read the following news article and identify any evidence of "
                "explosive earnings inflection, high revenue growth, margin expansion, or positive guidance. "
                "Summarize the most important inflection in 2 sentences."
            )
            llm_summary = self.llm_client.summarize(prompt, text)
            # Fallback to regex for matched_terms
            matches = self._find_matches(text.lower(), text)
            implications = self._generate_implications(matches, text)
            
            # Generate a meaningful summary based on matched terms
            summary = self._generate_summary_from_matches(matches, text)
            
            return {
                'company_name': company_name,
                'ticker': ticker,
                'date': date,
                'url': url,
                'agent_category': self.agent_name,
                'matched_terms': matches,
                'implications': implications,
                'summary': summary
            }
        else:
            return super().analyze_text(text, company_name, ticker, date, url)

    def _find_matches(self, text_lower: str, original_text: str) -> List[Dict]:
        # ... (same as before, copy from old agent)
        matches = []
        for category, patterns in self.inflection_patterns.items():
            for pattern in patterns:
                pattern_lower = pattern.lower()
                start_pos = 0
                while True:
                    match_pos = text_lower.find(pattern_lower, start_pos)
                    if match_pos == -1:
                        break
                    context = self._extract_context(original_text, match_pos, match_pos + len(pattern))
                    matches.append({
                        'category': category,
                        'phrase': pattern,
                        'context': context,
                        'match_type': 'inflection',
                        'position': match_pos
                    })
                    start_pos = match_pos + 1
        return matches
    def _generate_implications(self, matches: List[Dict], text: str) -> str:
        # ... (same as before, copy from old agent)
        implications = []
        for match in matches:
            category = match.get('category', '')
            phrase = match.get('phrase', '')
            percentage = match.get('percentage', 0)
            if 'explosive_revenue_growth' in category or 'explosive_growth_metrics' in category:
                if percentage >= 40:
                    implications.append(f"Explosive {percentage}% growth indicates strong business momentum and potential for continued expansion.")
                else:
                    implications.append("Revenue growth signals suggest improving business performance.")
            elif 'guidance_updates' in category:
                implications.append("Guidance updates indicate management confidence in future performance.")
            elif 'margin_expansion' in category:
                implications.append("Margin expansion signals suggest operational improvements and pricing strength.")
            elif 'structural_improvements' in category:
                implications.append("Structural improvements indicate fundamental business model enhancements.")
        return " ".join(implications) if implications else "No significant financial inflections identified." 
    
    def _generate_summary_from_matches(self, matches: List[Dict], text: str) -> str:
        """Generate a meaningful summary based on matched earnings terms."""
        if not matches:
            return "No earnings inflection signals identified in this article."
        
        # Group matches by category
        categories = {}
        for match in matches:
            category = match.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(match)
        
        # Generate summary based on the most significant categories
        summary_parts = []
        
        if 'explosive_revenue_growth' in categories:
            summary_parts.append("Explosive revenue growth identified")
        if 'guidance_updates' in categories:
            summary_parts.append("Positive guidance or outlook update")
        if 'margin_expansion' in categories:
            summary_parts.append("Margin expansion or profitability improvement")
        if 'structural_improvements' in categories:
            summary_parts.append("Structural improvement or operational efficiency")
        
        if summary_parts:
            return f"Key earnings signals: {'; '.join(summary_parts)}."
        else:
            return "Earnings inflection or financial improvement identified" 