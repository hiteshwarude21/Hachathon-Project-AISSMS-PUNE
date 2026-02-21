#!/usr/bin/env python3
"""
Migration script to add missing columns to AdminAlert table
"""

import sqlite3
import os

def migrate_admin_alert():
    """Add missing columns to AdminAlert table"""
    db_path = 'instance/database.db'
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(admin_alert)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'state' not in columns:
            cursor.execute("ALTER TABLE admin_alert ADD COLUMN state TEXT")
            print("Added 'state' column")
        
        if 'district' not in columns:
            cursor.execute("ALTER TABLE admin_alert ADD COLUMN district TEXT")
            print("Added 'district' column")
        
        if 'land_size' not in columns:
            cursor.execute("ALTER TABLE admin_alert ADD COLUMN land_size REAL")
            print("Added 'land_size' column")
        
        if 'category' not in columns:
            cursor.execute("ALTER TABLE admin_alert ADD COLUMN category TEXT")
            print("Added 'category' column")
        
        if 'processed_at' not in columns:
            cursor.execute("ALTER TABLE admin_alert ADD COLUMN processed_at DATETIME")
            print("Added 'processed_at' column")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_admin_alert()
