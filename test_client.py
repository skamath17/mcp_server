#!/usr/bin/env python3
"""
Simple test client for the Stock MCP Server
"""
import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """Test the MCP server by calling its tools"""
    print("🔍 Testing Stock MCP Server...")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "stock_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test 1: List available tools
        print("\n📋 Test 1: Listing available tools...")
        list_tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            result = json.loads(response)
            tools = result.get("result", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        # Test 2: Search for stocks
        print("\n🔍 Test 2: Searching for stocks...")
        search_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search_stocks",
                "arguments": {"pattern": "A", "limit": 3}
            },
            "id": 2
        }
        
        process.stdin.write(json.dumps(search_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            result = json.loads(response)
            if "result" in result:
                print("✅ Search results received:")
                content = result["result"][0]["text"]
                print(f"   {content[:200]}...")
            else:
                print("❌ No results from search")
        
        print("\n🎉 MCP Server test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 