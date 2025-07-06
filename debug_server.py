#!/usr/bin/env python3
"""
Debug wrapper for Stock MCP Server to catch exit issues
"""
import sys
import traceback

def main():
    """Run the server with comprehensive error handling"""
    print("🚀 Starting Stock MCP Server with debug info...")
    
    try:
        # Import and run the server
        from stock_mcp_server import main as server_main
        import asyncio
        
        print("✅ Server imports successful")
        print("🔄 Starting server main loop...")
        
        # Run the server
        asyncio.run(server_main())
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user (Ctrl+C)")
        return 0
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Check if all dependencies are installed")
        return 1
    except Exception as e:
        print(f"❌ Server crashed with error: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return 1
    except SystemExit as e:
        print(f"🚪 Server exited with code: {e.code}")
        return e.code if e.code is not None else 0
    
    print("✅ Server completed normally")
    return 0

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Process exiting with code: {exit_code}")
    sys.exit(exit_code) 