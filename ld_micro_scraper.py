# ld_micro_scraper.py
import asyncio
import logging
from playwright.async_api import async_playwright
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from llm.llm_client import LLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class LDMicroScraper:
    """Scrapes news articles from LD Micro's news archive using intelligent filtering."""
    
    def __init__(self, start_date: str, end_date: str, max_articles: int = 10, config: Dict = None):
        self.start_date = start_date
        self.end_date = end_date
        self.max_articles = max_articles
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.llm_client = LLMClient()
        
    async def scrape_news(self) -> List[Dict]:
        """Scrape news articles from LD Micro using intelligent filtering."""
        async with async_playwright() as p:
            # Set up browser with user agent
            browser = await p.chromium.launch(headless=True)
            self.logger.info("Playwright browser initialized.")
            
            context = await browser.new_context(
                user_agent=self.config.get('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            )
            page = await context.new_page()
            
            try:
                all_news_items = []
                
                # Generate list of dates to scrape
                from datetime import datetime, timedelta
                end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
                start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
                
                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    self.logger.info(f"Scraping news for date: {date_str}")
                    
                    # Navigate to the news page for this date
                    url = f"https://www.ldmicro.com/news/{date_str}"
                    await page.goto(url, wait_until='networkidle', timeout=self.config.get('timeout', 30000))
                    
                    # Wait for the page to load
                    await page.wait_for_load_state('domcontentloaded')
                    self.logger.info(f"Page DOM loaded for {date_str}")
                    
                    # Phase 1: Extract all titles and URLs (fast)
                    all_titles_and_urls = await self._extract_all_titles_and_urls(page)
                    self.logger.info(f"Extracted {len(all_titles_and_urls)} titles and URLs for {date_str}")
                    
                    # Phase 2: Use Gemini to filter interesting articles
                    selected_urls = self.llm_client.filter_news_titles(all_titles_and_urls)
                    self.logger.info(f"Gemini selected {len(selected_urls)} articles for detailed scraping")
                    
                    # Phase 3: Only scrape content for selected articles
                    processed_items = await self._scrape_selected_articles(page, all_titles_and_urls, selected_urls)
                    
                    all_news_items.extend(processed_items)
                    
                    # Move to next date
                    current_date += timedelta(days=1)
                
                # Save raw data
                self._save_raw_data(all_news_items)
                
                return all_news_items
                
            except Exception as e:
                self.logger.error(f"Error during scraping: {str(e)}")
                return []
            finally:
                await context.close()
                self.logger.info("Playwright context closed.")
                await browser.close()
                self.logger.info("Playwright browser closed.")
    
    async def _extract_all_titles_and_urls(self, page) -> List[Dict]:
        """Extract all titles and URLs from the page table (fast, no content scraping)."""
        try:
            # Try different table selectors
            table_selectors = [
                "table.table",
                "table",
                ".table",
                "table tbody",
                "[class*='table']"
            ]
            
            table_found = False
            selector = None
            for sel in table_selectors:
                try:
                    await page.wait_for_selector(sel, timeout=5000)
                    self.logger.info(f"Found table with selector: {sel}")
                    table_found = True
                    selector = sel
                    break
                except:
                    continue
            
            if not table_found:
                self.logger.warning("No table found, trying to extract any structured data")
                return await self._extract_fallback_data(page)
            
            # Get all rows in the table
            rows = await page.query_selector_all(f"{selector} tbody tr")
            if not rows:
                rows = await page.query_selector_all(f"{selector} tr")
            
            self.logger.info(f"Found {len(rows)} rows in the news table")
            
            titles_and_urls = []
            for row in rows:
                try:
                    # Extract cells from the row
                    cells = await row.query_selector_all("td")
                    if len(cells) >= 5:  # Expecting Date/Time, Premium, Symbol, Company, News Release
                        # Extract ticker from the third cell (Symbol column)
                        ticker_cell_text = await cells[3].inner_text()
                        ticker = ticker_cell_text.strip()
                        
                        # Extract company name from the fourth cell (Company column)
                        company_cell_text = await cells[4].inner_text()
                        company_name = company_cell_text.strip()
                        
                        # If company name is empty or just the ticker, try to get it from the title
                        if not company_name or company_name == ticker:
                            title_cell = cells[-1]
                            title_cell_text = await title_cell.inner_text()
                            company_name = self._extract_company_from_title(title_cell_text, ticker)
                        
                        # Extract title/link from the last cell (News Release column)
                        title_cell = cells[-1]
                        title_cell_text = await title_cell.inner_text()
                        
                        # Get the link
                        url = ""
                        link_element = await title_cell.query_selector("a")
                        if link_element:
                            url = await link_element.get_attribute("href")
                            if url and not url.startswith("http"):
                                url = f"https://www.ldmicro.com{url}"
                        
                        item = {
                            'company': company_name,
                            'ticker': ticker,
                            'title': title_cell_text.strip(),
                            'url': url
                        }
                        
                        titles_and_urls.append(item)

                except Exception as e:
                    self.logger.warning(f"Error extracting row: {str(e)}")
                    continue
                
            self.logger.info(f"Extracted {len(titles_and_urls)} titles and URLs")
            return titles_and_urls
            
        except Exception as e:
            self.logger.error(f"Error extracting titles and URLs: {str(e)}")
            return []
    
    async def _scrape_selected_articles(self, page, all_titles_and_urls: List[Dict], selected_urls: List[str]) -> List[Dict]:
        """Scrape full content only for articles selected by Gemini."""
        processed_items = []
        
        # Create a mapping of URL to full item data
        url_to_item = {item['url']: item for item in all_titles_and_urls}
        
        for i, url in enumerate(selected_urls, 1):
            try:
                # Add delay between requests to be respectful
                if i > 1:
                    delay = self.config.get('delay_between_requests', 2)
                    self.logger.info(f"Waiting {delay} seconds before next request...")
                    await asyncio.sleep(delay)
                
                # Get the item data for this URL
                item = url_to_item.get(url)
                if not item:
                    self.logger.warning(f"Item not found for URL: {url}")
                    continue
                
                processed_item = await self._process_news_item(page, item, i)
                if processed_item:
                    processed_items.append(processed_item)
                    
            except Exception as e:
                self.logger.error(f"Error processing selected article {i}: {str(e)}")
                continue
        
        return processed_items
    
    async def _extract_fallback_data(self, page) -> List[Dict]:
        """Extract data when table structure is not found."""
        try:
            # Try to find any links that might be news articles
            links = await page.query_selector_all("a[href*='news'], a[href*='press'], a[href*='release']")
            
            news_items = []
            for link in links[:self.max_articles]:
                try:
                    href = await link.get_attribute("href")
                    text = await link.inner_text()
                    
                    if href and text:
                        # Try to extract company and ticker from the text
                        company_info = self._parse_company_and_ticker(text)
                        
                        news_items.append({
                            'company': company_info['company'],
                            'ticker': company_info['ticker'],
                            'date': 'Unknown Date',
                            'title': text.strip(),
                            'url': href if href.startswith('http') else f"https://www.ldmicro.com{href}"
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Error extracting fallback link: {str(e)}")
                    continue
                
            self.logger.info(f"Extracted {len(news_items)} news items from fallback method")
            return news_items

        except Exception as e:
            self.logger.error(f"Error in fallback extraction: {str(e)}")
            return []
    
    def _parse_company_and_ticker(self, company_text: str) -> Dict[str, str]:
        """Parse company name and ticker from the company cell text."""
        # Remove extra whitespace and newlines
        company_text = re.sub(r'\s+', ' ', company_text.strip())
        
        # Look for ticker pattern (usually in parentheses or brackets)
        ticker_match = re.search(r'[\(\[]([A-Z]{1,5})[\)\]]', company_text)
        ticker = ticker_match.group(1) if ticker_match else ""
        
        # Remove ticker from company name
        company_name = re.sub(r'\s*[\(\[][A-Z]{1,5}[\)\]](?:\s*\([^)]*\))?', '', company_text).strip()
        
        return {
            'company': company_name,
            'ticker': ticker
        }
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date from the date cell."""
        try:
            # Clean up the date text
            date_text = date_text.strip()
            # You might need to adjust this based on the actual date format
            return date_text
        except:
            return "Unknown Date"
    
    async def _process_news_item(self, page, item: Dict, index: int) -> Optional[Dict]:
        """Process a single news item to get full content."""
        try:
            self.logger.info(f"Processing item {index}: {item.get('title', 'No title')[:50]}...")
            
            if not item['url']:
                self.logger.warning(f"No URL for item {index}")
                return None
            
            # Navigate to the article page
            await page.goto(item['url'], wait_until='networkidle')
            
            # Extract the article content
            content_selector = ".article-content, .content, .post-content, article"
            content_element = await page.query_selector(content_selector)
            
            content = ""
            if content_element:
                content = await content_element.inner_text()
            else:
                # Fallback: try to get all text from the page
                body = await page.query_selector("body")
                if body:
                    content = await body.inner_text()
            
            # Clean up the content
            content = self._clean_content(content)
            
            # Use current date if date is not available
            date = item.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            processed_item = {
                'company': item['company'],
                'ticker': item['ticker'],
                'title': item['title'],
                'content': content,
                'url': item['url'],
                'published_at': date
            }
            
            self.logger.info(f"Successfully processed article {index}: {item['company']} ({item['ticker']}) - {item['title'][:50]}...")
            return processed_item
            
        except Exception as e:
            self.logger.error(f"Error processing article {index}: {str(e)}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Clean up the article content."""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common page elements
        content = re.sub(r'LD Micro.*?News', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Home.*?News', '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def _save_raw_data(self, news_items: List[Dict]) -> None:
        """Save raw news data to JSON and CSV files."""
        try:
            # Save as JSON
            json_filename = f"output/ld_micro_news_may_2025.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Raw news data saved to {json_filename}")
            
            # Save as CSV
            csv_filename = f"output/ld_micro_news_may_2025.csv"
            if news_items:
                fieldnames = news_items[0].keys()
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(news_items)
                self.logger.info(f"Raw news data saved to {csv_filename}")
            
            self.logger.info(f"Saved {len(news_items)} news items to files")
            
        except Exception as e:
            self.logger.error(f"Error saving raw data: {str(e)}")
            self.logger.error(f"News items count: {len(news_items)}")
            if news_items:
                self.logger.error(f"First item keys: {list(news_items[0].keys())}")

    def _extract_company_from_title(self, title: str, ticker: str) -> str:
        """Extract company name from the title text."""
        # Common company name mappings
        company_mappings = {
            'DBI': 'Designer Brands Inc.',
            'RCKT': 'Rocket Pharmaceuticals Inc.',
            'IRBT': 'iRobot Corporation',
            'CAPR': 'Capricor Therapeutics Inc.',
            'DDD': '3D Systems Corporation',
            'RXST': 'RxSight Inc.'
        }
        
        # If we have a mapping for this ticker, use it
        if ticker in company_mappings:
            return company_mappings[ticker]
        
        # Try to extract from title
        # Look for patterns like "Company Name Inc." or "Company Name Corporation"
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.|Corporation|Corp\.|Company|Ltd\.))',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Inc)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Corp)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
        
        # Fallback: return ticker with "Corporation" suffix
        return f"{ticker} Corporation"

def main():
    """Main function for testing the scraper."""
    import asyncio
    
    scraper = LDMicroScraper(
        start_date="2025-07-15",
        end_date="2025-07-20",
        max_articles=10
    )
    
    news_data = asyncio.run(scraper.scrape_news())
    print(f"Scraped {len(news_data)} news articles")
    
    for item in news_data:
        print(f"Company: {item['company']} ({item['ticker']})")
        print(f"Title: {item['title']}")
        print(f"Date: {item['published_at']}")
        print(f"URL: {item['url']}")
        print("-" * 50)

if __name__ == "__main__":
    main()