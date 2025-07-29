# financial_data.py
import yfinance as yf
import logging
from typing import Dict, Optional
import time

class FinancialDataFetcher:
    """Fetches financial data like market cap and enterprise value for companies using yfinance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_company_data(self, ticker: str) -> Optional[Dict]:
        """Get company data including market cap and enterprise value using yfinance."""
        try:
            if not ticker:
                return None
            
            # Create yfinance ticker object
            ticker_obj = yf.Ticker(ticker)
            
            # Get ticker info
            info = ticker_obj.info
            
            # Extract key financial metrics
            market_cap = info.get("marketCap")
            enterprise_value = info.get("enterpriseValue")
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
            company_name = info.get("longName", info.get("shortName", "Unknown"))
            
            return {
                "ticker": ticker,
                "name": company_name,
                "market_cap": market_cap,
                "enterprise_value": enterprise_value,
                "sector": sector,
                "industry": industry
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching financial data for {ticker}: {str(e)}")
            return None
    
    def get_company_data_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get company data by ticker symbol."""
        return self.get_company_data(ticker)
    
    def format_market_cap(self, market_cap) -> str:
        """Format market cap for display."""
        if market_cap is None or market_cap == "N/A":
            return "N/A"
        
        try:
            market_cap = float(market_cap)
            if market_cap >= 1e12:
                return f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                return f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                return f"${market_cap/1e6:.2f}M"
            else:
                return f"${market_cap:,.0f}"
        except:
            return "N/A"
    
    def format_enterprise_value(self, enterprise_value) -> str:
        """Format enterprise value for display."""
        if enterprise_value is None or enterprise_value == "N/A":
            return "N/A"
        
        try:
            enterprise_value = float(enterprise_value)
            if enterprise_value >= 1e12:
                return f"${enterprise_value/1e12:.2f}T"
            elif enterprise_value >= 1e9:
                return f"${enterprise_value/1e9:.2f}B"
            elif enterprise_value >= 1e6:
                return f"${enterprise_value/1e6:.2f}M"
            else:
                return f"${enterprise_value:,.0f}"
        except:
            return "N/A" 