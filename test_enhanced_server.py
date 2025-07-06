#!/usr/bin/env python3
"""
Test script for the enhanced MCP server with PDF processing
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from stock_mcp_server import StockMCPServer

async def test_enhanced_server():
    """Test all the enhanced functionality"""
    print("🧪 Testing Enhanced MCP Server")
    print("=" * 40)
    
    # Initialize server
    server = StockMCPServer()
    
    try:
        # Test database connection
        print("\n📊 Testing database connection...")
        await server.connect_database()
        print("✅ Database connected successfully!")
        
        # Test basic stock info
        print("\n📈 Testing stock info retrieval...")
        result = await server.get_stock_info("AARTIIND")
        print(f"✅ Stock info: {result[0].text[:100]}...")
        
        # Test document listing
        print("\n📄 Testing document listing...")
        docs = await server.list_documents()
        print(f"✅ Documents found: {docs[0].text[:200]}...")
        
        # Test document analysis if documents exist
        print("\n🔍 Testing document analysis...")
        pdf_files = list(Path("data").glob("*.pdf"))
        if pdf_files:
            doc_result = await server.analyze_document(
                pdf_files[0].name, 
                "structured", 
                "summary"
            )
            print(f"✅ Document analysis: {doc_result[0].text[:200]}...")
        else:
            print("⚠️  No PDF documents found in data/ directory")
        
        # Test comprehensive analysis
        print("\n🎯 Testing comprehensive analysis...")
        comprehensive = await server.get_company_fundamentals("AARTIIND", "")
        print(f"✅ Comprehensive analysis: {comprehensive[0].text[:200]}...")
        
        print("\n🎉 All tests passed! Enhanced MCP server is ready.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if server.engine:
            server.engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_enhanced_server()) 