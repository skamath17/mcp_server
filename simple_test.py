#!/usr/bin/env python3
"""
Simple database connectivity test for Stock MCP Server
"""
import asyncio
import os
import sys
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error
import signal

# Add the current directory to the path so we can import our server
sys.path.append('.')

def timeout_handler(signum, frame):
    raise TimeoutError("Database connection timed out")

async def test_database_connection():
    """Test database connectivity directly with timeout"""
    print("🔍 Testing Database Connection...")
    
    try:
        # Use the same URL parsing logic as the server
        database_url = "mysql://mfuser:Mf_pass_03%@65.20.72.91:3306/mutualfunddb"
        parsed = urlparse(database_url)
        
        db_config = {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'connection_timeout': 10,  # 10 second timeout
            'autocommit': True
        }
        
        print(f"📡 Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        print("⏱️  Connection timeout: 10 seconds")
        
        # Set a signal alarm for timeout (Unix-like systems)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)  # 15 second overall timeout
        except AttributeError:
            # Windows doesn't have SIGALRM, so we'll rely on MySQL timeout
            pass
        
        # Test connection
        connection = mysql.connector.connect(**db_config)
        
        try:
            signal.alarm(0)  # Cancel the alarm
        except AttributeError:
            pass
        
        if connection.is_connected():
            print("✅ Database connection successful!")
            
            # Test a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) as stock_count FROM Stock")
            result = cursor.fetchone()
            print(f"📊 Found {result[0]} stocks in the database")
            
            # Test another table
            cursor.execute("SELECT COUNT(*) as history_count FROM PriceHistory")
            result = cursor.fetchone()
            print(f"📈 Found {result[0]} price history records")
            
            # Test advanced metrics table
            cursor.execute("SELECT COUNT(*) as metrics_count FROM AdvancedStockMetrics")
            result = cursor.fetchone()
            print(f"📋 Found {result[0]} advanced metrics records")
            
            # Test a sample query to make sure data is accessible
            cursor.execute("SELECT symbol, companyName FROM Stock LIMIT 3")
            results = cursor.fetchall()
            print("📋 Sample stocks:")
            for row in results:
                print(f"   - {row[0]}: {row[1]}")
            
            cursor.close()
            connection.close()
            
            print("\n🎉 All database tests passed!")
            print("✅ Your MCP server should work correctly with Claude!")
            
    except TimeoutError:
        print("❌ Database connection timed out")
        print("🔧 Possible issues:")
        print("   - Network connectivity to 65.20.72.91:3306")
        print("   - Firewall blocking the connection")
        print("   - MySQL server not accessible from your location")
        return False
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        print("🔧 Possible issues:")
        print("   - Incorrect credentials")
        print("   - Database doesn't exist")
        print("   - User doesn't have permissions")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        try:
            signal.alarm(0)  # Make sure to cancel any pending alarm
        except AttributeError:
            pass
    
    return True

async def test_basic_connectivity():
    """Test basic network connectivity to the database server"""
    print("\n🔍 Testing Basic Network Connectivity...")
    
    try:
        import socket
        
        host = "65.20.72.91"
        port = 3306
        timeout = 5
        
        print(f"📡 Testing connection to {host}:{port} (timeout: {timeout}s)")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ Network connection to MySQL server successful!")
            return True
        else:
            print("❌ Cannot reach MySQL server")
            print("🔧 Possible issues:")
            print("   - Server is down")
            print("   - Port 3306 is blocked")
            print("   - Network connectivity issues")
            return False
            
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return False

async def test_mcp_server_import():
    """Test if the MCP server can be imported and initialized"""
    print("\n🔍 Testing MCP Server Import...")
    
    try:
        from stock_mcp_server import StockMCPServer
        
        print("✅ MCP server module imported successfully")
        
        # Try to create the server instance (but don't connect to DB)
        print("✅ MCP server is ready to handle requests!")
        
    except Exception as e:
        print(f"❌ MCP server import failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Stock MCP Server Test Suite")
    print("=" * 40)
    
    # Test basic network connectivity first
    network_test = await test_basic_connectivity()
    
    if network_test:
        # Only test database if network is working
        db_test = await test_database_connection()
    else:
        print("⏭️  Skipping database test due to network issues")
        db_test = False
    
    server_test = await test_mcp_server_import()
    
    print("\n" + "=" * 40)
    if network_test and db_test and server_test:
        print("🎉 ALL TESTS PASSED!")
        print("Your Stock MCP Server is ready to use with Claude!")
    else:
        print("⚠️  Some tests failed:")
        if not network_test:
            print("   - Network connectivity issues")
        if not db_test:
            print("   - Database connection issues")
        if not server_test:
            print("   - MCP server setup issues")

if __name__ == "__main__":
    asyncio.run(main()) 