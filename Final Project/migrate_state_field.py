#!/usr/bin/env python3
"""
Database migration script to add state field to Profile table
"""

from app import app, db, Profile

def migrate_state_field():
    """Add state field to Profile table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if state column already exists
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [column['name'] for column in inspector.get_columns('profile')]
            
            if 'state' not in columns:
                # Add state column using proper SQLAlchemy syntax
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE profile ADD COLUMN state VARCHAR(50)'))
                print("State field added to Profile table")
            else:
                print("State field already exists in Profile table")
                
            # Commit the changes
            db.session.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Migration failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_state_field()
