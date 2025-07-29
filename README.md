# LD Micro News Analysis System

A sophisticated news scraping and analysis system that monitors LD Micro news for strategic inflection points and earnings signals, with email notification capabilities.

## 🚀 Features

- **Intelligent News Scraping**: Automatically scrapes LD Micro news articles
- **Strategic Analysis**: Identifies strategic inflection points and transformational opportunities
- **Earnings Inflection Detection**: Flags true financial inflections (40%+ growth)
- **Financial Data Integration**: Includes market cap and company information
- **Email Notifications**: Beautiful HTML email reports with all key information
- **High-Quality Signals**: Focuses on actionable insights, not noise

## 📧 Email Notification Setup

### Quick Setup

1. **Run the setup script**:
   ```bash
   python setup_email.py
   ```

2. **Follow the interactive prompts**:
   - Enter your email address
   - Choose your SMTP server (Gmail, Outlook, etc.)
   - Enter your password or app password

3. **For Gmail users**:
   - Enable 2-Step Verification
   - Generate an App Password (Security > App passwords)
   - Use the App Password instead of your regular password

### Manual Configuration

If you prefer to configure manually, edit `config.py`:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'from_email': 'your-email@gmail.com',
    'username': 'your-email@gmail.com',
    'password': 'your-app-password'
}

RECIPIENT_EMAIL = 'your-email@gmail.com'
```

## 🏃‍♂️ Running the System

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run the analysis
python main.py
```

### What You'll Receive

The system will send you a beautifully formatted email containing:

- **📅 Date and time** of the analysis
- **🔗 Direct links** to the news articles
- **🏢 Company information** including market cap and sector
- **🎯 Signal type** (Strategic Actions or Earnings Inflection)
- **💡 Implications** of the findings
- **📋 Next steps** for further analysis
- **🔍 Matched terms** with context

## 📊 Analysis Agents

### StrategicActionsAgent
Focuses on strategic inflection points:
- **Pricing Power**: Strategic pricing actions and increases
- **New Products**: Product launches and platform releases
- **Inflection Points**: Transformational opportunities
- **Structural Shifts**: Asset-light models, automation
- **Margin Expansion**: Operational improvements

### EarningsInflectionAgent
Identifies true financial inflections:
- **40%+ Growth**: Only flags explosive revenue/EPS growth
- **Guidance Updates**: Management outlook changes
- **Margin Expansion**: Clear margin improvement signals
- **Structural Improvements**: Operating leverage, automation

## 🔧 Configuration

### Email Settings
- **SMTP Server**: Your email provider's SMTP server
- **Port**: Usually 587 for TLS
- **Authentication**: Username and password/app password

### Financial Data
- **API Key**: Get free API key from [Alpha Vantage](https://www.alphavantage.co/)
- **Company Mapping**: Automatically maps company names to stock tickers

### Scraping Settings
- **Date Range**: Configure start and end dates
- **Article Limit**: Control number of articles to analyze
- **Timeout**: Adjust for slower connections

## 📈 Sample Email Report

The email reports include:

```
🔍 LD Micro News Analysis Report
Generated on: 2025-07-20 18:21:39
Total Signals Found: 2

📊 Strategic Actions & Inflection Points
Found 2 signals in this category.

Signal 1: iRobot Corporation
📅 Date: 2025-07-20
🔗 URL: https://www.ldmicro.com/news/...
💰 Market Cap: $1.2B
📈 Sector: Consumer Discretionary
🏭 Industry: Household Appliances

🎯 Signal Type: Strategic Actions & Inflection Points
💡 Implications: Strategic pricing actions indicate potential for margin expansion...
📋 Next Steps: Track iRobot strategic initiatives and rollout progress...

🔍 Matched Terms:
• strategic pricing actions (pricing_power)
• Context: "The company announced strategic pricing actions..."
```

## 🛠️ Troubleshooting

### Email Issues
- **Authentication Error**: Check your password/app password
- **SMTP Error**: Verify server and port settings
- **Rate Limiting**: Some providers limit emails per day

### Financial Data Issues
- **API Rate Limits**: Alpha Vantage has rate limits on free tier
- **Missing Companies**: Add company names to `COMPANY_TICKERS` in `config.py`

### Scraping Issues
- **Timeout Errors**: Increase timeout in `SCRAPING_CONFIG`
- **No Results**: Check date range and LD Micro website availability

## 🔄 Next Steps

1. **Configure Email**: Run `python setup_email.py`
2. **Test System**: Run `python main.py` to test
3. **Scale Up**: Increase `max_articles` in `config.py`
4. **Add Companies**: Update `COMPANY_TICKERS` for more companies
5. **Get API Key**: Get free Alpha Vantage API key for financial data

## 📝 Files Overview

- `main.py`: Main orchestration script
- `ld_micro_scraper.py`: News scraping functionality
- `analysis_agent_strategic_actions.py`: Strategic inflection analysis
- `analysis_agent_earnings_inflection.py`: Earnings inflection analysis
- `email_notifier.py`: Email notification system
- `financial_data.py`: Financial data fetching
- `config.py`: Configuration settings
- `setup_email.py`: Email setup wizard

## 🎯 Benefits

- **Actionable Insights**: Focus on high-quality signals only
- **Comprehensive Data**: Includes financial metrics and context
- **Professional Reports**: Beautiful HTML email formatting
- **Scalable**: Easy to adjust analysis scope and frequency
- **Cost-Effective**: Efficient analysis with minimal noise

The system is now ready to provide you with professional-grade financial analysis reports delivered directly to your inbox! 