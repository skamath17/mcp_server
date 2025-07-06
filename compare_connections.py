#!/usr/bin/env python3
"""
Compare SQLAlchemy vs mysql.connector connections
"""
import os
from urllib.parse import urlparse

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection (should work)"""
    print("🔍 Testing SQLAlchemy connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Use the same approach as your working app
        DATABASE_URL = "mysql://mfuser:Mf_pass_03%@65.20.72.91:3306/mutualfunddb"
        
        print(f"📡 DATABASE_URL: {DATABASE_URL}")
        
        engine = create_engine(DATABASE_URL)
        
        # Test the connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"✅ SQLAlchemy connection successful!")
            print(f"📁 Connected to database: {db_name}")
            
            # Test table access
            result = connection.execute(text("SELECT COUNT(*) FROM Stock"))
            count = result.fetchone()[0]
            print(f"📊 Stock table: {count} records")
            
            return True
            
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def test_mysql_connector_parsed():
    """Test mysql.connector with URL parsing (our current approach)"""
    print("\n🔍 Testing mysql.connector with parsed URL...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
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
        
        print(f"📡 Parsed config:")
        print(f"   Host: {config['host']}")
        print(f"   Port: {config['port']}")
        print(f"   User: {config['user']}")
        print(f"   Password: {config['password']}")
        print(f"   Database: {config['database']}")
        
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ mysql.connector connection successful!")
            
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
        print(f"❌ mysql.connector Error: {e}")
        if hasattr(e, 'errno'):
            print(f"📍 Error code: {e.errno}")
        return False
    except Exception as e:
        print(f"❌ mysql.connector failed: {e}")
        return False

def test_mysql_connector_direct():
    """Test mysql.connector with direct parameters (no URL parsing)"""
    print("\n🔍 Testing mysql.connector with direct parameters...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
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
        print(f"   Password: {config['password']}")
        print(f"   Database: {config['database']}")
        
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ mysql.connector (direct) connection successful!")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"📁 Connected to database: {db_name}")
            
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

def main():
    """Compare all connection methods"""
    print("🚀 Database Connection Comparison Test")
    print("=" * 50)
    
    # Test 1: SQLAlchemy (known working)
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    # Test 2: mysql.connector with URL parsing (our current approach)  
    mysql_parsed_ok = test_mysql_connector_parsed()
    
    # Test 3: mysql.connector with direct parameters
    mysql_direct_ok = test_mysql_connector_direct()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY:")
    print(f"   SQLAlchemy:           {'✅ PASS' if sqlalchemy_ok else '❌ FAIL'}")
    print(f"   mysql.connector (URL): {'✅ PASS' if mysql_parsed_ok else '❌ FAIL'}")
    print(f"   mysql.connector (direct): {'✅ PASS' if mysql_direct_ok else '❌ FAIL'}")
    
    if sqlalchemy_ok and not mysql_parsed_ok:
        print("\n🔧 DIAGNOSIS: URL parsing issue!")
        print("   The connection works with SQLAlchemy but fails with mysql.connector URL parsing")
        print("   Solution: Fix URL parsing or use direct parameters")
    elif sqlalchemy_ok and mysql_direct_ok and not mysql_parsed_ok:
        print("\n🔧 DIAGNOSIS: URL parsing issue confirmed!")
        print("   Direct parameters work, URL parsing doesn't")

if __name__ == "__main__":
    main() 