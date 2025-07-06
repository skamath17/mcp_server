# Stock Analysis MCP Server

A comprehensive **Model Context Protocol (MCP) server** that provides advanced stock analysis capabilities combining real-time database metrics with PDF document insights. Features both native MCP support for Claude Desktop and HTTP API endpoints for web applications.

## 🚀 Features

### **📊 Advanced Stock Analysis**
- **Real-time technical metrics** from MySQL database (RSI, MACD, Sharpe ratios, volatility, beta)
- **Fundamental analysis** from PDF documents (earnings transcripts, annual reports)
- **Smart document matching** - automatically finds relevant PDFs by stock symbol
- **Multi-timeframe analysis** (short, medium, long-term)
- **Risk assessment** with comprehensive metrics

### **🔍 Smart Document Processing**
- **Automatic PDF discovery** based on stock symbols
- **Intelligent document scoring** (transcripts > earnings > annual reports)
- **Financial keyword extraction** from company documents
- **Table and metrics parsing** from PDF reports
- **Multi-document analysis** for comprehensive insights

### **🌐 Dual Integration**
- **Native MCP protocol** for Claude Desktop
- **HTTP REST API** for web applications and screeners
- **Flexible deployment** - works in multiple environments

## 📁 Project Structure

```
stock-mcp-server/
├── stock_mcp_server.py      # Main MCP server
├── http_mcp_proxy.py        # HTTP API wrapper
├── claude_config.json       # Claude Desktop configuration
├── requirements.txt         # Python dependencies
├── data/                    # PDF documents directory
│   ├── AARTIIND.pdf
│   └── AARTIIND_Transcript.pdf
└── stock-mcp-env/          # Virtual environment
```

## 🛠️ Installation

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd stock-mcp-server

# Create virtual environment
python -m venv stock-mcp-env

# Activate virtual environment
# Windows:
stock-mcp-env\Scripts\activate
# Linux/Mac:
source stock-mcp-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Database Configuration**
Set your database connection in environment variables or use the fallback:

```bash
# Optional: Set environment variable
export DATABASE_URL="mysql://username:password@host:port/database"

# Or use the built-in fallback configuration
# (mysql://mfuser:Mf_pass_03%@65.20.72.91:3306/mutualfunddb)
```

### **3. Add PDF Documents**
Place your PDF documents in the `data/` directory:

```
data/
├── AARTIIND.pdf                    # Main company document
├── AARTIIND_Transcript.pdf         # Earnings transcript
├── RELIANCE_Annual_Report.pdf      # Annual report
└── TCS_Earnings_Q4_2024.pdf       # Quarterly results
```

**Naming Convention:**
- Best: `{SYMBOL}_{DOCUMENT_TYPE}.pdf` (e.g., `AARTIIND_Transcript.pdf`)
- Good: `{SYMBOL}.pdf` (e.g., `AARTIIND.pdf`)
- Also works: Company name variations

## 🎯 Usage

### **Option 1: Claude Desktop Integration**

#### **Setup Claude Desktop:**
1. Copy `claude_config.json` to:
   - **Windows:** `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Update the Python path in the config:
```json
{
  "mcpServers": {
    "stock-analyzer": {
      "command": "python",
      "args": ["E:\\Projects\\stock-mcp-server\\stock_mcp_server.py"],
      "env": {
        "DATABASE_URL": "mysql://your-connection-string"
      }
    }
  }
}
```

3. Restart Claude Desktop

#### **Claude Desktop Commands:**
```
Ask Claude:
• "Analyze AARTIIND with latest documents"
• "Get advanced metrics for RELIANCE"
• "Show me documents for TCS"
• "Screen stocks with RSI < 30 and Sharpe ratio > 1"
• "Compare AARTIIND fundamentals vs technicals"
```

### **Option 2: HTTP API (For Web Applications)**

#### **Start HTTP Server:**
```bash
python http_mcp_proxy.py
```

Server runs on: `http://localhost:8001`
API Documentation: `http://localhost:8001/docs`

#### **Available Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/stocks/{symbol}` | GET | Basic stock info |
| `/api/stocks/{symbol}/fundamentals` | GET | Comprehensive analysis with PDFs |
| `/api/stocks/{symbol}/metrics` | GET | Advanced technical metrics |
| `/api/stocks/{symbol}/history` | POST | Price history with RSI |
| `/api/stocks/{symbol}/documents` | GET | Document search debug |
| `/api/stocks/search/{pattern}` | GET | Search stocks |
| `/api/stocks/screen` | POST | Screen stocks by criteria |

#### **Example API Usage:**

**JavaScript:**
```javascript
// Get fundamental analysis
const response = await fetch('http://localhost:8001/api/stocks/AARTIIND/fundamentals');
const data = await response.json();
console.log(data.fundamental_analysis[0]);

// Screen stocks
const criteria = {
  min_sharpe_ratio: 1.0,
  max_volatility: 0.3,
  min_rsi: 25,
  max_rsi: 35
};

const screening = await fetch('http://localhost:8001/api/stocks/screen', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ criteria })
});
```

**Python:**
```python
import requests

# Get stock analysis
response = requests.get('http://localhost:8001/api/stocks/AARTIIND/fundamentals')
analysis = response.json()['fundamental_analysis'][0]

# Use in screener application
class StockScreener:
    def enhance_with_fundamentals(self, technical_candidates):
        enhanced = []
        for stock in technical_candidates:
            fundamental_data = requests.get(
                f'http://localhost:8001/api/stocks/{stock.symbol}/fundamentals'
            ).json()
            
            # Combine technical + fundamental scoring
            stock.fundamental_score = self.parse_score(fundamental_data)
            stock.total_score = stock.technical_score + stock.fundamental_score
            enhanced.append(stock)
        
        return sorted(enhanced, key=lambda x: x.total_score, reverse=True)
```

## 🔧 Available Tools/Endpoints

### **Stock Information**
- `get_stock_info` - Company details, price ranges, volume data
- `search_stocks` - Find stocks by symbol or company name

### **Technical Analysis**
- `get_price_history` - OHLCV data with RSI indicators
- `get_advanced_metrics` - Beta, volatility, Sharpe ratio, MACD, etc.
- `screen_stocks_by_metrics` - Multi-criteria stock screening

### **Fundamental Analysis**
- `get_company_fundamentals` - PDF analysis + technical data
- `analyze_document` - Extract insights from specific PDFs
- `find_company_documents` - Smart document discovery
- `list_documents` - All available PDF files

## 📊 Database Schema

The server expects these MySQL tables:

### **Stock**
- `symbol` (VARCHAR) - Stock symbol
- `companyName` (VARCHAR) - Company name
- `sector` (VARCHAR) - Business sector

### **PriceHistory**
- `symbol`, `date`, `open`, `high`, `low`, `close`, `volume`
- `rsi_14` - 14-day RSI indicator

### **WeeklyPriceHistory**
- Weekly aggregated price data with RSI

### **AdvancedStockMetrics**
- `beta`, `volatility`, `sharpe_ratio`, `max_drawdown`
- `rsi_current`, `macd_line`, `macd_signal`
- Advanced technical and risk metrics

## 🎨 Smart Document Matching

The system automatically finds relevant documents using:

### **Priority Scoring:**
1. **Exact symbol match** (100 points)
2. **Document type bonuses:**
   - Transcripts/Calls: +50 points
   - Earnings/Results: +40 points
   - Annual Reports: +30 points
   - Main document (SYMBOL.pdf): +10 points
3. **Recency bonus** (newer files preferred)

### **Matching Examples:**
```
Query: AARTIIND
✅ Matches: AARTIIND_Transcript.pdf (150 pts)
✅ Matches: AARTIIND.pdf (110 pts)
✅ Matches: Q3_AARTIIND_Results.pdf (140 pts)
❌ Ignored: random_document.pdf (0 pts)
```

## 🔍 Integration Patterns

### **For Existing Screener Applications:**

**Pattern 1: HTTP Integration**
```python
# Your existing screener
technical_candidates = run_technical_screening()

# Enhance with MCP server
for stock in technical_candidates:
    fundamentals = requests.get(
        f'http://localhost:8001/api/stocks/{stock.symbol}/fundamentals'
    ).json()
    
    stock.fundamental_insights = parse_insights(fundamentals)
    stock.combined_score = calculate_combined_score(stock)
```

**Pattern 2: Microservice Architecture**
```
Web Frontend → Your Screener API → Stock MCP HTTP API → Database + PDFs
```

**Pattern 3: Direct MCP Client**
```python
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

# Direct MCP integration (advanced)
async def get_analysis(symbol):
    server_params = StdioServerParameters(
        command="python",
        args=["stock_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            return await session.call_tool("get_company_fundamentals", {
                "symbol": symbol,
                "document_pattern": ""
            })
```

## 🚀 Deployment

### **Development:**
```bash
# Start MCP server for Claude Desktop
python stock_mcp_server.py

# Start HTTP API for web applications
python http_mcp_proxy.py
```

### **Production:**
```bash
# Use uvicorn for production HTTP API
uvicorn http_mcp_proxy:app --host 0.0.0.0 --port 8001 --workers 4

# Or use Docker
docker build -t stock-mcp-server .
docker run -p 8001:8001 stock-mcp-server
```

### **Docker Example:**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "http_mcp_proxy:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🧪 Testing

### **Test MCP Server:**
```bash
# Test database connection
python -c "from stock_mcp_server import StockMCPServer; import asyncio; server = StockMCPServer(); asyncio.run(server.connect_database())"

# Test document discovery
python -c "from stock_mcp_server import StockMCPServer; server = StockMCPServer(); print(server.find_relevant_documents('AARTIIND'))"
```

### **Test HTTP API:**
```bash
# Health check
curl http://localhost:8001/health

# Get stock info
curl http://localhost:8001/api/stocks/AARTIIND

# Get fundamentals
curl http://localhost:8001/api/stocks/AARTIIND/fundamentals
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📚 Dependencies

- **mcp** - Model Context Protocol
- **sqlalchemy** - Database ORM
- **pymysql** - MySQL connector
- **fastapi** - HTTP API framework
- **uvicorn** - ASGI server
- **pymupdf** - PDF processing
- **python-dotenv** - Environment variables

## 🔒 Security Notes

- Configure CORS properly for production
- Use environment variables for sensitive data
- Validate all input parameters
- Implement rate limiting for production APIs

## 📄 License

MIT License - see LICENSE file for details

## 🙋‍♂️ Support

For issues and questions:
1. Check the `/health` endpoint for server status
2. Review logs for error details
3. Verify database connectivity
4. Ensure PDF files are in correct directory with proper naming

---

**Perfect for:** Financial applications, stock screeners, investment research tools, AI-powered trading systems, and any application requiring comprehensive stock analysis with document insights! 🚀📈 