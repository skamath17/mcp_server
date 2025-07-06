#!/usr/bin/env python3
"""
Detailed debug wrapper to trace exactly where the server stops
"""
import sys
import traceback
import asyncio
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("detailed-debug")

async def debug_database_connection():
    """Test database connection step by step"""
    logger.info("🔍 Testing database connection step by step...")
    
    try:
        from stock_mcp_server import StockMCPServer
        
        logger.info("✅ StockMCPServer imported successfully")
        
        # Create server instance
        logger.info("🔄 Creating server instance...")
        server = StockMCPServer()
        logger.info("✅ Server instance created")
        
        # Try database connection
        logger.info("🔄 Attempting database connection...")
        await server.connect_database()
        logger.info("✅ Database connection successful!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.error(f"📍 Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

async def debug_mcp_server_startup():
    """Test MCP server startup step by step"""
    logger.info("🔍 Testing MCP server startup...")
    
    try:
        from stock_mcp_server import StockMCPServer
        
        # Create server instance
        server = StockMCPServer()
        logger.info("✅ Server instance created")
        
        # Try database connection
        logger.info("🔄 Connecting to database...")
        await server.connect_database()
        logger.info("✅ Database connected")
        
        # Now try to start the MCP server
        logger.info("🔄 Starting MCP server loop...")
        
        # This is where the server should stay running
        logger.info("⏳ Server should now be waiting for MCP connections...")
        logger.info("🔍 If you see this message, the server setup is working!")
        logger.info("❗ The server should stay running here (no more messages)")
        
        # Simulate what the real server does - run the MCP server
        async with server.server.run_stdio() as (read_stream, write_stream):
            from mcp.server.models import InitializationOptions
            from mcp.server import NotificationOptions
            
            logger.info("🚀 MCP server is now running and waiting for connections...")
            
            await server.server.run(
                read_stream, 
                write_stream,
                InitializationOptions(
                    server_name="stock-database-server",
                    server_version="1.0.0",
                    capabilities=server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
        
    except Exception as e:
        logger.error(f"❌ MCP server startup failed: {e}")
        logger.error(f"📍 Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

async def main():
    """Run detailed debugging"""
    logger.info("🚀 Starting detailed debug session...")
    
    # Step 1: Test database connection
    logger.info("=" * 50)
    logger.info("STEP 1: Testing Database Connection")
    logger.info("=" * 50)
    
    db_success = await debug_database_connection()
    
    if not db_success:
        logger.error("❌ Database connection failed - stopping here")
        return 1
    
    # Step 2: Test MCP server startup
    logger.info("=" * 50)
    logger.info("STEP 2: Testing MCP Server Startup")
    logger.info("=" * 50)
    
    try:
        await debug_mcp_server_startup()
        logger.info("✅ MCP server completed normally")
        return 0
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user (Ctrl+C)")
        return 0
    except Exception as e:
        logger.error(f"❌ MCP server failed: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        logger.info(f"🏁 Debug session completed with exit code: {exit_code}")
    except Exception as e:
        logger.error(f"❌ Debug session crashed: {e}")
        traceback.print_exc()
        exit_code = 1
    
    sys.exit(exit_code) 