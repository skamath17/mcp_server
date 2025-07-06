#!/usr/bin/env python3
"""
Test mysql.connector approaches to identify URL parsing issue
"""
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error

def test_mysql_connector_parsed():
    """Test mysql.connector with URL parsing (our current approach)"""
    print("🔍 Testing mysql.connector with URL parsing...")
    
    try:
        # Parse the URL the way we do in the MCP server
        database_url = "mysql://mfuser:Mf_pass_03%@65.20.72.91:3306/mutualfunddb"
        parsed = urlparse(database_url)
        
        config = {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'connection_timeout': 10
        }
        
        print(f"📡 Original URL: {database_url}")
        print(f"📡 Parsed config:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   User: {config['user']}")
        print(f"   Password: '{config['password']}'")
        print(f"   Database: {config['database']}")
        
        print("🔄 Attempting connection with parsed config...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ mysql.connector (URL parsing) connection successful!")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"📁 Connected to database: {db_name}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ mysql.connector (URL parsing) Error: {e}")
        if hasattr(e, 'errno'):
            print(f"📍 Error code: {e.errno}")
        return False
    except Exception as e:
        print(f"❌ mysql.connector (URL parsing) failed: {e}")
        return False

def test_mysql_connector_direct():
    """Test mysql.connector with direct parameters (no URL parsing)"""
    print("\n🔍 Testing mysql.connector with direct parameters...")
    
    try:
        # Use direct parameters instead of URL parsing
        config = {
            'host': '65.20.72.91',
            'port': 3306,
            'user': 'mfuser',
            'password': 'Mf_pass_03%',  # Direct password
            'database': 'mutualfunddb',
            'connection_timeout': 10
        }
        
        print(f"📡 Direct config:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   User: {config['user']}")
        print(f"   Password: '{config['password']}'")
        print(f"   Database: {config['database']}")
        
        print("🔄 Attempting connection with direct config...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ mysql.connector (direct) connection successful!")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"📁 Connected to database: {db_name}")
            
            cursor.execute("SELECT COUNT(*) FROM Stock")
            count = cursor.fetchone()[0]
            print(f"📊 Stock table: {count} records")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ mysql.connector (direct) Error: {e}")
        if hasattr(e, 'errno'):
            print(f"📍 Error code: {e.errno}")
        return False
    except Exception as e:
        print(f"❌ mysql.connector (direct) failed: {e}")
        return False

def debug_url_parsing():
    """Debug the URL parsing to see what's wrong"""
    print("\n🔍 Debugging URL parsing...")
    
    database_url = "mysql://mfuser:Mf_pass_03%@65.20.72.91:3306/mutualfunddb"
    parsed = urlparse(database_url)
    
    print(f"📡 Original URL: {database_url}")
    print(f"📡 Parsed components:")
    print(f"   scheme: '{parsed.scheme}'")
    print(f"   hostname: '{parsed.hostname}'")
    print(f"   port: {parsed.port}")
    print(f"   username: '{parsed.username}'")
    print(f"   password: '{parsed.password}'")
    print(f"   path: '{parsed.path}'")
    print(f"   database (path.lstrip('/')): '{parsed.path.lstrip('/') if parsed.path else None}'")
    
    # Check if password needs URL decoding
    from urllib.parse import unquote
    decoded_password = unquote(parsed.password) if parsed.password else None
    print(f"   password (URL decoded): '{decoded_password}'")

def main():
    """Compare mysql.connector approaches"""
    print("🚀 MySQL Connector Comparison Test")
    print("=" * 50)
    
    # Debug URL parsing first
    debug_url_parsing()
    
    # Test 1: mysql.connector with URL parsing (our current approach)  
    mysql_parsed_ok = test_mysql_connector_parsed()
    
    # Test 2: mysql.connector with direct parameters
    mysql_direct_ok = test_mysql_connector_direct()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY:")
    print(f"   mysql.connector (URL parsing): {'✅ PASS' if mysql_parsed_ok else '❌ FAIL'}")
    print(f"   mysql.connector (direct):      {'✅ PASS' if mysql_direct_ok else '❌ FAIL'}")
    
    if mysql_direct_ok and not mysql_parsed_ok:
        print("\n🔧 DIAGNOSIS: URL parsing issue!")
        print("   Direct parameters work, but URL parsing fails")
        print("   Solution: Fix URL parsing or use direct parameters in MCP server")
    elif mysql_parsed_ok and mysql_direct_ok:
        print("\n✅ Both approaches work! The issue is elsewhere.")
    elif not mysql_direct_ok and not mysql_parsed_ok:
        print("\n❌ Both approaches fail - check credentials/network")

if __name__ == "__main__":
    main() 