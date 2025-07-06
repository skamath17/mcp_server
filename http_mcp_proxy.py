#!/usr/bin/env python3
"""
HTTP Proxy for Stock MCP Server
Provides REST API endpoints that internally call the MCP server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from pathlib import Path

# Get the MCP server path
MCP_SERVER_PATH = str(Path(__file__).parent / "stock_mcp_server.py")

app = FastAPI(
    title="Stock Analysis API",
    description="HTTP API wrapper for Stock MCP Server",
    version="1.0.0"
)

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class StockAnalysisRequest(BaseModel):
    symbol: str
    document_pattern: Optional[str] = ""

class PriceHistoryRequest(BaseModel):
    symbol: str
    period: str = "daily"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ScreeningRequest(BaseModel):
    criteria: Dict[str, Any]

class MCP_Client:
    """Helper class to manage MCP server communication"""
    
    @staticmethod
    async def call_mcp_tool(tool_name: str, arguments: dict):
        """Call a tool on the MCP server and return the result"""
        try:
            # Use the virtual environment Python if available
            python_cmd = "python"
            venv_python = Path("stock-mcp-env/Scripts/python.exe")
            if venv_python.exists():
                python_cmd = str(venv_python)
            
            server_params = StdioServerParameters(
                command=python_cmd,
                args=[MCP_SERVER_PATH]
            )
            
            async with stdio_client(server_params) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Extract text content from result
                    if result and hasattr(result, 'content') and result.content:
                        return [item.text for item in result.content if hasattr(item, 'text')]
                    elif result:
                        return str(result)
                    return "No result returned"
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise HTTPException(status_code=500, detail=f"MCP server error: {str(e)}\n{error_details}")

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Stock Analysis API - HTTP wrapper for MCP server",
        "version": "1.0.0",
        "endpoints": {
            "stock_info": "/api/stocks/{symbol}",
            "fundamentals": "/api/stocks/{symbol}/fundamentals",
            "price_history": "/api/stocks/{symbol}/history",
            "search": "/api/stocks/search/{pattern}",
            "advanced_metrics": "/api/stocks/{symbol}/metrics",
            "screen": "/api/stocks/screen",
            "documents": "/api/stocks/{symbol}/documents"
        }
    }

@app.get("/api/stocks/{symbol}")
async def get_stock_info(symbol: str):
    """Get basic stock information"""
    result = await MCP_Client.call_mcp_tool("get_stock_info", {"symbol": symbol})
    return {"symbol": symbol, "data": result}

@app.get("/api/stocks/{symbol}/fundamentals")
async def get_fundamentals(symbol: str, document_pattern: str = ""):
    """Get fundamental analysis combining technical data and PDF documents"""
    result = await MCP_Client.call_mcp_tool("get_company_fundamentals", {
        "symbol": symbol,
        "document_pattern": document_pattern
    })
    return {"symbol": symbol, "fundamental_analysis": result}

@app.post("/api/stocks/{symbol}/history")
async def get_price_history(symbol: str, request: PriceHistoryRequest):
    """Get historical price data"""
    result = await MCP_Client.call_mcp_tool("get_price_history", {
        "symbol": symbol,
        "period": request.period,
        "start_date": request.start_date,
        "end_date": request.end_date
    })
    return {"symbol": symbol, "price_history": result}

@app.get("/api/stocks/search/{pattern}")
async def search_stocks(pattern: str, limit: int = 10):
    """Search for stocks by symbol or company name"""
    result = await MCP_Client.call_mcp_tool("search_stocks", {
        "pattern": pattern,
        "limit": limit
    })
    return {"pattern": pattern, "results": result}

@app.get("/api/stocks/{symbol}/metrics")
async def get_advanced_metrics(symbol: str, timeframe: str = "medium"):
    """Get advanced technical and risk metrics"""
    result = await MCP_Client.call_mcp_tool("get_advanced_metrics", {
        "symbol": symbol,
        "timeframe": timeframe
    })
    return {"symbol": symbol, "metrics": result}

@app.post("/api/stocks/screen")
async def screen_stocks(request: ScreeningRequest):
    """Screen stocks based on criteria"""
    result = await MCP_Client.call_mcp_tool("screen_stocks_by_metrics", {
        "criteria": request.criteria
    })
    return {"criteria": request.criteria, "results": result}

@app.get("/api/stocks/{symbol}/documents")
async def get_stock_documents(symbol: str):
    """Get available documents for a stock (debug info)"""
    result = await MCP_Client.call_mcp_tool("find_company_documents", {
        "symbol": symbol
    })
    return {"symbol": symbol, "documents": result}

@app.get("/api/documents")
async def list_all_documents():
    """List all available PDF documents"""
    result = await MCP_Client.call_mcp_tool("list_documents", {})
    return {"documents": result}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MCP server connectivity
        result = await MCP_Client.call_mcp_tool("search_stocks", {"pattern": "TEST", "limit": 1})
        return {"status": "healthy", "mcp_server": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Stock Analysis HTTP API")
    print(f"📄 MCP Server: {MCP_SERVER_PATH}")
    print("🌐 API will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    ) 