#!/usr/bin/env python3
"""
Example Integration: Screener App <-> MCP Server
Shows how your technical screener can access the MCP server for fundamental analysis
"""

import subprocess
import json
import asyncio
from typing import Dict, Any, List

class MCPStockAnalyzer:
    """
    Wrapper class to interact with the MCP Stock Server from your screener app
    """
    
    def __init__(self, mcp_server_path: str = "stock_mcp_server.py"):
        self.mcp_server_path = mcp_server_path
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process"""
        self.process = subprocess.Popen(
            ["python", self.mcp_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.process:
            await self.start_server()
        
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        return json.loads(response_line) if response_line else {}
    
    async def get_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get both technical metrics and fundamental insights for a stock
        This is the key method your screener would call
        """
        try:
            # Get technical analysis
            technical_result = await self.call_tool("get_advanced_metrics", {
                "symbol": symbol,
                "timeframe": "medium"
            })
            
            # Get fundamental analysis from documents
            fundamental_result = await self.call_tool("get_company_fundamentals", {
                "symbol": symbol,
                "document_pattern": ""
            })
            
            # Get latest price data
            price_result = await self.call_tool("get_price_history", {
                "symbol": symbol,
                "period": "daily"
            })
            
            return {
                "symbol": symbol,
                "technical_analysis": technical_result.get("result", [{}])[0].get("text", ""),
                "fundamental_analysis": fundamental_result.get("result", [{}])[0].get("text", ""),
                "recent_prices": price_result.get("result", [{}])[0].get("text", ""),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "status": "error"
            }
    
    async def screen_stocks_with_fundamentals(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Screen stocks based on technical criteria, then enrich with fundamental insights
        """
        try:
            # First, screen based on technical criteria
            screening_result = await self.call_tool("screen_stocks_by_metrics", {
                "criteria": criteria
            })
            
            screening_text = screening_result.get("result", [{}])[0].get("text", "")
            
            # Parse the screening results to extract symbols
            symbols = self._parse_screening_results(screening_text)
            
            # Get comprehensive analysis for each symbol
            enriched_results = []
            for symbol in symbols[:5]:  # Limit to top 5 for demo
                comprehensive = await self.get_comprehensive_analysis(symbol)
                enriched_results.append(comprehensive)
            
            return enriched_results
            
        except Exception as e:
            return [{"error": str(e), "status": "error"}]
    
    def _parse_screening_results(self, screening_text: str) -> List[str]:
        """Parse symbols from screening results text"""
        symbols = []
        lines = screening_text.split('\n')
        for line in lines:
            if '|' in line and len(line.split('|')) > 1:
                symbol = line.split('|')[0].strip()
                if symbol and symbol.isupper() and len(symbol) <= 10:
                    symbols.append(symbol)
        return symbols
    
    async def analyze_document(self, filename: str, analysis_type: str = "financial_highlights") -> Dict[str, Any]:
        """Analyze a specific document"""
        try:
            result = await self.call_tool("analyze_document", {
                "filename": filename,
                "analysis_type": analysis_type,
                "output_format": "structured"
            })
            
            return {
                "filename": filename,
                "analysis": result.get("result", [{}])[0].get("text", ""),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "status": "error"
            }
    
    async def list_available_documents(self) -> List[str]:
        """List all available documents for analysis"""
        try:
            result = await self.call_tool("list_documents", {})
            documents_text = result.get("result", [{}])[0].get("text", "")
            
            # Parse document names from the response
            documents = []
            lines = documents_text.split('\n')
            for line in lines:
                if line.strip().endswith('.pdf'):
                    documents.append(line.strip().replace('📄 ', ''))
            
            return documents
            
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def close(self):
        """Clean up the MCP server process"""
        if self.process:
            self.process.terminate()
            self.process = None

# Example Usage for your Screener App
async def demo_screener_integration():
    """
    Demo showing how your screener app would integrate with the MCP server
    """
    print("🔍 Stock Screener + MCP Server Integration Demo")
    print("=" * 50)
    
    # Initialize the MCP analyzer
    analyzer = MCPStockAnalyzer()
    
    try:
        # Example: Get comprehensive analysis for a stock
        print("\n🔍 Comprehensive Analysis for AARTIIND (matching your PDF)")
        analysis = await analyzer.get_comprehensive_analysis("AARTIIND")
        
        print(f"\nTechnical Analysis:")
        print(f"{analysis.get('technical_analysis', 'No technical data')[:300]}...")
        
        print(f"\nFundamental Analysis from Documents:")
        print(f"{analysis.get('fundamental_analysis', 'No documents found')[:300]}...")
        
        print("\n✅ Integration demo completed!")
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
    
    finally:
        analyzer.close()

# FastAPI Integration Example (for web-based screener)
def create_screener_api():
    """
    Example FastAPI integration for web-based screener
    """
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        
        app = FastAPI(title="Enhanced Stock Screener API")
        
        class ScreeningCriteria(BaseModel):
            min_sharpe_ratio: float = None
            max_volatility: float = None
            min_rsi: float = None
            max_rsi: float = None
            sector: str = None
            limit: int = 10
        
        @app.post("/screen-stocks")
        async def screen_stocks(criteria: ScreeningCriteria):
            """Screen stocks with both technical and fundamental analysis"""
            analyzer = MCPStockAnalyzer()
            try:
                results = await analyzer.screen_stocks_with_fundamentals(criteria.dict())
                return {"results": results, "count": len(results)}
            finally:
                analyzer.close()
        
        @app.get("/analyze/{symbol}")
        async def analyze_stock(symbol: str):
            """Get comprehensive analysis for a specific stock"""
            analyzer = MCPStockAnalyzer()
            try:
                analysis = await analyzer.get_comprehensive_analysis(symbol)
                return analysis
            finally:
                analyzer.close()
        
        @app.get("/documents")
        async def list_documents():
            """List available documents for analysis"""
            analyzer = MCPStockAnalyzer()
            try:
                documents = await analyzer.list_available_documents()
                return {"documents": documents}
            finally:
                analyzer.close()
        
        return app
    
    except ImportError:
        print("FastAPI not installed. To use web API: pip install fastapi uvicorn")
        return None

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_screener_integration())
    
    # Optionally start the FastAPI server
    # app = create_screener_api()
    # if app:
    #     import uvicorn
    #     uvicorn.run(app, host="0.0.0.0", port=8000) 