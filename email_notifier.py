# email_notifier.py
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from financial_data import FinancialDataFetcher

class EmailNotifier:
    """Sends email notifications with analysis results."""
    
    def __init__(self, email_config: Dict):
        self.logger = logging.getLogger(__name__)
        self.email_config = email_config
        self.financial_fetcher = FinancialDataFetcher()
        
    def send_analysis_report(self, analysis_results: List, to_email: str) -> bool:
        """Send analysis report via email."""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"LD Micro News Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = self.email_config['from_email']
            msg['To'] = to_email
            
            # Generate HTML content
            html_content = self._generate_html_report(analysis_results)
            text_content = self._generate_text_report(analysis_results)
            
            # Attach both HTML and text versions
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                if self.email_config.get('use_tls', True):
                    server.starttls()
                
                if self.email_config.get('username') and self.email_config.get('password'):
                    server.login(self.email_config['username'], self.email_config['password'])
                
                server.send_message(msg)
            
            self.logger.info(f"Analysis report sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _generate_html_report(self, analysis_results: List) -> str:
        """Generate HTML formatted report, grouped by company."""
        # Filter out results that don't contain meaningful signals
        filtered_results = []
        for result in analysis_results:
            implications = result.get('implications', '').lower()
            summary = result.get('summary', '')
            
            # Skip results with no meaningful signals
            if any(phrase in implications for phrase in [
                'no significant', 'non strategic', 'no strategic', 'no inflection',
                'no earnings', 'no growth', 'no revenue', 'no profit'
            ]):
                continue
                
            # Skip results with placeholder LLM summaries
            if '[LLM SUMMARY' in summary and 'Content:' in summary:
                continue
                
            # Skip results with empty or very short implications
            if not implications or len(implications.strip()) < 10:
                continue
                
            filtered_results.append(result)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .company-section {{ border: 2px solid #3498db; border-radius: 8px; margin: 25px 0; padding: 20px; background-color: #f8f9fa; }}
                .financial-data {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #27ae60; }}
                .signal-card {{ background-color: white; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .signal-type {{ color: #e74c3c; font-weight: bold; margin-bottom: 10px; }}
                .summary {{ color: #2c3e50; margin-bottom: 10px; }}
                .implications {{ color: #8e44ad; margin-bottom: 10px; }}
                .matched-terms {{ margin-top: 10px; }}
                .context {{ color: #7f8c8d; font-style: italic; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 LD Micro News Analysis Report</h1>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Total Companies with Signals: {len(set((r.get('company_name', ''), r.get('ticker', '')) for r in filtered_results))}</p>
                </div>
        """
        # Group results by company (company_name, ticker)
        by_company = {}
        for result in filtered_results:
            key = (result.get('company_name', ''), result.get('ticker', ''))
            if key not in by_company:
                by_company[key] = []
            by_company[key].append(result)
        
        for i, ((company_name, ticker), company_results) in enumerate(by_company.items(), 1):
            # Get financial data using ticker
            financial_data = None
            if ticker:
                financial_data = self.financial_fetcher.get_company_data_by_ticker(ticker)
            html += f"""
                <div class="company-section">
                    <h2>Signal {i}: {company_name}</h2>
            """
            if financial_data:
                market_cap_formatted = self.financial_fetcher.format_market_cap(financial_data.get('market_cap'))
                enterprise_value_formatted = self.financial_fetcher.format_enterprise_value(financial_data.get('enterprise_value'))
                html += f"""
                    <div class="financial-data">
                        <strong>💰 Financial Data:</strong><br>
                        Market Cap: {market_cap_formatted}<br>
                        Enterprise Value: {enterprise_value_formatted}
                    </div>
                """
            
            # Add all signals for this company
            for j, result in enumerate(company_results, 1):
                html += f"""
                    <div class="signal-card">
                        <div class="signal-type">📊 {result.get('agent_category', 'Unknown Signal Type')}</div>
                        <div class="summary">📝 {result.get('summary', 'No summary available')}</div>
                        <div class="implications">💡 Implications: {result.get('implications', 'No implications available')}</div>
                        <p><strong>📅 Date:</strong> {result.get('date', 'Unknown')}</p>
                        <p><strong>🔗 URL:</strong> <a href="{result.get('url', '#')}" target="_blank">{result.get('url', 'No URL available')}</a></p>
                """
                
                # Add matched terms if available
                matched_terms = result.get('matched_terms', [])
                if matched_terms:
                    html += '<div class="matched-terms"><strong>🎯 Matched Terms:</strong><ul>'
                    for match in matched_terms:
                        html += f'<li><strong>{match.get("phrase", "Unknown")}</strong> ({match.get("category", "Unknown")})'
                        if match.get('context'):
                            html += f'<br><span class="context">Context: {match.get("context", "")[:200]}...</span>'
                        html += '</li>'
                    html += '</ul></div>'
                
                html += '</div>'
            
            html += '</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        return html

    def _generate_text_report(self, analysis_results: List) -> str:
        """Generate plain text formatted report, grouped by company."""
        # Filter out results that don't contain meaningful signals
        filtered_results = []
        for result in analysis_results:
            implications = result.get('implications', '').lower()
            summary = result.get('summary', '')
            
            # Skip results with no meaningful signals
            if any(phrase in implications for phrase in [
                'no significant', 'non strategic', 'no strategic', 'no inflection',
                'no earnings', 'no growth', 'no revenue', 'no profit'
            ]):
                continue
                
            # Skip results with placeholder LLM summaries
            if '[LLM SUMMARY' in summary and 'Content:' in summary:
                continue
                
            # Skip results with empty or very short implications
            if not implications or len(implications.strip()) < 10:
                continue
                
            filtered_results.append(result)
        
        text = f"""
LD Micro News Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Companies with Signals: {len(set((r.get('company_name', ''), r.get('ticker', '')) for r in filtered_results))}

"""
        # Group results by company (company_name, ticker)
        by_company = {}
        for result in filtered_results:
            key = (result.get('company_name', ''), result.get('ticker', ''))
            if key not in by_company:
                by_company[key] = []
            by_company[key].append(result)
        for i, ((company_name, ticker), company_results) in enumerate(by_company.items(), 1):
            financial_data = None
            if ticker:
                financial_data = self.financial_fetcher.get_company_data_by_ticker(ticker)
            text += f"Signal {i}: {company_name}\n"
            if financial_data:
                market_cap_formatted = self.financial_fetcher.format_market_cap(financial_data['market_cap'])
                enterprise_value_formatted = self.financial_fetcher.format_enterprise_value(financial_data['enterprise_value'])
                text += f"Market Cap: {market_cap_formatted}\n"
                text += f"Enterprise Value: {enterprise_value_formatted}\n"
            for result in company_results:
                # News summary: use title if available, else first 200 chars of content
                summary = result.get('title', None) or ''
                if not summary and result.get('content'):
                    summary = (result['content'] or '')[:200]
                elif result.get('content') and result['content']:
                    summary += f"\n{result['content'][:200]}"
                text += f"Date: {result.get('date', 'Unknown')}\n"
                text += f"URL: {result.get('url', 'No URL available')}\n"
                text += f"Summary: {summary}\n"
                text += f"Signal Type: {result.get('agent_category', 'Unknown Signal Type')}\n"
                text += f"Implications: {result.get('implications', 'No implications available')}\n"
                if result.get('matched_terms'):
                    text += "Matched Terms:\n"
                    for match in result['matched_terms']:
                        match_text = f"- {match.get('phrase', 'Unknown')} ({match.get('category', 'Unknown')})"
                        if match.get('percentage'):
                            match_text += f" - {match['percentage']}% growth"
                        text += match_text + "\n"
                        if match.get('context'):
                            text += f"  Context: {match['context'][:200]}...\n"
                text += "\n" + "="*50 + "\n\n"
        return text 