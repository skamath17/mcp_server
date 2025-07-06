#!/usr/bin/env python3
"""
Simple MySQL database connection test
"""
import mysql.connector
from mysql.connector import Error
import socket
import time

def test_network_connectivity():
    """Test basic network connectivity to MySQL server"""
    print("🔍 Testing network connectivity...")
    
    host = "65.20.72.91"
    port = 3306
    timeout = 5
    
    try:
        print(f"📡 Connecting to {host}:{port} with {timeout}s timeout...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        sock.close()
        
        if result == 0:
            print(f"✅ Network connection successful! ({end_time-start_time:.2f}s)")
            return True
        else:
            print(f"❌ Network connection failed (error code: {result})")
            return False
            
    except socket.timeout:
        print("❌ Network connection timed out")
        return False
    except Exception as e:
        print(f"❌ Network test error: {e}")
        return False

def test_mysql_connection():
    """Test MySQL database connection with detailed logging"""
    print("\n🔍 Testing MySQL connection...")
    
    # Connection parameters
    config = {
        'host': '65.20.72.91',
        'port': 3306,
        'user': 'mfuser',  
        'password': 'Mf_pass_03%',
        'database': 'mutualfunddb',
        'connection_timeout': 10,
        'autocommit': True
    }
    
    print(f"📡 MySQL Config:")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   User: {config['user']}")
    print(f"   Database: {config['database']}")
    print(f"   Timeout: {config['connection_timeout']}s")
    
    try:
        print("🔄 Attempting MySQL connection...")
        start_time = time.time()
        
        # Add more detailed timeout handling
        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError("MySQL connection timed out")
        
        # Set timeout (Windows compatible)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)  # 15 second timeout
        except AttributeError:
            # Windows doesn't support SIGALRM
            pass
        
        connection = mysql.connector.connect(**config)
        
        try:
            signal.alarm(0)  # Cancel timeout
        except AttributeError:
            pass
        
        end_time = time.time()
        print(f"✅ MySQL connection successful! ({end_time-start_time:.2f}s)")
        
        if connection.is_connected():
            # Get server info
            db_info = connection.get_server_info()
            print(f"📊 MySQL Server version: {db_info}")
            
            # Test a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            record = cursor.fetchone()
            print(f"📁 Connected to database: {record[0]}")
            
            # Test table access
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables in database")
            
            # Test specific tables
            test_tables = ['Stock', 'PriceHistory', 'AdvancedStockMetrics']
            for table in test_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table}: {count} records")
                except Error as e:
                    print(f"   ❌ {table}: {e}")
            
            cursor.close()
            connection.close()
            print("✅ Database test completed successfully!")
            return True
            
    except TimeoutError:
        print("❌ MySQL connection timed out (15s)")
        print("🔧 This usually means:")
        print("   - Authentication is failing")
        print("   - User doesn't have permission from your IP")
        print("   - Database server is rejecting the connection")
        return False
    except Error as e:
        print(f"❌ MySQL Error: {e}")
        print(f"📍 Error code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
        
        # Common MySQL error codes
        if hasattr(e, 'errno'):
            if e.errno == 1045:
                print("🔧 Error 1045: Access denied - wrong username/password")
            elif e.errno == 1049:
                print("🔧 Error 1049: Database doesn't exist")
            elif e.errno == 1130:
                print("🔧 Error 1130: Host not allowed to connect")
            elif e.errno == 2003:
                print("🔧 Error 2003: Can't connect to MySQL server")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        return False

def main():
    """Run database connection tests"""
    print("🚀 MySQL Database Connection Test")
    print("=" * 40)
    
    # Test 1: Network connectivity
    network_ok = test_network_connectivity()
    
    if not network_ok:
        print("\n❌ Network connectivity failed - cannot reach MySQL server")
        print("🔧 Possible issues:")
        print("   - Server is down")
        print("   - Firewall blocking port 3306")
        print("   - Network connectivity issues")
        return 1
    
    # Test 2: MySQL connection
    mysql_ok = test_mysql_connection()
    
    print("\n" + "=" * 40)
    if network_ok and mysql_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Database is accessible and working correctly")
        print("✅ Your MCP server should be able to connect")
        return 0
    else:
        print("❌ Database connection issues detected")
        return 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    exit(exit_code) 