import sqlite3
import os
from tabulate import tabulate

# Path to your database
db_path = os.path.join('database', 'college_chatbot.db')

try:
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*60)
    print("COLLEGE CHATBOT DATABASE INSPECTION")
    print("="*60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📊 Tables in database: {[table[0] for table in tables]}")
    
    # Show data from each table
    for table in tables:
        table_name = table[0]
        print(f"\n{'─'*60}")
        print(f"📋 Table: {table_name}")
        print(f"{'─'*60}")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Columns: {', '.join(column_names)}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Rows: {count}")
        
        # Show data if there are rows
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
            rows = cursor.fetchall()
            print(f"\nData (first 10 rows):")
            print(tabulate(rows, headers=column_names, tablefmt="grid"))
        else:
            print("No data in this table")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")