#!/usr/bin/env python3
"""
Diagnostic script for checking Python environment on cPanel
Run this script after deployment to diagnose issues
"""

import sys
import os
import platform
import sqlite3
import importlib.util

def check_module(module_name):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False, None
        module = importlib.import_module(module_name)
        return True, getattr(module, "__version__", "Unknown")
    except ImportError:
        return False, None
    except Exception as e:
        return False, str(e)

def main():
    """Run diagnostic checks"""
    print("DIAGNOSTIC REPORT")
    print("=================\n")
    
    # System information
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check critical modules
    modules = [
        "fastapi", "uvicorn", "aiosqlite", "jinja2", 
        "pydantic", "typing_extensions"
    ]
    
    print("\nModule Checks:")
    for module in modules:
        installed, version = check_module(module)
        status = f"✓ {version}" if installed else "✗ Not found"
        print(f"  {module}: {status}")
    
    # Check files and directories
    print("\nFile Checks:")
    files_to_check = [
        "app.py", "passenger_wsgi.py", ".htaccess", 
        "static", "templates", "content_bank.db"
    ]
    
    for file in files_to_check:
        exists = os.path.exists(file)
        status = "✓ Found" if exists else "✗ Not found"
        if exists:
            if os.path.isdir(file):
                status += f" (directory, {len(os.listdir(file))} items)"
            else:
                status += f" ({os.path.getsize(file)} bytes)"
        print(f"  {file}: {status}")
    
    # Check database
    print("\nDatabase Check:")
    try:
        conn = sqlite3.connect("content_bank.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"  Connected successfully, found {len(tables)} tables:")
        for table in tables:
            print(f"    - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"  Failed to connect to database: {e}")
    
    print("\nLog files:")
    log_files = ["app_error.log", "error.log"]
    for log in log_files:
        if os.path.exists(log):
            size = os.path.getsize(log)
            print(f"  {log}: {size} bytes")
            if size > 0 and size < 10000:  # Show contents if not too large
                print("  Contents:")
                with open(log, 'r') as f:
                    print("    " + "\n    ".join(f.readlines()[-10:]))  # Last 10 lines
        else:
            print(f"  {log}: Not found")

if __name__ == "__main__":
    main() 