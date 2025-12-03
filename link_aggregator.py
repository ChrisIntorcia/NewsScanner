#!/usr/bin/env python3
"""
Simple LD Micro News Link Aggregator
Just collects all news links for today - no analysis, no complex processing.
"""
import asyncio
import logging
from playwright.async_api import async_playwright
import json
import csv
import os
import html
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from config import EMAIL_CONFIG, RECIPIENT_EMAIL, GEMINI_CONFIG

# Try to import Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('link_aggregator.log'),
        logging.StreamHandler()
    ]
)

class LDMicroLinkAggregator:
    """Simple aggregator that just collects news links from LD Micro."""
    
    def __init__(self, date: str = None):
        """
        Initialize the aggregator.
        
        Args:
            date: Date in YYYY-MM-DD format. If None, uses today's date.
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        self.date = date
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini if available
        self.gemini_client = None
        if GEMINI_AVAILABLE and GEMINI_CONFIG.get('api_key'):
            try:
                genai.configure(api_key=GEMINI_CONFIG['api_key'])
                self.gemini_client = genai.GenerativeModel(GEMINI_CONFIG.get('model', 'gemini-2.5-flash'))
                self.logger.info(f"Gemini {GEMINI_CONFIG.get('model', 'gemini-2.5-flash')} initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Gemini: {str(e)}")
                self.gemini_client = None
        elif not GEMINI_AVAILABLE:
            self.logger.warning("google-generativeai package not installed. Install with: pip install google-generativeai")
        elif not GEMINI_CONFIG.get('api_key'):
            self.logger.warning("GEMINI_API_KEY not set. Set environment variable or add to config.")
    
    def analyze_for_catalysts(self, title: str, content: str, company: str, ticker: str) -> Optional[Dict]:
        """
        Use Gemini 1.5 Pro to analyze article for material catalysts.
        
        Returns:
            Dict with 'has_catalyst' (bool), 'catalysts' (list), 'summary' (str) if catalyst found
            None if no catalyst or Gemini unavailable
        """
        if not self.gemini_client or not content:
            return None
        
        try:
            prompt = f"""You are an expert financial analyst specializing in identifying material catalysts that would be important to investors.

Analyze the following news article and determine if it contains ANY material catalysts from the categories below. Be STRICT - only flag articles with genuine, material catalysts that would meaningfully impact an investor's decision.

COMPANY: {company} ({ticker})
TITLE: {title}

ARTICLE CONTENT:
{content[:8000]}

CATALYST CATEGORIES TO IDENTIFY:

1. INFLECTION POINTS:
   - Major permitting/regulatory approvals (FAST-41, EPA, FDA, state permits)
   - Commercial launch, first revenue, first customer shipment
   - Operational model transitions (asset-light, outsourcing, plant shuttering, CAPEX→OPEX, cloud/SaaS pivot)
   - Major restructuring changing cost base
   - New management with explicit turnaround mandate
   - Transformational strategy changes

2. CONTRACT WINS / CUSTOMERS ADDED:
   - Purchase orders (especially initial PO → validation)
   - MSAs/supply agreements
   - Government awards (DoD, DOE, provinces, municipalities)
   - OEM integrations, design wins
   - Multi-year or multi-site deals
   - Large enterprise customer additions
   - Material expansions with existing customers

3. FINANCINGS THAT CHANGE SURVIVAL OR TRAJECTORY:
   - Strategic financings with institutions
   - Insider-led or insider-participating financings
   - Capital raises linked to plant construction, expansion, commercialization
   - PIPEs, convertibles, royalty deals extending runway
   - Debt refinancing removing near-term default risk
   - Project financing unlocking development

4. M&A / SPINOUTS / STRATEGIC INVESTMENTS:
   - Acquisitions (especially tuck-ins or platform expansions)
   - Divestitures streamlining operations or exiting low-margin businesses
   - Spinouts unlocking value
   - Strategic equity investment by major industry player
   - Joint ventures
   - Major partnerships or co-development agreements

5. EARNINGS SURPRISES (POSITIVE ONLY):
   - Revenue or EBITDA beats
   - Gross margin expansion
   - Upward guidance
   - Record quarterly performance
   - Blowout earnings commentary
   - Clearly telegraphed massive improvement in upcoming quarters
   - Inflection in profitability or cash flow

6. BACKLOG / BOOKINGS MOMENTUM:
   - Record backlog
   - Accelerating bookings
   - Large LOIs with high likelihood of conversion
   - Pipeline expansion
   - Customer ramp commentary ("orders accelerating", "bookings doubled")

7. OPERATIONAL MILESTONES:
   - Plant commissioning, restart, or full ramp
   - Production start or capacity expansion
   - First shipment to customers
   - Drilling results, mineral/43-101 updates, maiden resources
   - Certifications (UL, CE, FDA device approvals, ISO, etc.)
   - Large operational wins (e.g., huge enrollment growth for education/subscription models)
   - New product launches (excluding biotech clinical readouts)
   - Transition from R&D → commercial operations

RESPONSE FORMAT (JSON only):
{{
    "has_catalyst": true/false,
    "catalysts": ["category1", "category2", ...],
    "summary": "Brief 1-2 sentence summary of the key catalyst(s)"
}}

If NO material catalyst is found, return:
{{
    "has_catalyst": false,
    "catalysts": [],
    "summary": ""
}}

Be very strict - exclude routine announcements, minor updates, or non-material developments."""

            response = self.gemini_client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks if present)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            
            if result.get('has_catalyst'):
                return result
            return None
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            self.logger.debug(f"Response was: {response_text[:500]}")
            return None
        except Exception as e:
            self.logger.error(f"Error analyzing article with Gemini: {str(e)}")
            return None
    
    def should_skip_link(self, title: str) -> bool:
        """
        Check if a link should be skipped based on title keywords.
        
        Args:
            title: The article title to check
            
        Returns:
            True if the link should be skipped, False otherwise
        """
        if not title:
            return True
        
        title_lower = title.lower()
        
        # Keywords/phrases that indicate unwanted content
        skip_keywords = [
            'class action',
            'law firm',
            'shareholder rights',
            'investors that lost money',
            'investors have opportunity',
            'securities fraud',
            'securities class action',
            'contact the firm',
            'discuss your rights',
            'deadline to',
            'reminder',
            # Only filter conference/event presentations, not all uses of "present"
            'to present at',
            'to participate at',
            'to participate in',
            'announces plans for upcoming',
            'schedules',
            'to report',
            'will report',
            'to announce',
            'will announce'
        ]
        
        # Check if title contains any skip keywords
        for keyword in skip_keywords:
            if keyword in title_lower:
                return True
        
        return False
        
    async def aggregate_links(self, page) -> List[Dict]:
        """
        Aggregate all news links for the specified date.
        
        Args:
            page: Playwright page object to use for navigation
        
        Returns:
            List of dictionaries containing: title, url, company, ticker, date
        """
        try:
            # Navigate to the news page for today
            url = f"https://www.ldmicro.com/news/{self.date}"
            self.logger.info(f"Fetching links from: {url}")
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_load_state('domcontentloaded')
            self.logger.info("Page loaded successfully.")
            
            # Extract all links
            links = await self._extract_links(page)
            self.logger.info(f"Found {len(links)} news links for {self.date}")
            
            return links
            
        except Exception as e:
            self.logger.error(f"Error aggregating links: {str(e)}")
            return []
    
    async def _extract_links(self, page) -> List[Dict]:
        """Extract all news links from the page."""
        try:
            # Find the table
            table_selectors = ["table.table", "table", ".table", "table tbody"]
            table_found = False
            
            for sel in table_selectors:
                try:
                    await page.wait_for_selector(sel, timeout=5000)
                    self.logger.info(f"Found table with selector: {sel}")
                    table_found = True
                    break
                except:
                    continue
            
            if not table_found:
                self.logger.warning("No table found on page")
                return []
            
            # Get total number of rows
            count_script = """
            () => {
                const rows = document.querySelectorAll('table tbody tr');
                if (rows.length === 0) {
                    const rows2 = document.querySelectorAll('table tr');
                    return rows2.length;
                }
                return rows.length;
            }
            """
            total_rows = await page.evaluate(count_script)
            self.logger.info(f"Found {total_rows} total rows in the news table")
            
            # Process rows in chunks to avoid memory issues
            chunk_size = 50
            all_links = []
            
            for start_idx in range(0, total_rows, chunk_size):
                end_idx = min(start_idx + chunk_size, total_rows)
                self.logger.info(f"Processing rows {start_idx} to {end_idx-1}")
                
                # Extract chunk of rows
                # LD Micro table structure: Date/Time | Premium | Member of LD Micro Index | Symbol | Company | News Release
                chunk_script = f"""
                () => {{
                    const rows = document.querySelectorAll('table tbody tr');
                    let rowArray;
                    if (rows.length === 0) {{
                        rowArray = Array.from(document.querySelectorAll('table tr'));
                    }} else {{
                        rowArray = Array.from(rows);
                    }}
                    
                    // Skip header row if present
                    const dataRows = rowArray.filter(row => {{
                        const cells = row.querySelectorAll('td');
                        return cells.length >= 5; // Data rows have at least 5 cells
                    }});
                    
                    const chunk = dataRows.slice({start_idx}, {end_idx});
                    return chunk.map((row, index) => {{
                        const cells = row.querySelectorAll('td');
                        if (cells.length >= 6) {{
                            // Column structure: 0=Date/Time, 1=Premium, 2=Member, 3=Symbol, 4=Company, 5=News Release
                            const dateTime = cells[0] ? cells[0].textContent.trim() : '';
                            const premium = cells[1] ? cells[1].textContent.trim() : '';
                            const member = cells[2] ? cells[2].textContent.trim() : '';
                            const ticker = cells[3] ? cells[3].textContent.trim() : '';
                            const company = cells[4] ? cells[4].textContent.trim() : '';
                            const newsCell = cells[5] ? cells[5] : cells[cells.length - 1]; // News Release is last column
                            const title = newsCell ? newsCell.textContent.trim() : '';
                            const link = newsCell ? newsCell.querySelector('a') : null;
                            const url = link ? link.href : '';
                            
                            return {{
                                index: {start_idx} + index,
                                date_time: dateTime,
                                premium: premium,
                                ld_micro_index_member: member,
                                ticker: ticker,
                                company: company,
                                title: title,
                                url: url
                            }};
                        }}
                        return null;
                    }}).filter(item => item !== null);
                }}
                """
                
                try:
                    chunk_data = await page.evaluate(chunk_script)
                    all_links.extend(chunk_data)
                    self.logger.info(f"Processed chunk: {len(chunk_data)} items")
                except Exception as e:
                    self.logger.warning(f"Error processing chunk: {str(e)}")
                    continue
            
            # Format the links
            formatted_links = []
            for item in all_links:
                formatted_links.append({
                    'date': self.date,
                    'date_time': item.get('date_time', ''),
                    'premium': item.get('premium', ''),
                    'ld_micro_index_member': item.get('ld_micro_index_member', ''),
                    'company': item.get('company', ''),
                    'ticker': item.get('ticker', ''),
                    'title': item.get('title', ''),
                    'url': item.get('url', '')
                })
            
            return formatted_links
            
        except Exception as e:
            self.logger.error(f"Error extracting links: {str(e)}")
            return []
    
    async def fetch_article_content(self, page, url: str) -> Dict:
        """
        Fetch the full content from an article URL, excluding navigation and page chrome.
        
        Returns:
            Dictionary with 'content' and 'success' keys
        """
        try:
            self.logger.info(f"Fetching content from: {url}")
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_load_state('domcontentloaded')
            
            # Use JavaScript to extract clean article content
            # Look for content after "News and Media" marker, excluding navigation
            content_script = """
            () => {
                // First, try to find the main content area
                // Look for elements that typically contain article content
                const contentSelectors = [
                    'article',
                    '.article-content',
                    '.content',
                    '.post-content',
                    '.news-content',
                    '[class*="article"]',
                    '[class*="content"]',
                    'main',
                    '.main-content'
                ];
                
                let contentElement = null;
                for (const selector of contentSelectors) {
                    const el = document.querySelector(selector);
                    if (el) {
                        const text = el.innerText || el.textContent || '';
                        // Make sure it has substantial content (not just navigation)
                        if (text.length > 500) {
                            contentElement = el;
                            break;
                        }
                    }
                }
                
                // If no specific content area found, try to extract from body
                // but exclude navigation elements
                if (!contentElement) {
                    const body = document.body;
                    if (body) {
                        // Clone body to avoid modifying original
                        const clone = body.cloneNode(true);
                        
                        // Remove common navigation elements
                        const navSelectors = [
                            'nav', '.nav', '#nav', '.navigation', '.sidebar',
                            '.menu', '.header', 'header', '.footer', 'footer',
                            '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
                            '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]'
                        ];
                        
                        navSelectors.forEach(sel => {
                            const elements = clone.querySelectorAll(sel);
                            elements.forEach(el => el.remove());
                        });
                        
                        contentElement = clone;
                    }
                }
                
                if (!contentElement) {
                    return '';
                }
                
                // Get text content
                let text = contentElement.innerText || contentElement.textContent || '';
                
                // Clean up: remove navigation menu items that might still be there
                // Common patterns: "Back to Index", "Overview", "Corporate Events", etc.
                const navPatterns = [
                    /Back to Index[\\s\\S]*?Insiders/g,
                    /Overview[\\s\\S]*?Insiders/g,
                    /News & Media[\\s\\S]*?Detail View/g,
                    /Email Print Share[\\s\\S]*?Share/g
                ];
                
                navPatterns.forEach(pattern => {
                    text = text.replace(pattern, '');
                });
                
                // Find the actual article start (usually after "News and Media" or title)
                const markers = ['News and Media', 'News & Media'];
                for (const marker of markers) {
                    const index = text.indexOf(marker);
                    if (index !== -1) {
                        // Get text after the marker
                        text = text.substring(index + marker.length).trim();
                        // Remove any remaining navigation-like text at the start
                        text = text.replace(/^[\\s\\S]{0,200}(?=News and Media|News & Media|\\w{3,})/, '');
                        break;
                    }
                }
                
                // Remove excessive whitespace but preserve paragraph structure
                text = text.replace(/\\s+/g, ' ').trim();
                
                // Remove common footer/header text patterns
                const unwantedPatterns = [
                    /Not for dissemination[\\s\\S]*?Newswire Services/gi,
                    /Forward-looking[\\s\\S]*?statements/gi,
                    /Neither the TSX[\\s\\S]*?this release/gi,
                    /On behalf of[\\s\\S]*?Board/gi,
                    /For further information[\\s\\S]*?contact:/gi
                ];
                
                unwantedPatterns.forEach(pattern => {
                    text = text.replace(pattern, '');
                });
                
                return text.trim();
            }
            """
            
            content = await page.evaluate(content_script)
            
            # Additional cleanup in Python
            if content:
                # Remove any remaining navigation menu items at the start
                nav_keywords = ['Back to Index', 'Overview', 'Corporate Events', 'Filings', 
                              'Financials', 'Historical Data', 'Share Info', 'Time and Sales', 
                              'Insiders', 'Detail View', 'Email Print Share']
                
                # Find where actual content starts (after navigation)
                content_start = 0
                for keyword in nav_keywords:
                    idx = content.find(keyword)
                    if idx != -1:
                        # Look for the title or "News and Media" after this
                        after_nav = content[idx + len(keyword):idx + 500]
                        if 'News and Media' in after_nav or 'News & Media' in after_nav:
                            # Find the title after "News and Media"
                            media_idx = content.find('News and Media', idx)
                            if media_idx == -1:
                                media_idx = content.find('News & Media', idx)
                            if media_idx != -1:
                                # Get text after "News and Media" and the title
                                potential_start = media_idx + len('News and Media')
                                # Skip the title (usually first 100-200 chars after marker)
                                content_start = potential_start + 200
                                break
                
                if content_start > 0:
                    content = content[content_start:].strip()
                
                # Remove excessive whitespace
                content = ' '.join(content.split())
                
                # No character limit - get all content
            
            return {
                'content': content,
                'success': len(content) > 200,  # Require at least 200 chars of actual content
                'content_length': len(content)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching article content: {str(e)}")
            return {
                'content': '',
                'success': False,
                'error': str(e),
                'content_length': 0
            }
    
    def send_email_report(self, links: List[Dict], filtered_links: List[Dict]) -> bool:
        """Send email report with all links and their content."""
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"LD Micro News Links - {self.date}"
            msg['From'] = EMAIL_CONFIG['from_email']
            msg['To'] = RECIPIENT_EMAIL
            
            # Generate HTML and text content
            html_content = self._generate_html_email(links, filtered_links)
            text_content = self._generate_text_email(links, filtered_links)
            
            # Attach both HTML and text versions
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                if EMAIL_CONFIG.get('use_tls', True):
                    server.starttls()
                
                if EMAIL_CONFIG.get('username') and EMAIL_CONFIG.get('password'):
                    server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                
                server.send_message(msg)
            
            self.logger.info(f"Email report sent successfully to {RECIPIENT_EMAIL}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _generate_html_email(self, all_links: List[Dict], filtered_links: List[Dict]) -> str:
        """Generate HTML email content with improved layout for Gmail."""
        # Escape HTML in content to prevent issues
        def escape_html(text):
            if not text:
                return ''
            return html.escape(str(text))
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7fa; line-height: 1.6;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f7fa; padding: 20px 0;">
        <tr>
            <td align="center">
                <table role="presentation" width="90%" max-width="900" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 40px; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">📰 LD Micro News Links</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">{self.date} • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </td>
                    </tr>
                    
                    <!-- Summary Stats -->
                    <tr>
                        <td style="padding: 25px 40px; background-color: #f8f9fa; border-bottom: 2px solid #e9ecef;">
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 8px 0;">
                                        <strong style="color: #495057; font-size: 16px;">Summary:</strong>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 5px 0; color: #6c757d; font-size: 14px;">
                                        Total Links Found: <strong style="color: #495057;">{len(all_links)}</strong> • 
                                        Articles with Material Catalysts: <strong style="color: #28a745;">{len(filtered_links)}</strong> • 
                                        Filtered Out: <strong style="color: #dc3545;">{len(all_links) - len(filtered_links)}</strong>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Articles -->
        """
        
        # Add links with content
        for i, link in enumerate(filtered_links, 1):
            company = escape_html(link.get('company', 'Unknown'))
            ticker = escape_html(link.get('ticker', 'N/A'))
            title = escape_html(link.get('title', 'No title'))
            date_time = escape_html(link.get('date_time', link.get('date', 'Unknown')))
            url = link.get('url', '#')
            content = link.get('content', '')
            
            # Format content with proper line breaks
            if content:
                # Split into sentences and add line breaks for readability
                content_escaped = escape_html(content)
                # Add line breaks after periods followed by space and capital letter
                content_formatted = re.sub(r'\. ([A-Z])', r'.<br><br>\1', content_escaped)
                # Limit to first 3000 chars for email size
                if len(content_escaped) > 3000:
                    content_formatted = content_formatted[:3000] + '...<br><br><em style="color: #6c757d;">(Content truncated - view full article for complete text)</em>'
            else:
                content_formatted = '<em style="color: #6c757d;">No content available</em>'
            
            html_content += f"""
                    <!-- Article {i} -->
                    <tr>
                        <td style="padding: 30px 40px; border-bottom: 1px solid #e9ecef;">
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding-bottom: 12px;">
                                        <h2 style="margin: 0; color: #212529; font-size: 20px; font-weight: 600; line-height: 1.3;">
                                            {i}. {company} <span style="color: #6c757d; font-weight: 400;">({ticker})</span>
                                        </h2>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-bottom: 15px;">
                                        <p style="margin: 0; color: #495057; font-size: 16px; font-weight: 500; line-height: 1.5;">
                                            {title}
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-bottom: 20px;">
                                        <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td style="padding-right: 20px; color: #6c757d; font-size: 13px;">
                                                    📅 {date_time}
                                                </td>
                                                <td>
                                                    <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 13px; font-weight: 500;">🔗 View Article →</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>"""
            
            # Add catalyst information if available
            catalysts = link.get('catalysts', [])
            catalyst_summary = link.get('catalyst_summary', '')
            if catalysts:
                catalysts_text = ', '.join(catalysts)
                html_content += f"""
                                <tr>
                                    <td style="padding-bottom: 15px;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 15px; border-radius: 6px; font-size: 13px;">
                                            <strong>🎯 Material Catalysts:</strong> {catalysts_text}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding-bottom: 20px;">
                                        <div style="background-color: #f0f4ff; padding: 12px 15px; border-left: 3px solid #667eea; border-radius: 4px; font-size: 13px; color: #495057; font-style: italic;">
                                            {escape_html(catalyst_summary)}
                                        </div>
                                    </td>
                                </tr>
            """
            
            html_content += f"""
                                <tr>
                                    <td style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #667eea; border-radius: 4px;">
                                        <div style="color: #212529; font-size: 14px; line-height: 1.7; max-height: 600px; overflow-y: auto;">
                                            {content_formatted}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
            """
        
        # Add filtered out links section if any
        filtered_out = [link for link in all_links if link.get('filtered_out')]
        if filtered_out:
            html_content += """
                    <!-- Filtered Out Section Header -->
                    <tr>
                        <td style="padding: 30px 40px 15px 40px; background-color: #fff3cd; border-top: 3px solid #ffc107;">
                            <h2 style="margin: 0; color: #856404; font-size: 18px; font-weight: 600;">⏭️ Filtered Out Links</h2>
                            <p style="margin: 5px 0 0 0; color: #856404; font-size: 13px;">These links were excluded based on filtering criteria</p>
                        </td>
                    </tr>
            """
            for link in filtered_out:
                company = escape_html(link.get('company', 'Unknown'))
                ticker = escape_html(link.get('ticker', 'N/A'))
                title = escape_html(link.get('title', 'No title'))
                reason = escape_html(link.get('filter_reason', 'Title contains unwanted keywords'))
                
                html_content += f"""
                    <tr>
                        <td style="padding: 15px 40px; border-bottom: 1px solid #ffeaa7; background-color: #fffbf0;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                <strong>{company} ({ticker}):</strong> {title}<br>
                                <span style="font-size: 12px; color: #b8860b;">Reason: {reason}</span>
                            </p>
                        </td>
                    </tr>
                """
        
        html_content += """
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; background-color: #f8f9fa; border-radius: 0 0 8px 8px; text-align: center;">
                            <p style="margin: 0; color: #6c757d; font-size: 12px;">
                                Generated by LD Micro News Aggregator
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        return html_content
    
    def _generate_text_email(self, all_links: List[Dict], filtered_links: List[Dict]) -> str:
        """Generate plain text email content."""
        text = f"""
LD Micro News Links - {self.date}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
Total Links Found: {len(all_links)}
Articles with Material Catalysts: {len(filtered_links)}
Filtered Out: {len(all_links) - len(filtered_links)}

{'='*80}

"""
        
        # Add links with content
        for i, link in enumerate(filtered_links, 1):
            text += f"""
Link {i}: {link.get('company', 'Unknown')} ({link.get('ticker', 'N/A')})
Title: {link.get('title', 'No title')}
Date: {link.get('date_time', link.get('date', 'Unknown'))}
URL: {link.get('url', 'N/A')}
"""
            # Add catalyst information if available
            catalysts = link.get('catalysts', [])
            catalyst_summary = link.get('catalyst_summary', '')
            if catalysts:
                text += f"\n🎯 Material Catalysts: {', '.join(catalysts)}\n"
                if catalyst_summary:
                    text += f"Summary: {catalyst_summary}\n"
            
            if link.get('content'):
                content_preview = link.get('content', '')[:1500]  # First 1500 chars
                if len(link.get('content', '')) > 1500:
                    content_preview += '...'
                text += f"\nContent:\n{content_preview}\n"
            
            text += "\n" + "-"*80 + "\n"
        
        return text


async def main():
    """Main function to run the link aggregator."""
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"LD Micro News Link Aggregator")
    print(f"Date: {today}")
    print("-" * 50)
    
    aggregator = LDMicroLinkAggregator(date=today)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            # Step 1: Aggregate all links
            links = await aggregator.aggregate_links(page)
            
            if links:
                # Step 2: Filter out unwanted links
                print(f"\n🔍 Filtering links...")
                filtered_links = []
                skipped_count = 0
                
                for link in links:
                    if aggregator.should_skip_link(link.get('title', '')):
                        skipped_count += 1
                        continue
                    filtered_links.append(link)
                
                print(f"  ✅ Kept {len(filtered_links)} links after filtering")
                print(f"  ⏭️  Skipped {skipped_count} links (class action, law firm, presentations, etc.)")
                
                # Step 3: Fetch content for all filtered links
                if filtered_links:
                    print(f"\n📄 Fetching content for {len(filtered_links)} links...")
                    
                    for i, link in enumerate(filtered_links, 1):
                        if link.get('url'):
                            print(f"  [{i}/{len(filtered_links)}] {link['company']} - {link['title'][:50]}...", end=' ')
                            content_result = await aggregator.fetch_article_content(page, link['url'])
                            
                            # Add content to the link data
                            link['content'] = content_result.get('content', '')
                            link['content_fetched'] = content_result.get('success', False)
                            link['content_length'] = content_result.get('content_length', 0)
                            
                            if content_result.get('success'):
                                print(f"✅ ({content_result.get('content_length', 0)} chars)")
                            else:
                                print(f"❌ ({content_result.get('error', 'Unknown error')})")
                    
                    # Step 3.5: Analyze articles with Gemini for material catalysts
                    if aggregator.gemini_client:
                        print(f"\n🤖 Analyzing articles with Gemini for material catalysts...")
                        catalyst_links = []
                        
                        for i, link in enumerate(filtered_links, 1):
                            if link.get('content') and link.get('content_fetched'):
                                print(f"  [{i}/{len(filtered_links)}] Analyzing: {link['company']}...", end=' ')
                                catalyst_result = aggregator.analyze_for_catalysts(
                                    title=link.get('title', ''),
                                    content=link.get('content', ''),
                                    company=link.get('company', ''),
                                    ticker=link.get('ticker', '')
                                )
                                
                                if catalyst_result and catalyst_result.get('has_catalyst'):
                                    link['catalyst_analysis'] = catalyst_result
                                    link['catalysts'] = catalyst_result.get('catalysts', [])
                                    link['catalyst_summary'] = catalyst_result.get('summary', '')
                                    catalyst_links.append(link)
                                    print(f"✅ Catalyst found: {', '.join(catalyst_result.get('catalysts', []))}")
                                else:
                                    print("⏭️  No material catalyst")
                            else:
                                # Skip articles without content
                                print(f"  [{i}/{len(filtered_links)}] Skipping {link['company']} (no content)")
                        
                        print(f"\n  ✅ Found {len(catalyst_links)} articles with material catalysts out of {len(filtered_links)} analyzed")
                        filtered_links = catalyst_links  # Replace with only catalyst-containing links
                    else:
                        print(f"\n⚠️  Gemini not available - including all articles (install google-generativeai and set GEMINI_API_KEY)")
                    
                    # Step 4: Prepare all links (filtered links with content + skipped links without content)
                    # Include skipped links in output but mark them as filtered
                    all_links = filtered_links.copy()
                    for link in links:
                        if aggregator.should_skip_link(link.get('title', '')):
                            link['filtered_out'] = True
                            link['filter_reason'] = 'Title contains unwanted keywords'
                            all_links.append(link)
                    
                    # Step 5: Send email report instead of saving to files
                    print(f"\n📧 Sending email report...")
                    if aggregator.send_email_report(all_links, filtered_links):
                        print(f"✅ Email sent successfully to {RECIPIENT_EMAIL}")
                    else:
                        print(f"❌ Failed to send email")
                    
                    print(f"\n✅ Successfully processed {len(filtered_links)} links with content")
                    print(f"✅ Total links: {len(all_links)} (including {skipped_count} filtered)")
                else:
                    print("\n⚠️  No links remaining after filtering")
            else:
                print("\n❌ No links found")
                
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

