# setup_email.py
"""Setup script to configure email settings for the LD Micro News Analysis System."""

import os
import getpass
from config import EMAIL_CONFIG, RECIPIENT_EMAIL

def setup_email_config():
    """Interactive setup for email configuration."""
    print("🔧 LD Micro News Analysis - Email Setup")
    print("=" * 50)
    
    print("\n📧 Email Configuration Setup")
    print("You'll need to configure your email settings to receive analysis reports.")
    
    # Get email address
    email = input("\nEnter your email address: ").strip()
    if not email:
        print("❌ Email address is required!")
        return False
    
    # Get SMTP settings
    print("\n📮 SMTP Server Configuration")
    print("Common SMTP servers:")
    print("- Gmail: smtp.gmail.com:587")
    print("- Outlook: smtp-mail.outlook.com:587")
    print("- Yahoo: smtp.mail.yahoo.com:587")
    
    smtp_server = input("Enter SMTP server (e.g., smtp.gmail.com): ").strip()
    if not smtp_server:
        smtp_server = "smtp.gmail.com"
    
    smtp_port = input("Enter SMTP port (default: 587): ").strip()
    if not smtp_port:
        smtp_port = 587
    else:
        try:
            smtp_port = int(smtp_port)
        except ValueError:
            smtp_port = 587
    
    # Get password
    print("\n🔐 Email Password")
    print("For Gmail, you'll need to use an 'App Password' instead of your regular password.")
    print("To create an App Password:")
    print("1. Go to your Google Account settings")
    print("2. Enable 2-Step Verification if not already enabled")
    print("3. Go to Security > App passwords")
    print("4. Generate a new app password for 'Mail'")
    
    password = getpass.getpass("Enter your email password or app password: ")
    if not password:
        print("❌ Password is required!")
        return False
    
    # Update configuration
    EMAIL_CONFIG.update({
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'from_email': email,
        'username': email,
        'password': password
    })
    
    # Update recipient email
    global RECIPIENT_EMAIL
    RECIPIENT_EMAIL = email
    
    # Save configuration to file
    save_config()
    
    print("\n✅ Email configuration saved successfully!")
    print(f"📧 Reports will be sent to: {email}")
    print(f"📮 SMTP Server: {smtp_server}:{smtp_port}")
    
    return True

def save_config():
    """Save the updated configuration to config.py."""
    config_content = f'''# config.py
"""Configuration settings for the LD Micro News Analysis System."""

# Email Configuration
EMAIL_CONFIG = {{
    'smtp_server': '{EMAIL_CONFIG['smtp_server']}',
    'smtp_port': {EMAIL_CONFIG['smtp_port']},
    'use_tls': True,
    'from_email': '{EMAIL_CONFIG['from_email']}',
    'username': '{EMAIL_CONFIG['username']}',
    'password': '{EMAIL_CONFIG['password']}'
}}

# Recipient email - update with your email
RECIPIENT_EMAIL = '{RECIPIENT_EMAIL}'

# Financial Data API Configuration
FINANCIAL_API_CONFIG = {{
    'api_key': 'demo',  # Get free API key from alphavantage.co
    'base_url': 'https://www.alphavantage.co/query'
}}

# Scraping Configuration
SCRAPING_CONFIG = {{
    'start_date': '2025-07-15',
    'end_date': '2025-07-20',
    'max_articles': 10,
    'timeout': 30000,  # 30 seconds
    'headless': True
}}

# Analysis Configuration
ANALYSIS_CONFIG = {{
    'min_growth_percentage': 40,  # Minimum percentage for earnings inflection
    'context_window': 200,  # Characters around matched terms
    'max_context_length': 200  # Maximum context length to display
}}

# Company Ticker Mapping (for financial data lookup)
COMPANY_TICKERS = {{
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
}}
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)

def test_email_config():
    """Test the email configuration."""
    print("\n🧪 Testing Email Configuration...")
    
    try:
        from email_notifier import EmailNotifier
        
        # Create a test message with proper structure
        class TestResult:
            def __init__(self):
                self.company_name = 'Test Company'
                self.date = '2025-07-20'
                self.url = 'https://example.com'
                self.agent_category = 'Test Category'
                self.matched_terms = []
                self.implications = 'This is a test email to verify your configuration.'
                self.next_steps = 'If you receive this email, your configuration is working correctly!'
        
        test_results = [TestResult()]
        
        notifier = EmailNotifier(EMAIL_CONFIG)
        success = notifier.send_analysis_report(test_results, RECIPIENT_EMAIL)
        
        if success:
            print("✅ Email test successful! Check your inbox for a test message.")
        else:
            print("❌ Email test failed. Please check your configuration.")
            
    except Exception as e:
        print(f"❌ Email test failed with error: {str(e)}")

if __name__ == "__main__":
    print("Welcome to the LD Micro News Analysis Email Setup!")
    
    if setup_email_config():
        test_choice = input("\nWould you like to test the email configuration? (y/n): ").strip().lower()
        if test_choice in ['y', 'yes']:
            test_email_config()
    
    print("\n🎉 Setup complete! You can now run the analysis system with email notifications.")
    print("Run 'python main.py' to start the analysis.") 