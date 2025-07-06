# Stock MCP Server - Screener Integration Guide

## Overview

This MCP server provides **comprehensive stock analysis** by combining:
- **Real-time technical data** from MySQL database (RSI, MACD, Sharpe ratios, etc.)
- **Latest fundamental insights** from PDF documents (earnings calls, annual reports)
- **AI-powered analysis** through intelligent document processing

Perfect for enhancing your technical screener with fundamental analysis using the latest company documents.

## 🚀 Quick Integration

### Installation

```bash
# Clone and setup
git clone <repository>
cd stock-mcp-server
pip install -r requirements.txt
```

### Basic Usage

```python
from screener_integration_example import MCPStockAnalyzer

# Get comprehensive analysis (technical + fundamental)
analyzer = MCPStockAnalyzer()
analysis = await analyzer.get_comprehensive_analysis("AARTIIND")

print(f"Technical: {analysis['technical_analysis']}")
print(f"Fundamental: {analysis['fundamental_analysis']}")

analyzer.close()
```

## 📊 Available Data

### Technical Metrics (Real-time from Database)
- **Risk Metrics**: Beta, Volatility, Sharpe Ratio, Sortino Ratio, Max Drawdown
- **Performance**: Total Return, Annualized Return, Momentum, Win Rate
- **Technical Indicators**: RSI (14/20/30), MACD, Bollinger Bands, ATR
- **Price Data**: OHLCV with moving averages

### Fundamental Insights (Latest from Documents)
- **Financial Highlights**: Revenue, profit, margins, growth mentions
- **Management Guidance**: Forward-looking statements from earnings calls
- **Key Metrics**: Tables and numerical data extraction
- **Document Types**: Earnings transcripts, annual reports, quarterly results

## 🔍 Smart Document Matching

The server **automatically finds relevant documents** based on stock symbol:

```python
# You pass the symbol
analysis = mcp_server.get_company_fundamentals("AARTIIND")

# Server automatically finds:
# ✅ AARTIIND_Transcript.pdf
# ✅ AARTIIND_Annual_Report.pdf  
# ✅ AARTIIND_Earnings_Q3.pdf
# ❌ Ignores: RELIANCE_Report.pdf
```

### Document Naming Convention
Place PDFs in `data/` directory with this naming:
```
SYMBOL_DocumentType.pdf

Examples:
AARTIIND_Transcript.pdf         ← Highest priority
RELIANCE_Annual_Report.pdf      ← High priority
TCS_Earnings_Q3.pdf             ← Auto-detected
INFY_Results_FY24.pdf           ← Auto-detected
```

## 🛠️ Integration Patterns

### Pattern 1: Enhance Existing Screening

```python
# Your existing technical screener
candidates = screen_stocks({
    "min_rsi": 30,
    "max_rsi": 70,
    "min_volume": 1000000,
    "price_trend": "upward"
})

# Enhance with fundamental analysis
analyzer = MCPStockAnalyzer()
for stock in candidates:
    analysis = await analyzer.get_comprehensive_analysis(stock.symbol)
    
    # Score based on fundamental insights
    text = analysis['fundamental_analysis'].lower()
    if "revenue growth" in text:
        stock.fundamental_score += 20
    if "margin expansion" in text:
        stock.fundamental_score += 15
    if "debt reduction" in text:
        stock.fundamental_score += 10
    
    # Combined scoring
    stock.total_score = stock.technical_score + stock.fundamental_score

analyzer.close()

# Now you have both technical + fundamental scoring!
final_picks = sorted(candidates, key=lambda x: x.total_score, reverse=True)
```

### Pattern 2: Real-time Analysis API

```python
async def get_stock_insights(symbol: str) -> dict:
    """Get comprehensive stock analysis for your app"""
    analyzer = MCPStockAnalyzer()
    try:
        result = await analyzer.get_comprehensive_analysis(symbol)
        
        return {
            "symbol": symbol,
            "technical_score": extract_technical_score(result['technical_analysis']),
            "fundamental_score": extract_fundamental_score(result['fundamental_analysis']),
            "key_insights": extract_key_points(result['fundamental_analysis']),
            "risk_metrics": extract_risk_data(result['technical_analysis']),
            "latest_documents": get_document_list(symbol),
            "last_updated": datetime.now().isoformat()
        }
    finally:
        analyzer.close()
```

### Pattern 3: Batch Processing

```python
async def analyze_portfolio(symbols: list) -> dict:
    """Analyze multiple stocks efficiently"""
    results = {}
    analyzer = MCPStockAnalyzer()
    
    try:
        for symbol in symbols:
            results[symbol] = await analyzer.get_comprehensive_analysis(symbol)
    finally:
        analyzer.close()
    
    return results

# Usage
portfolio = ["AARTIIND", "RELIANCE", "TCS", "INFY"]
analysis = await analyze_portfolio(portfolio)
```

## 📋 API Reference

### Core Methods

```python
class MCPStockAnalyzer:
    async def get_comprehensive_analysis(symbol: str) -> dict:
        """
        Returns:
        {
            "symbol": "AARTIIND",
            "technical_analysis": "Risk metrics, performance data...",
            "fundamental_analysis": "Document insights, financial highlights...", 
            "recent_prices": "OHLCV data with indicators...",
            "status": "success"
        }
        """
    
    async def call_tool(tool_name: str, arguments: dict) -> dict:
        """Direct MCP tool access"""
```

### Available Tools

| Tool | Purpose | Input |
|------|---------|-------|
| `get_advanced_metrics` | Technical analysis | `{"symbol": "AARTIIND", "timeframe": "medium"}` |
| `get_company_fundamentals` | Combined analysis | `{"symbol": "AARTIIND"}` |
| `screen_stocks_by_metrics` | Advanced screening | `{"criteria": {"min_sharpe_ratio": 1.0}}` |
| `find_company_documents` | Debug document matching | `{"symbol": "AARTIIND"}` |
| `analyze_document` | Specific document analysis | `{"filename": "AARTIIND.pdf"}` |

## 🔧 Configuration

### Database Connection
The server automatically connects to the MySQL database. No configuration needed.

### Document Directory
Place PDF documents in the `data/` directory:
```
stock-mcp-server/
├── data/
│   ├── AARTIIND_Transcript.pdf
│   ├── RELIANCE_Annual_Report.pdf
│   └── TCS_Earnings_Q3.pdf
├── stock_mcp_server.py
└── requirements.txt
```

## 🎯 Use Cases for Your Screener

### 1. **Enhanced Stock Scoring**
Combine technical signals with latest fundamental insights for better stock selection.

### 2. **Risk Assessment**
Use document analysis to identify companies with improving/deteriorating fundamentals.

### 3. **Timing Analysis**
Technical indicators for entry/exit + fundamental analysis for conviction.

### 4. **Sector Analysis**
Screen by technical criteria, then rank by fundamental strength within sectors.

### 5. **News-Driven Screening**
Identify stocks with positive earnings commentary and good technical setup.

## ⚡ Performance Notes

- **Database queries**: Sub-second response for technical data
- **Document processing**: 2-5 seconds per PDF (cached after first analysis)
- **Batch processing**: Recommended for analyzing >10 stocks
- **Memory usage**: ~50MB per server instance

## 🐛 Troubleshooting

### Common Issues

1. **"No documents found"**
   - Check file naming: `SYMBOL_*.pdf`
   - Place files in `data/` directory

2. **"Database connection failed"**
   - Server automatically uses fallback connection
   - Check network connectivity if needed

3. **"PDF processing not available"**
   ```bash
   pip install pymupdf
   ```

### Debug Tools

```python
# Check which documents are found for a symbol
debug_info = await analyzer.call_tool("find_company_documents", {"symbol": "AARTIIND"})
print(debug_info)

# List all available documents  
docs = await analyzer.call_tool("list_documents", {})
print(docs)
```

## 📈 Example Output

```python
analysis = await analyzer.get_comprehensive_analysis("AARTIIND")

# Technical Analysis Extract:
"""
RISK & RETURN METRICS:
- Beta: 1.52 (High market correlation)
- Volatility: 39.07% (High risk)
- Sharpe Ratio: -0.33 (Poor risk-adjusted return)
- Max Drawdown: -23.70%

TECHNICAL INDICATORS:
- RSI (14): 45.2 (Neutral)
- MACD: Bullish crossover
"""

# Fundamental Analysis Extract:
"""
📂 Found 2 relevant documents for AARTIIND:
   1. AARTIIND_Transcript.pdf
   2. AARTIIND.pdf

Key Financial Insights:
• Revenue growth of 15% YoY driven by specialty chemicals
• EBITDA margins improved to 18.5% vs 16.2% last year  
• Management guidance: Expecting 20% growth in FY25
• Debt reduction of ₹200 crores completed ahead of schedule
"""
```

## 🚀 Getting Started

1. **Setup**: Install requirements and place PDF documents in `data/` directory
2. **Test**: Run `python test_enhanced_server.py` to verify everything works
3. **Integrate**: Use the code patterns above in your screener
4. **Scale**: Implement batch processing for multiple stocks

The server automatically handles document matching, data extraction, and analysis - you just need to call the functions and process the insights! 🎉

---

**Questions?** Check the detailed guides in `README_Enhanced.md` and `DOCUMENT_MATCHING_GUIDE.md` 