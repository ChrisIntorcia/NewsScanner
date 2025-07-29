import os
import logging
from typing import List, Dict

class LLMClient:
    """Client for interacting with an LLM API (Gemini, OpenAI, etc.)."""
    
    def __init__(self, api_key=None, provider='gemini'):
        self.api_key = api_key or os.getenv('LLM_API_KEY')
        self.provider = provider
        self.logger = logging.getLogger(__name__)

    def summarize(self, prompt: str, content: str) -> str:
        """Send content and prompt to the LLM and return the summary (stub)."""
        # TODO: Implement actual API call to Gemini/OpenAI
        # For now, just return a placeholder
        return f"[LLM SUMMARY for prompt: {prompt}\nContent: {content[:200]}...]"
    
    def filter_news_titles(self, titles_and_urls: List[Dict]) -> List[str]:
        """
        Use Gemini to filter news titles and return URLs of interesting articles.
        
        Args:
            titles_and_urls: List of dicts with 'title' and 'url' keys
            
        Returns:
            List of URLs that should be scraped for full content
        """
        try:
            # Create prompt for Gemini
            prompt = self._create_filtering_prompt(titles_and_urls)
            
            # TODO: Implement actual Gemini API call
            # For now, return a simple filter based on keywords
            return self._simple_filter_fallback(titles_and_urls)
            
        except Exception as e:
            self.logger.error(f"Error in Gemini filtering: {str(e)}")
            # Fallback to simple filtering
            return self._simple_filter_fallback(titles_and_urls)
    
    def _create_filtering_prompt(self, titles_and_urls: List[Dict]) -> str:
        """Create a prompt for Gemini to filter news titles."""
        
        # Convert titles to numbered list
        titles_text = ""
        for i, item in enumerate(titles_and_urls, 1):
            titles_text += f"{i}. {item['title']}\n"
        
        prompt = f"""
You are an expert financial analyst. I have a list of news article titles from LD Micro (a small-cap stock news site). 

Please analyze these titles and identify which articles are likely to contain significant financial or strategic information that could impact stock prices.

Look for articles about:
- Earnings announcements and financial results
- Mergers, acquisitions, and partnerships
- New project wins and contract wins
- New product announcements and launches
- New initiatives and strategic developments
- Strategic alternatives and business reviews
- Asset sales and divestitures
- Strong pipelines and growth opportunities
- Major business developments and expansions
- Regulatory approvals or rejections (excluding FDA/clinical trials)

Here are the titles to analyze:

{titles_text}

Please return ONLY the numbers of the articles that are interesting (e.g., "1, 5, 12, 23"). 
If no articles are interesting, return "NONE".

Focus on articles that could have material impact on stock prices or company fundamentals through business growth, revenue opportunities, or strategic positioning.
"""
        return prompt
    
    def _simple_filter_fallback(self, titles_and_urls: List[Dict]) -> List[str]:
        """Simple keyword-based filtering as fallback when Gemini is not available."""
        
        interesting_keywords = [
            # Financial Results
            'earnings', 'financial', 'quarter', 'results', 'revenue', 'profit',
            
            # Strategic Actions
            'acquisition', 'merger', 'partnership', 'deal', 'buyout',
            
            # New Business Wins
            'project win', 'contract win', 'awarded', 'selected', 'chosen',
            'new contract', 'new project', 'deal win', 'partnership win',
            
            # Product & Innovation
            'new product', 'product launch', 'announcement', 'launch',
            'innovation', 'technology', 'platform', 'solution',
            
            # Strategic Initiatives
            'new initiative', 'strategic', 'initiative', 'development',
            'expansion', 'growth', 'opportunity', 'pipeline',
            
            # Business Alternatives
            'strategic alternative', 'business review', 'strategic review',
            'asset sale', 'divestiture', 'spin-off', 'restructuring',
            
            # Pipeline & Growth
            'strong pipeline', 'pipeline', 'growth', 'opportunity',
            'expansion', 'development', 'progress',
            
            # Regulatory (excluding FDA/clinical)
            'regulatory', 'compliance', 'approval', 'clearance',
            
            # Business Developments
            'announcement', 'launch', 'expansion', 'contract',
            'partnership', 'collaboration', 'alliance',
            
            # NEW: Strategic Business Actions (from user request)
            'disposition', 'divestiture', 'acquisition', 'merger', 'spin-off',
            'restructuring', 'reorganization', 'turnaround', 'transformation',
            'pivot', 'strategic shift', 'realignment', 'expansion',
            'consolidation', 'rationalization', 'optimization', 'repositioning',
            'scaling', 'monetization', 'capital allocation', 'portfolio review',
            'strategic review', 'capital raise', 'financing', 'deleveraging',
            'recapitalization', 'write-down', 'impairment', 'asset sale',
            'partnership', 'joint venture', 'licensing', 'breakthrough',
            'market entry', 'geographic expansion', 'vertical integration',
            'horizontal integration', 'product launch', 'disruption',
            'innovation', 'strategic initiative', 'margin expansion',
            'profitability inflection', 'cost restructuring', 'efficiency program',
            'operational leverage', 'strategic exit', 'redeployment',
            'business model change', 'value creation plan',
            
            # NEW: New Business & Customer Terms
            'new customer', 'new client', 'new order', 'new agreement',
            'new deal', 'new partnership', 'new collaboration', 'new market',
            'new territory', 'new service', 'new offering', 'new solution',
            'new technology', 'new platform', 'new division', 'new subsidiary',
            'new joint venture', 'new acquisition', 'new investment', 'new funding',
            
            # NEW: Revenue-related Terms
            'revenue win', 'bookings', 'order backlog', 'purchase order', 'sales contract',
            
            # NEW: Customer-related Terms
            'flagship customer', 'anchor client', 'key account', 'enterprise deal',
            
            # NEW: Expansion-related Terms
            'franchise launch', 'channel partner', 'distribution deal', 'new vertical', 'market penetration',
            
            # NEW: Strategic Initiatives
            'commercial rollout', 'beta launch', 'pilot program', 'scale-up', 'go-to-market',
            
            # NEW: Market & Geography Terms
            'territory expansion', 'regional launch', 'international rollout', 'cross-border deal', 'domestic expansion',
            
            # NEW: Strategic Capital/Deals Terms
            'strategic investment', 'growth capital', 'seed funding', 'venture round', 'equity stake', 'minority investment', 'controlling interest',
            
            # NEW: Competitive Wins Terms
            'vendor of choice', 'rfp award', 'bid win', 'competitive displacement'
        ]
        
        selected_urls = []
        
        for item in titles_and_urls:
            title_lower = item['title'].lower()
            
            # Check if title contains any interesting keywords
            if any(keyword in title_lower for keyword in interesting_keywords):
                selected_urls.append(item['url'])
                
                # Limit to 30 articles for faster testing
                if len(selected_urls) >= 30:
                    break
        
        self.logger.info(f"Simple filter selected {len(selected_urls)} articles out of {len(titles_and_urls)}")
        return selected_urls 