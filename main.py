# main.py
import pandas as pd
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict
from ld_micro_scraper import LDMicroScraper
from agents.strategic_actions.agent import StrategicActionsAgent
from agents.earnings_inflection.agent import EarningsInflectionAgent
from email_notifier import EmailNotifier
from config import EMAIL_CONFIG, RECIPIENT_EMAIL, SCRAPING_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler()
    ]
)

async def main():
    """Main function to run the LD Micro news analysis."""
    logger = logging.getLogger(__name__)
    logger.info("Starting LD Micro news analysis...")
    
    # Initialize scraper with configuration
    scraper = LDMicroScraper(
        start_date=SCRAPING_CONFIG['start_date'],
        end_date=SCRAPING_CONFIG['end_date'],
        config=SCRAPING_CONFIG
    )
    
    try:
        # Scrape news data
        logger.info("Starting news scraping...")
        news_data = await scraper.scrape_news()
        
        if not news_data:
            logger.warning("No news data found. Exiting.")
            return
        
        logger.info(f"Scraped {len(news_data)} news articles")
        
        # Initialize analysis agents
        strategic_agent = StrategicActionsAgent()
        earnings_agent = EarningsInflectionAgent()
        
        # Analyze each news item
        analysis_results = []
        
        for news_item in news_data:
            logger.info(f"Analyzing: {news_item.get('title', 'Unknown title')[:100]}...")
            
            # Combine title and content for analysis
            full_text = f"{news_item.get('title', '')} {news_item.get('content', '')}"
            
            # Get company info from scraped data
            company_name = news_item.get('company', 'Unknown Company')
            ticker = news_item.get('ticker', '')
            date = news_item.get('published_at', 'Unknown Date')
            url = news_item.get('url', '')
            
            # Analyze with strategic agent
            strategic_result = strategic_agent.analyze_text(
                text=full_text,
                company_name=company_name,
                ticker=ticker,
                date=date,
                url=url
            )
            
            # Analyze with earnings inflection agent
            earnings_result = earnings_agent.analyze_text(
                text=full_text,
                company_name=company_name,
                ticker=ticker,
                date=date,
                url=url
            )
            
            if strategic_result:
                analysis_results.append(strategic_result)
                logger.info(f"Found strategic signals in: {company_name}")
            
            if earnings_result:
                analysis_results.append(earnings_result)
                logger.info(f"Found earnings inflection signals in: {company_name}")
        
        # Generate analysis report
        if analysis_results:
            generate_analysis_report(analysis_results)
            logger.info(f"Analysis complete. Found {len(analysis_results)} significant signals.")
            
            # Send email notification
            send_email_report(analysis_results)
        else:
            logger.info("No significant signals found in the analyzed news.")
            
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)

def send_email_report(analysis_results: List) -> None:
    """Send email report with analysis results."""
    logger = logging.getLogger(__name__)
    
    try:
        notifier = EmailNotifier(EMAIL_CONFIG)
        success = notifier.send_analysis_report(analysis_results, RECIPIENT_EMAIL)
        
        if success:
            logger.info("Email report sent successfully!")
        else:
            logger.error("Failed to send email report.")
            
    except Exception as e:
        logger.error(f"Error sending email report: {str(e)}")

def generate_analysis_report(results: List) -> None:
    """Generate analysis report in markdown and JSON formats."""
    logger = logging.getLogger(__name__)
    
    # Create markdown report
    markdown_content = "# LD Micro News Analysis Report\n\n"
    markdown_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    markdown_content += f"Total signals found: {len(results)}\n\n"
    
    # Group results by agent category
    by_category = {}
    for result in results:
        category = result.get('agent_category', 'Unknown')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(result)
    
    # Generate report for each category
    for category, category_results in by_category.items():
        markdown_content += f"## {category}\n\n"
        markdown_content += f"Found {len(category_results)} signals in this category.\n\n"
        
        for i, result in enumerate(category_results, 1):
            markdown_content += f"### Signal {i}: {result.get('company_name', 'Unknown')} ({result.get('ticker', 'Unknown')})\n\n"
            markdown_content += f"- **Date:** {result.get('date', 'Unknown')}\n"
            markdown_content += f"- **URL:** {result.get('url', 'Unknown')}\n"
            markdown_content += f"- **Implications:** {result.get('implications', 'None')}\n"
            markdown_content += f"- **Summary:** {result.get('summary', 'None')}\n\n"
            
            # Add matched terms
            matched_terms = result.get('matched_terms', [])
            if matched_terms:
                markdown_content += "**Matched Terms:**\n"
                for match in matched_terms:
                    match_text = f"- {match.get('phrase', 'Unknown')} ({match.get('category', 'Unknown')})"
                    if match.get('percentage'):
                        match_text += f" - {match['percentage']}% growth"
                    markdown_content += match_text + "\n"
                    if match.get('context'):
                        markdown_content += f"  - Context: {match['context'][:200]}...\n"
                markdown_content += "\n"
    
    # Save markdown report
    with open('output/analysis_results.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # Save JSON report
    json_results = []
    for result in results:
        json_results.append({
            'company_name': result.get('company_name', 'Unknown'),
            'ticker': result.get('ticker', 'Unknown'),
            'date': result.get('date', 'Unknown'),
            'url': result.get('url', 'Unknown'),
            'agent_category': result.get('agent_category', 'Unknown'),
            'matched_terms': result.get('matched_terms', []),
            'implications': result.get('implications', 'None'),
            'summary': result.get('summary', 'None')
        })
    
    with open('output/analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    logger.info("Analysis reports generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())