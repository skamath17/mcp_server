# Enhanced Stock MCP Server with Document Analysis

## Overview

This project provides a comprehensive stock analysis system that combines:

1. **Real-time Technical Analysis** - Direct access to MySQL database with advanced metrics
2. **Latest Fundamental Analysis** - PDF document processing for earnings reports, transcripts, annual reports
3. **AI-Powered Insights** - Claude Desktop integration for intelligent analysis
4. **Screener Integration** - API for your technical screener app to access both technical + fundamental data

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Screener App   │────│  MCP Server      │────│  MySQL Database │
│  (Technical)    │    │  (Bridge)        │    │  (Live Data)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                │
                       ┌──────────────────┐    ┌─────────────────┐
                       │  PDF Documents   │    │  Claude Desktop │
                       │  (Fundamentals)  │    │  (AI Analysis)  │
                       └──────────────────┘    └─────────────────┘
```

## Key Features

### 🔍 Enhanced Stock Analysis Tools

1. **get_stock_info** - Company details, price ranges, volume
2. **get_price_history** - OHLCV data with RSI, moving averages
3. **search_stocks** - Search by symbol or company name
4. **get_advanced_metrics** - Professional metrics (Sharpe ratio, beta, volatility, MACD, Bollinger Bands)
5. **screen_stocks_by_metrics** - Advanced screening with multiple criteria

### 📄 NEW: Document Analysis Tools

6. **analyze_document** - Extract insights from PDF documents
   - **Financial highlights** - Automatically find revenue, profit, growth mentions
   - **Key metrics** - Extract tables and numerical data
   - **Full text** - Complete document content
   - **Summary** - First few pages overview

7. **list_documents** - Show all available PDFs with metadata

8. **get_company_fundamentals** - **🌟 STAR FEATURE** 
   - Combines real-time technical data from database
   - With latest fundamental insights from company documents
   - Perfect for your screener app integration

## Installation & Setup

### 1. Install Requirements

```bash
# Activate virtual environment
.\stock-mcp-env\Scripts\activate

# Install enhanced requirements (includes PDF processing)
pip install -r requirements.txt
```

### 2. Add Company Documents

Place PDF documents in the `data/` directory:
```
data/
├── AARTIIND_Transcript.pdf
├── AARTIIND.pdf
├── RELIANCE_Annual_Report.pdf
├── TCS_Earnings_Call.pdf
└── ... (any company PDFs)
```

### 3. Configure Claude Desktop

Update `C:\Users\[username]\AppData\Roaming\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock-server": {
      "command": "E:\\Projects\\stock-mcp-server\\stock-mcp-env\\Scripts\\python.exe",
      "args": ["E:\\Projects\\stock-mcp-server\\stock_mcp_server.py"],
      "env": {}
    }
  }
}
```

## Integration with Your Screener App

### Option 1: Direct MCP Integration

Use the provided `screener_integration_example.py`:

```python
from screener_integration_example import MCPStockAnalyzer

# Initialize
analyzer = MCPStockAnalyzer()

# Get comprehensive analysis (technical + fundamental)
analysis = await analyzer.get_comprehensive_analysis("AARTIIND")

print(f"Technical: {analysis['technical_analysis']}")
print(f"Fundamental: {analysis['fundamental_analysis']}")
```

### Option 2: HTTP API Wrapper

Create a simple FastAPI wrapper:

```python
from fastapi import FastAPI
from screener_integration_example import MCPStockAnalyzer

app = FastAPI()

@app.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    analyzer = MCPStockAnalyzer()
    try:
        return await analyzer.get_comprehensive_analysis(symbol)
    finally:
        analyzer.close()
```

### Option 3: Direct Database + Document Processing

For high-performance scenarios, directly integrate the components:

```python
# Use SQLAlchemy for database (your existing technical data)
# Use PyMuPDF for document processing (new fundamental insights)
# Combine in your screener logic
```

## Usage Examples

### 1. Analyze Company Documents

```python
# Claude Desktop conversation:
"Analyze the AARTIIND transcript for key financial highlights"

# Server will:
# 1. Process AARTIIND_Transcript.pdf
# 2. Extract financial keywords and metrics
# 3. Present organized insights
```

### 2. Comprehensive Stock Analysis

```python
# Claude Desktop conversation:
"Give me a complete analysis of AARTIIND including both technical metrics and latest fundamental insights"

# Server will:
# 1. Fetch real-time technical data from database
# 2. Analyze relevant documents for fundamental insights
# 3. Combine both perspectives for investment decision
```

### 3. Screener Integration

```python
# Your screener app:
results = technical_screen(criteria)  # Your existing logic

for stock in results:
    # Enhance with fundamental analysis
    fundamental_data = mcp_server.get_company_fundamentals(stock.symbol)
    stock.fundamental_score = calculate_fundamental_score(fundamental_data)
    
# Now you have technical + fundamental scoring!
```

## PDF Document Processing Features

### Supported Analysis Types

1. **summary** - Overview of first few pages
2. **financial_highlights** - Auto-extract financial mentions
3. **key_metrics** - Tables and numerical data
4. **full_text** - Complete document content

### Supported Output Formats

1. **text** - Plain text (default)
2. **json** - Structured JSON
3. **structured** - Organized with metadata

### Financial Keyword Detection

Automatically finds mentions of:
- Revenue, profit, earnings, EBITDA
- Cash flow, debt, equity, ROI, ROE
- EPS, dividend, margin, growth
- Guidance, outlook, performance

## Benefits for Your Screener App

### Before (Technical Only)
```
Stock Score = Technical Analysis Only
- RSI, MACD, moving averages
- Price momentum, volatility
- Historical patterns
```

### After (Technical + Fundamental)
```
Stock Score = Technical Analysis + Fundamental Analysis
- RSI, MACD, moving averages (from database)
- Price momentum, volatility (from database)
- Latest earnings insights (from PDFs)
- Management guidance (from transcripts)
- Financial health (from annual reports)
```

### Key Advantages

1. **Latest Information** - Process documents as soon as they're released
2. **No API Delays** - Direct document processing, no third-party dependencies
3. **Customizable** - Extract exactly what's relevant for your strategy
4. **AI-Enhanced** - Use Claude for intelligent interpretation
5. **Real-time Combo** - Technical data from DB + fundamental data from docs

## Performance Considerations

### For High-Volume Screening

1. **Cache document analysis** - Parse PDFs once, reuse insights
2. **Batch processing** - Analyze multiple stocks together
3. **Async operations** - Non-blocking document processing
4. **Database optimization** - Indexed queries for technical data

### Document Management

1. **Automated downloads** - Script to fetch latest company reports
2. **File naming** - Use `{SYMBOL}_{TYPE}_{DATE}.pdf` convention
3. **Cleanup** - Remove old documents to save space
4. **Monitoring** - Track when new documents are available

## Example Workflow

### Daily Screening Process

```python
# 1. Your technical screener identifies candidates
candidates = run_technical_screen({
    "min_rsi": 30, "max_rsi": 70,
    "min_volume": 1000000,
    "price_trend": "upward"
})

# 2. Enhance with fundamental analysis
for stock in candidates:
    analysis = mcp_server.get_company_fundamentals(stock.symbol)
    
    # Extract key metrics from analysis
    if "revenue growth" in analysis.lower():
        stock.fundamental_score += 10
    if "margin expansion" in analysis.lower():
        stock.fundamental_score += 15
    
    # Final score = Technical + Fundamental
    stock.total_score = stock.technical_score + stock.fundamental_score

# 3. Rank by combined score
final_picks = sorted(candidates, key=lambda x: x.total_score, reverse=True)
```

## Troubleshooting

### Common Issues

1. **PyMuPDF not found**
   ```bash
   pip install pymupdf
   ```

2. **Database connection issues**
   - Check network connectivity to 65.20.72.91:3306
   - Verify credentials in DATABASE_URL

3. **PDF processing errors**
   - Ensure PDFs are not password-protected
   - Check file permissions in data/ directory

4. **Claude Desktop integration**
   - Verify python.exe path in config
   - Check MCP server logs for errors

### Logs and Debugging

The server provides detailed logging:
```
INFO - Database connection successful
INFO - PDF processing available (PyMuPDF found)
INFO - Document analyzed: AARTIIND_Transcript.pdf
INFO - MCP Server is running and ready for connections
```

## Future Enhancements

1. **OCR Support** - Process scanned PDFs
2. **Web Scraping** - Auto-download latest reports
3. **ML Models** - Sentiment analysis on transcripts
4. **Excel Processing** - Analyze financial spreadsheets
5. **News Integration** - Include latest news sentiment

---

## Contact & Support

This enhanced MCP server bridges the gap between technical analysis and fundamental analysis, giving your screener app access to the latest company insights through AI-powered document processing.

Perfect for building a comprehensive stock analysis platform that goes beyond just technical indicators! 