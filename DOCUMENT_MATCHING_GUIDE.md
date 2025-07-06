# Smart Document Matching Guide

## How the MCP Server Automatically Finds Your Documents

Your enhanced MCP server now uses **intelligent document matching** to automatically find the right PDF documents for any stock symbol. No need to manually specify filenames!

## 🔍 How It Works

### 1. **Priority-Based Matching**

When you pass a stock symbol like `AARTIIND`, the server searches for documents in this order:

#### **Priority 1: Exact Symbol Match**
- `AARTIIND.pdf` ✅
- `AARTIIND_Transcript.pdf` ✅
- `Q3_AARTIIND_Results.pdf` ✅
- `Annual_Report_AARTIIND_2024.pdf` ✅

#### **Priority 2: Company Name Match**
- If no exact symbol match, looks up company name from database
- `AARTI_INDUSTRIES_Report.pdf` ✅
- `Aarti_Earnings_Call.pdf` ✅

#### **Priority 3: Fallback**
- If no matches found, analyzes all available PDFs
- Still provides technical analysis even without documents

### 2. **Smart Relevance Scoring**

Documents are ranked by relevance:

| Document Type | Score | Why Important |
|---------------|-------|---------------|
| `SYMBOL_Transcript.pdf` | 150 | Latest earnings call insights |
| `SYMBOL_Earnings.pdf` | 140 | Quarterly performance data |
| `SYMBOL_Annual_Report.pdf` | 130 | Comprehensive yearly analysis |
| `SYMBOL_Results.pdf` | 140 | Financial results |
| `SYMBOL.pdf` | 100 | General company document |

### 3. **Automatic Document Type Detection**

The server recognizes document types automatically:

```
AARTIIND_Transcript.pdf → "earnings transcript" 
AARTIIND_Annual_Report.pdf → "annual report"
AARTIIND_Q3_Results.pdf → "earnings related"
```

## 📁 Recommended File Naming

### **Best Practices**

✅ **Perfect naming:**
- `AARTIIND_Transcript.pdf`
- `RELIANCE_Annual_Report_2024.pdf`
- `TCS_Q4_Results.pdf`
- `INFY_Earnings_Call_FY25.pdf`

✅ **Also works:**
- `AARTI_INDUSTRIES_Report.pdf`
- `Transcript_AARTIIND_Dec2024.pdf`
- `Q3_AARTIIND_Results.pdf`

❌ **Avoid:**
- `financial_report.pdf` (no stock identifier)
- `document1.pdf` (no meaningful name)
- `earnings.pdf` (no company identifier)

### **File Naming Template**

```
{SYMBOL}_{DOCUMENT_TYPE}_{OPTIONAL_DATE}.pdf

Examples:
AARTIIND_Transcript.pdf
RELIANCE_Annual_Report_FY24.pdf
TCS_Earnings_Q3_2024.pdf
INFY_Results_Dec2024.pdf
```

## 🚀 Usage Examples

### **Example 1: Perfect Match**

```python
# Your screener calls:
analysis = mcp_server.get_company_fundamentals("AARTIIND")

# Server finds:
# ✅ AARTIIND_Transcript.pdf (Score: 150)
# ✅ AARTIIND.pdf (Score: 100)

# Result: Rich analysis combining technical + fundamental data
```

### **Example 2: No Exact Match**

```python
# Your screener calls:
analysis = mcp_server.get_company_fundamentals("RELIANCE")

# Server searches:
# ❌ No RELIANCE_*.pdf files found
# ✅ Looks up company name: "RELIANCE INDUSTRIES"
# ✅ Finds documents containing "RELIANCE" or "INDUSTRIES"
# ⚠️ Fallback: Analyzes all PDFs if no matches

# Result: Technical analysis + any relevant document insights
```

### **Example 3: Debug Document Matching**

```python
# Use the debug tool to see what documents are found:
debug_info = mcp_server.find_company_documents("AARTIIND")

# Shows:
# 📁 All available documents (2):
#    1. AARTIIND.pdf
#    2. AARTIIND_Transcript.pdf
# 
# 🎯 Documents matched for AARTIIND (2):
#    1. AARTIIND_Transcript.pdf → exact symbol match, earnings transcript
#    2. AARTIIND.pdf → exact symbol match
```

## 🔧 Integration with Your Screener

### **Simple Integration**

```python
# Your existing screener code:
candidates = screen_stocks_by_technical_criteria()

# Enhanced with documents:
for stock in candidates:
    # Server automatically finds relevant documents
    comprehensive_analysis = mcp_server.get_company_fundamentals(stock.symbol)
    
    # Parse insights
    if "revenue growth" in comprehensive_analysis.lower():
        stock.fundamental_score += 20
    if "margin expansion" in comprehensive_analysis.lower():
        stock.fundamental_score += 15
    
    # Combined scoring
    stock.total_score = stock.technical_score + stock.fundamental_score
```

### **Batch Processing**

```python
symbols = ["AARTIIND", "RELIANCE", "TCS", "INFY"]

for symbol in symbols:
    # Each call automatically finds the right documents
    analysis = mcp_server.get_company_fundamentals(symbol)
    store_analysis(symbol, analysis)
```

## 📊 Claude Desktop Integration

### **Natural Language Queries**

You can now ask Claude:

✅ **"Analyze AARTIIND with latest documents"**
- Server automatically finds AARTIIND documents
- Combines with real-time technical data
- Provides comprehensive investment perspective

✅ **"Compare RELIANCE fundamentals vs technicals"**
- Finds RELIANCE-related documents
- Shows both fundamental and technical analysis
- Highlights key insights

✅ **"What documents are available for TCS?"**
- Uses `find_company_documents` tool
- Shows all relevant files
- Explains matching logic

## 🛠️ Troubleshooting

### **No Documents Found**

```
📄 FUNDAMENTAL ANALYSIS:
No PDF documents found in the data directory.
Please add company reports, transcripts, or annual reports to the data directory.
Example filenames: AARTIIND_Transcript.pdf, AARTIIND_Annual_Report.pdf
```

**Solution:** Add documents with stock symbol in filename.

### **Wrong Documents Matched**

Use the debug tool:
```python
debug_info = mcp_server.find_company_documents("SYMBOL")
```

This shows exactly which documents were found and why.

### **Multiple Company Documents**

The server automatically prioritizes:
1. Most recent documents (by file modification date)
2. More relevant document types (transcripts > reports > general)
3. Exact symbol matches over partial matches

## 🎯 Key Benefits

### **For Your Screener App**

1. **Zero Configuration** - Just pass the stock symbol
2. **Automatic Discovery** - Finds relevant documents without manual mapping
3. **Smart Prioritization** - Most important documents analyzed first
4. **Flexible Naming** - Works with various filename conventions
5. **Fallback Handling** - Still provides technical analysis if no documents

### **Perfect for Your Use Case**

```
Your Screener → "Give me fundamentals for AARTIIND"
    ↓
MCP Server → Automatically finds AARTIIND_Transcript.pdf + AARTIIND.pdf
    ↓
Returns → Technical metrics + Latest earnings insights + Investment perspective
    ↓
Your Screener → Enhanced stock scoring with latest fundamental data!
```

## 🚀 Next Steps

1. **Add more documents** to the `data/` directory using the recommended naming
2. **Test the matching** with `find_company_documents` tool
3. **Integrate with your screener** using the simple API calls
4. **Scale up** by processing multiple stocks in batch

Your MCP server now intelligently bridges technical analysis with the latest fundamental insights, automatically finding the right documents for any stock symbol! 🎉 