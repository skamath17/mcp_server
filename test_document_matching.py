#!/usr/bin/env python3
"""
Test script to demonstrate smart document matching
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from stock_mcp_server import StockMCPServer

async def test_document_matching():
    """Test the smart document matching functionality"""
    print("🔍 Testing Smart Document Matching")
    print("=" * 40)
    
    # Initialize server
    server = StockMCPServer()
    
    try:
        # Test database connection
        await server.connect_database()
        
        # Test 1: Symbol with exact match (AARTIIND)
        print("\n📄 Test 1: Symbol with exact filename match")
        result = await server.find_company_documents("AARTIIND")
        print(result[0].text)
        
        # Test 2: Symbol without exact match (try RELIANCE if no RELIANCE.pdf exists)
        print("\n📄 Test 2: Symbol without exact filename match")
        result = await server.find_company_documents("RELIANCE")
        print(result[0].text)
        
        # Test 3: Show comprehensive analysis with the smart matching
        print("\n🎯 Test 3: Comprehensive analysis using smart matching")
        result = await server.get_company_fundamentals("AARTIIND", "")
        print(result[0].text[:500] + "...")
        
        print("\n✅ Document matching tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if server.engine:
            server.engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_document_matching()) 