"""
Database table creation module for Neighborhood Complaint & Feedback System
Creates all necessary tables for the application
"""

import sqlite3
from database.db_connection import get_db_connection

def create_tables():
    """
    Create all necessary tables for the Neighborhood Complaint & Feedback System
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Complaints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                priority TEXT NOT NULL DEFAULT 'Medium',
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_to INTEGER,
                resolution_notes TEXT,
                resolved_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id)
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (complaint_id) REFERENCES complaints (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Status updates table for tracking complaint progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id INTEGER NOT NULL,
                updated_by INTEGER NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                update_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (complaint_id) REFERENCES complaints (id),
                FOREIGN KEY (updated_by) REFERENCES users (id)
            )
        ''')
        
        # Categories table for complaint categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('Roads & Infrastructure', 'Issues related to roads, bridges, and infrastructure'),
            ('Street Lighting', 'Problems with street lights and public lighting'),
            ('Water Supply', 'Water supply issues and quality concerns'),
            ('Sanitation & Waste', 'Garbage collection, sanitation, and waste management'),
            ('Public Safety', 'Safety concerns and security issues'),
            ('Parks & Recreation', 'Issues with parks, playgrounds, and recreational facilities'),
            ('Traffic & Transportation', 'Traffic management and transportation issues'),
            ('Environmental', 'Environmental concerns and pollution issues'),
            ('Utilities', 'Electricity, gas, and other utility problems'),
            ('Other', 'Other community issues not covered above')
        ]
        
        for category in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, description) 
                VALUES (?, ?)
            ''', category)
        
        # Create default admin user (password will be hashed by auth system)
        cursor.execute('''
            INSERT OR IGNORE INTO users (name, email, password, role, phone)
            VALUES ('Admin', 'admin@neighborhood.com', 'admin123', 'admin', '000-000-0000')
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_user_id ON complaints(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_complaint_id ON feedback(complaint_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status_updates_complaint_id ON status_updates(complaint_id)')
        
        conn.commit()
        print("Database tables created successfully!")
        
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        raise

def drop_tables():
    """
    Drop all tables (for testing/reset purposes)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        tables = ['status_updates', 'feedback', 'complaints', 'categories', 'users']
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        
        conn.commit()
        print("All tables dropped successfully!")
        
    except sqlite3.Error as e:
        print(f"Error dropping tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def reset_database():
    """
    Reset the database by dropping and recreating all tables
    """
    print("Resetting database...")
    drop_tables()
    create_tables()
    print("Database reset completed!")

if __name__ == "__main__":
    # Create tables when this script is run directly
    create_tables()
