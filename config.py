# config.py
"""Configuration settings for the LD Micro News Analysis System."""
import os

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'from_email': 'intorciachristian@gmail.com',  # Update with your email
    'username': 'intorciachristian@gmail.com',    # Update with your email
    'password': 'nqcj grqe cerc gzhr',           # Update with your app password
    'sender_email': 'intorciachristian@gmail.com',  # Update with your email
    'sender_password': 'nqcj grqe cerc gzhr',      # Update with your app password
    'recipient_email': 'intorciachristian@gmail.com'
}

# Recipient email - update with your email
RECIPIENT_EMAIL = 'intorciachristian@gmail.com'  # Update with your email

# Financial Data API Configuration
FINANCIAL_API_CONFIG = {
    'api_key': 'demo',  # Get free API key from alphavantage.co
    'base_url': 'https://www.alphavantage.co/query'
}

# Gemini API Configuration
GEMINI_CONFIG = {
    'api_key': os.getenv('GEMINI_API_KEY', ''),  # Set GEMINI_API_KEY environment variable
    'model': 'gemini-2.5-flash'  # Using Gemini 2.5 Flash (fast and efficient)
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'start_date': '2025-12-01',  # Today (update as needed)
    'end_date': '2025-12-01',    # Today (update as needed)
    'delay_between_requests': 2,
    'timeout': 30000,
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'min_growth_percentage': 40,  # Minimum percentage for earnings inflection
    'context_window': 200,  # Characters around matched terms
    'max_context_length': 200  # Maximum context length to display
}

# Company Ticker Mapping (for financial data lookup)
COMPANY_TICKERS = {
    "iRobot Corporation": "IRBT",
    "iRobot": "IRBT",
    "IRobot": "IRBT",
    "3D Systems Corporation": "DDD",
    "3D Systems": "DDD",
    "Rocket Pharmaceuticals": "RCKT",
    "RxSight": "RXST",
    "RxSight, Inc.": "RXST",
    "Designer Brands Inc.": "DBI",
    "Designer Brands": "DBI",
    "Apple Inc.": "AAPL",
    "Apple": "AAPL",
    "Microsoft Corporation": "MSFT",
    "Microsoft": "MSFT",
    "Tesla, Inc.": "TSLA",
    "Tesla": "TSLA",
    "Amazon.com, Inc.": "AMZN",
    "Amazon": "AMZN",
    "Alphabet Inc.": "GOOGL",
    "Google": "GOOGL",
    "Meta Platforms, Inc.": "META",
    "Facebook": "META",
    "Netflix, Inc.": "NFLX",
    "Netflix": "NFLX",
    "NVIDIA Corporation": "NVDA",
    "NVIDIA": "NVDA",
    "AMD": "AMD",
    "Advanced Micro Devices": "AMD",
    "Intel Corporation": "INTC",
    "Intel": "INTC"
}
