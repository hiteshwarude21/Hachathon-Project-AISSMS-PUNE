#!/usr/bin/env python3
"""
Database migration script to add missing columns to existing database
"""
import sqlite3
import os

def migrate_database():
    db_path = 'instance/database.db'
    
    if not os.path.exists(db_path):
        print("Database not found. A new one will be created automatically.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if name column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'name' not in columns:
            print("Adding 'name' column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN name VARCHAR(100)")
        
        if 'role' not in columns:
            print("Adding 'role' column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'farmer'")
        
        # Update existing users to have role and name
        cursor.execute("UPDATE user SET role = 'farmer' WHERE role IS NULL")
        cursor.execute("UPDATE user SET name = username WHERE name IS NULL")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
