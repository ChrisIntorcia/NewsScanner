import re
from typing import List, Dict
from agents.strategic_actions.llm_client import LLMClient
from text_analyzer_base import TextAnalyzerBase

class StrategicActionsAgent(TextAnalyzerBase):
    """Agent for analyzing strategic inflection points and transformational opportunities, with LLM support."""
    def __init__(self, use_llm=True, llm_client=None):
        super().__init__("Strategic Actions & Inflection Points")
        self.use_llm = use_llm
        self.llm_client = llm_client or LLMClient()
        self.strategic_patterns = {
            'pricing_power': [
                'strategic pricing actions', 'pricing increases', 'increase in gross profit pricing', 'pricing power',
                'pricing flexibility', 'pricing strength', 'pricing advantage', 'pricing position', 'pricing capability',
                'pricing authority', 'pricing leverage'
            ],
            'new_products': [
                'new product launch', 'new platform', 'new service', 'product launch', 'platform launch',
                'service launch', 'new offering', 'new solution', 'new technology', 'new innovation',
                'new development', 'new release', 'new version', 'new model', 'new system'
            ],
            'inflection_points': [
                'inflection point', 'transformational opportunity', 'transformational agreement', 'transformational change',
                'transformational moment', 'transformational shift', 'transformational deal', 'transformational partnership',
                'transformational growth', 'transformational impact', 'strategic inflection', 'business inflection',
                'market inflection', 'growth inflection', 'revenue inflection'
            ],
            'structural_shifts': [
                'moving asset-light model', 'shift to asset-light', 'outsourcing the manufacturing',
                'automation of our manufacturing process', 'fully automated manufacturing', 'margins will increase over time',
                'structural improvement', 'structural change', 'structural shift', 'business model transformation',
                'operating model change', 'manufacturing automation', 'process automation', 'digital transformation',
                'operational transformation'
            ],
            'margin_expansion': [
                'margin expansion', 'margin improvement', 'margin enhancement', 'margin growth', 'margin increase',
                'margin strengthening', 'margin optimization', 'margin boost', 'margin elevation', 'margin acceleration',
                'gross margin improvement', 'operating margin expansion', 'profit margin growth', 'margin leverage',
                'margin potential'
            ],
            # NEW: Asset Transactions
            'asset_transactions': [
                'disposition', 'divestiture', 'asset sale', 'spin-off', 'restructuring', 'reorganization',
                'strategic exit', 'redeployment', 'portfolio review', 'strategic review'
            ],
            # NEW: Competitive Wins
            'competitive_wins': [
                'vendor of choice', 'rfp award', 'bid win', 'competitive displacement', 'awarded', 'selected',
                'chosen', 'project win', 'contract win', 'deal win'
            ],
            # NEW: Geographic Expansion
            'geographic_expansion': [
                'territory expansion', 'regional launch', 'international rollout', 'cross-border deal',
                'domestic expansion', 'new market', 'new territory', 'geographic expansion'
            ],
            # NEW: Strategic Capital
            'strategic_capital': [
                'strategic investment', 'growth capital', 'seed funding', 'venture round', 'equity stake',
                'minority investment', 'controlling interest', 'capital raise', 'financing'
            ],
            # NEW: Revenue Wins
            'revenue_wins': [
                'revenue win', 'bookings', 'order backlog', 'purchase order', 'sales contract',
                'new customer', 'new client', 'new order', 'new agreement', 'new deal'
            ],
            # NEW: Business Development
            'business_development': [
                'new partnership', 'new collaboration', 'joint venture', 'licensing', 'breakthrough',
                'market entry', 'vertical integration', 'horizontal integration'
            ],
            # NEW: Strategic Initiatives
            'strategic_initiatives': [
                'commercial rollout', 'beta launch', 'pilot program', 'scale-up', 'go-to-market',
                'franchise launch', 'channel partner', 'distribution deal', 'new vertical'
            ]
        }

    def analyze_text(self, text: str, company_name: str, ticker: str, date: str, url: str):
        if self.use_llm:
            prompt = (
                "You are an expert financial analyst. Read the following news article and identify any evidence of "
                "strategic inflection points, pricing power, new product launches, or structural shifts. "
                "Summarize the most important strategic action or inflection in 2 sentences."
            )
            llm_summary = self.llm_client.summarize(prompt, text)
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
    
    def _generate_summary_from_matches(self, matches: List[Dict], text: str) -> str:
        """Generate a meaningful summary based on matched strategic terms."""
        if not matches:
            return "No strategic signals identified in this article."
        
        # Group matches by category
        categories = {}
        for match in matches:
            category = match.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(match)
        
        # Generate summary based on the most significant categories
        summary_parts = []
        
        if 'asset_transactions' in categories:
            summary_parts.append("Strategic asset transaction identified")
        if 'competitive_wins' in categories:
            summary_parts.append("Competitive win or market positioning signal")
        if 'geographic_expansion' in categories:
            summary_parts.append("Geographic expansion or market entry")
        if 'strategic_capital' in categories:
            summary_parts.append("Strategic capital activity or investment")
        if 'revenue_wins' in categories:
            summary_parts.append("Revenue win or customer acquisition")
        if 'business_development' in categories:
            summary_parts.append("Business development or partnership activity")
        if 'strategic_initiatives' in categories:
            summary_parts.append("Strategic initiative or operational execution")
        if 'new_products' in categories:
            summary_parts.append("New product or service launch")
        if 'margin_expansion' in categories:
            summary_parts.append("Margin expansion or operational improvement")
        if 'pricing_power' in categories:
            summary_parts.append("Pricing power or strategic pricing action")
        
        if summary_parts:
            return f"Key strategic signals: {'; '.join(summary_parts)}."
        else:
            return "Strategic business development identified"

    def _find_matches(self, text_lower: str, original_text: str) -> List[Dict]:
        matches = []
        for category, patterns in self.strategic_patterns.items():
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
                        'match_type': 'strategic',
                        'position': match_pos
                    })
                    start_pos = match_pos + 1
        return matches
    def _generate_implications(self, matches: List[Dict], text: str) -> str:
        implications = []
        for match in matches:
            category = match.get('category', '')
            phrase = match.get('phrase', '')
            if 'pricing_power' in category or 'pricing' in phrase.lower():
                implications.append("Strategic pricing actions indicate potential for margin expansion and revenue growth.")
            elif 'new_products' in category or 'product' in phrase.lower():
                implications.append("New product launches suggest growth opportunities and market expansion potential.")
            elif 'inflection_points' in category or 'inflection' in phrase.lower():
                implications.append("Inflection point language suggests transformational business opportunities.")
            elif 'structural_shifts' in category or 'structural' in phrase.lower():
                implications.append("Structural shifts indicate fundamental business model improvements and margin expansion potential.")
            elif 'margin_expansion' in category or 'margin' in phrase.lower():
                implications.append("Margin expansion signals suggest operational improvements and pricing strength.")
            # NEW: Asset Transactions
            elif 'asset_transactions' in category:
                implications.append("Asset transactions indicate strategic portfolio optimization and capital reallocation opportunities.")
            # NEW: Competitive Wins
            elif 'competitive_wins' in category:
                implications.append("Competitive wins demonstrate market strength and validate business positioning.")
            # NEW: Geographic Expansion
            elif 'geographic_expansion' in category:
                implications.append("Geographic expansion signals growth opportunities and market penetration potential.")
            # NEW: Strategic Capital
            elif 'strategic_capital' in category:
                implications.append("Strategic capital activities indicate financial flexibility and growth investment capacity.")
            # NEW: Revenue Wins
            elif 'revenue_wins' in category:
                implications.append("Revenue wins demonstrate business momentum and customer acquisition success.")
            # NEW: Business Development
            elif 'business_development' in category:
                implications.append("Business development activities suggest strategic partnerships and market expansion.")
            # NEW: Strategic Initiatives
            elif 'strategic_initiatives' in category:
                implications.append("Strategic initiatives indicate operational execution and growth acceleration potential.")
        return " ".join(implications) if implications else "No strategic inflection points identified." 